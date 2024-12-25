"""
    Unpacking a vscode extension and extracting the different components.
"""

import os
import json
import logging
import fnmatch
import hashlib
import argparse
from urllib.parse import urljoin
from zipfile import ZipFile
from bs4 import BeautifulSoup
from multiprocessing import Pool
import subprocess

def parse_arguments():
    parser = argparse.ArgumentParser(description='Unpack VSCode extension and extract components')
    
    parser.add_argument(
        '--vsix-path',
        required=True,
        help='Path to the .vsix file to unpack'
    )
    
    parser.add_argument(
        '--output-dir',
        required=True,
        help='Directory to store unpacked extension'
    )
    
    parser.add_argument(
        '--temp-dir',
        default='/tmp',
        help='Directory for temporary files (default: /tmp)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    return parser.parse_args()

def read_from_zip(zf, filename):
    """ Returns the bytes of the file filename in the archive zf. """
    filename = filename.lstrip("./").split("?")[0]
    filename = "extension/" + filename

    try:
        return zf.read(filename)
    except KeyError:
        # Now try lowercase
        mapping = {}
        for zi in zf.infolist():
            mapping[zi.filename.lower()] = zi.filename
        if filename.lower() in mapping:
            return zf.read(mapping[filename.lower()])
        logging.exception(f"KeyError in {zf.filename}, {filename}")
        return b''
    except Exception as e:
        logging.exception(f"Error in {zf.filename}, {filename}: {str(e)}")
        return b''

def beautify_script(content, suffix, temp_dir):
    """ Beautifies a script with js-beautify """
    filehash = hashlib.md5(content.encode()).hexdigest()
    temp_file = os.path.join(temp_dir, f"{filehash}_{suffix.replace('/', '_')}")

    with open(temp_file, "w") as fh:
        fh.write(content)
    os.system(f"js-beautify -t -j -r {temp_file} > /dev/null")

    with open(temp_file, "r") as fh:
        content = fh.read()
    os.unlink(temp_file)

    return content

def pack_and_beautify(extension_zip, scripts, temp_dir):
    """ Appends and beautifies the content of scripts. """
    all_content = ""

    for script in scripts:
        if ("jquery" in script.lower() or 
            not script.endswith(".js") or 
            script.startswith("https://") or 
            "jq.min.js" in script.lower() or 
            "jq.js" in script.lower()):
            continue
        
        content = read_from_zip(extension_zip, script)
        if not content:
            continue

        all_content += f"// New file: {script}\n"
        content = content.replace(b"use strict", b"")
        all_content += beautify_script(content.decode("utf8", "ignore"), 
                                     extension_zip.filename, 
                                     temp_dir) + "\n"

    return all_content

def get_all_content_scripts(manifest, extension_zip, temp_dir):
    """ Extracts the content scripts. """
    content_scripts = manifest.get("main", str())

    if not isinstance(content_scripts, str):
        return None
    
    if content_scripts.endswith(".js"):
        content_scripts = [content_scripts]
    else:
        content_scripts = [content_scripts + ".js"]

    return pack_and_beautify(extension_zip, content_scripts, temp_dir)

def bundle_all_files(package_json_p, extension_dir):
    """Bundle all JavaScript files using browserify"""
    with open(package_json_p, "r") as f:
        manifest = json.loads(f.read())
    
    main_entry = manifest.get("main", str()).replace("./", "")
    output_bundle_p = os.path.join(extension_dir, "extension.js")
    
    current_dir = os.getcwd()
    os.chdir(os.path.dirname(package_json_p))
    
    # Get dependencies
    deps_command = """node -p "Object.keys(require('./package.json').dependencies || {}).concat(Object.keys(require('./package.json').devDependencies || {})).join(' -u ')" """
    deps = os.popen(deps_command).read().strip()
    
    # Bundle with browserify
    browserify_command = f"npx browserify {main_entry} -u {deps} -u vscode -o {output_bundle_p} --no-builtin --no-commondir --no-builtins"
    process = subprocess.Popen(browserify_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    
    # Handle missing dependencies
    stderr_text = stderr.decode("utf-8")
    if "Error: Can't walk dependency graph" in stderr_text:
        while True:
            try:
                missing_module = stderr_text.split("Cannot find module '")[1].split("' from")[0]
                if len(missing_module) >= 30:
                    break
                    
                deps += f" -u {missing_module}"
                new_command = f"npx browserify {main_entry} -u {deps} -u vscode -o {output_bundle_p} --no-builtin --no-commondir --no-builtins"
                
                process = subprocess.Popen(new_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                stderr_text = stderr.decode("utf-8")
                
                if "Error: Can't walk dependency graph" not in stderr_text:
                    break
            except IndexError:
                break
    
    os.chdir(current_dir)

def unpack_extension(extension_vsix, dest, temp_dir):
    """
    Extract the manifest and scripts from a VSCode extension.
    
    Args:
        extension_vsix: Path to the .vsix file
        dest: Output directory for extracted files
        temp_dir: Directory for temporary files
    """
    # Extract extension ID from vsix path
    extension_id = os.path.basename(extension_vsix).replace('.vsix', '')
    dest_dir = os.path.join(dest, extension_id)

    # Check if already processed
    extension_js_path = os.path.join(dest_dir, "extension.js")
    if os.path.exists(extension_js_path):
        with open(extension_js_path, "r") as fh:
            if fh.read().strip():
                return
            os.remove(extension_js_path)

    try:
        extension_zip = ZipFile(extension_vsix)
        manifest = json.loads(extension_zip.read("extension/package.json"))
    except Exception as e:
        logging.error(f"Failed to read extension {extension_vsix}: {str(e)}")
        return

    # Create destination folder
    os.makedirs(dest_dir, exist_ok=True)

    # Save manifest
    with open(os.path.join(dest_dir, "package.json"), "w") as fh:
        json.dump(manifest, fh, indent=2)

    if "main" not in manifest:
        return

    # Extract content scripts
    content_scripts = get_all_content_scripts(manifest, extension_zip, temp_dir)
    if not content_scripts:
        return
    
    # Check for local requires in first 50 lines
    first_50_lines = "\n".join(content_scripts.split("\n")[:50])
    if any(pattern in first_50_lines for pattern in ["require('./", "require('."]):
        # Handle local requires with browserify
        unzip_dir = os.path.join(dest_dir, "vsix")
        os.makedirs(unzip_dir, exist_ok=True)
        
        os.system(f"unzip -o {extension_vsix} -d {unzip_dir}")
        extension_dir = os.path.join(unzip_dir, "extension")
        bundle_all_files(os.path.join(extension_dir, "package.json"), dest_dir)
        os.system(f"rm -rf {unzip_dir}")
    else:
        # Save content scripts directly
        with open(os.path.join(dest_dir, "extension.js"), "w") as fh:
            fh.write(content_scripts)

def main():
    args = parse_arguments()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, 
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Process extension
    try:
        unpack_extension(args.vsix_path, args.output_dir, args.temp_dir)
        logging.info(f"Successfully unpacked {args.vsix_path}")
    except Exception as e:
        logging.error(f"Failed to unpack {args.vsix_path}: {str(e)}")
        raise

if __name__ == "__main__":
    main()