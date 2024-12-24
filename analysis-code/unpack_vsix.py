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
        logging.exception(zf.filename, filename, 'KeyError')
        return b''

    except Exception as e:
        logging.exception(zf.filename, filename, e)
        return b''


def beautify_script(content, suffix):
    """ Beautifies a script with js-beautify (https://www.npmjs.com/package/js-beautify). """

    filehash = hashlib.md5(content.encode()).hexdigest()
    temp_file = "/tmp/%s_%s" % (filehash, suffix.replace("/", "_"))

    with open(temp_file, "w") as fh:
        fh.write(content)
    os.system("js-beautify -t -j -r %s > /dev/null" % temp_file)

    with open(temp_file, "r") as fh:
        content = fh.read()
    os.unlink(temp_file)

    return content

def pack_and_beautify(extension_zip, scripts):
    """ Appends and beautifies the content of scripts. """
    all_content = ""

    for script in scripts:
        if "jquery" in script.lower() or \
                not script.endswith(".js") or \
                script.startswith("https://") \
                or script.startswith("https://") or \
                "jq.min.js" in script.lower() or \
                "jq.js" in script.lower():
            continue
        
        content = read_from_zip(extension_zip, script)

        if len(content):
            pass
        else:
            continue
        all_content += "// New file: %s\n" % script
        content = content.replace(b"use strict", b"")
        all_content += beautify_script(content.decode("utf8", "ignore"), extension_zip.filename) + "\n"

    return all_content


def get_all_content_scripts(manifest, extension_zip):
    """ Extracts the content scripts. """

    content_scripts = manifest.get("main", str())

    if not isinstance(content_scripts, str):
        return
    
    if content_scripts.endswith(".js"):
        content_scripts = [content_scripts]
    else:
        content_scripts = [content_scripts + ".js"]


    return pack_and_beautify(extension_zip, content_scripts)




def unpack_extension(extension_vsix, dest):
    """
    Call this function to extract the manifest, scripts.

    :param extension_vsix: str, path of the packed extension to unpack;
    :param dest: str, path where to store the extracted extension components.
    """
    # if exsit return
    if os.path.exists(os.path.join(dest, "extension.js")):
        with open(os.path.join(dest, "extension.js"), "r") as fh:
            content_scripts = fh.read()

        if content_scripts == "": # empty file
            os.remove(os.path.join(dest, "extension.js"))
        else:
            return

    extension_id = extension_vsix.split("/")[-2]
    dest = os.path.join(dest, extension_id)

    try:
        extension_zip = ZipFile(extension_vsix)
        manifest = json.loads(extension_zip.read("extension/package.json"))
    except:
        return

    # Create the destination folder
    if not os.path.exists(dest):
        os.makedirs(dest)

    with open(os.path.join(dest, "package.json"), "w") as fh:
        fh.write(json.dumps(manifest, indent=2))

    if "main" not in manifest:
        return

    # Extract the content scripts
    content_scripts = get_all_content_scripts(manifest, extension_zip)

    if not content_scripts or content_scripts == "":
        return
    
    first_50_lines = content_scripts.split("\n")[:50]
    first_50_lines = "\n".join(first_50_lines)

    if ("require('./" in first_50_lines or 'require("./' in first_50_lines):
        # unzip the extension to the dest dir 
        unzip_dir = os.path.join(dest, "vsix")
        if not os.path.exists(unzip_dir):
            os.makedirs(unzip_dir)
        
        # unzip the extension to the dest dir
        os.system("unzip -o %s -d %s" % (extension_vsix, unzip_dir))
        extension_dir = os.path.join(unzip_dir, "extension")
        bundle_all_files(extension_dir+"/package.json", dest)
        # remove the unzip folder
        os.system("rm -rf %s" % unzip_dir)
        
    else:
        with open(os.path.join(dest, "extension.js"), "w") as fh:
            fh.write(content_scripts)

def bundle_all_files(package_json_p, extension_dir):
    with open(package_json_p, "r") as f:
        manifest = json.loads(f.read())
    main_entry = manifest.get("main", str())
    main_entry = main_entry.replace("./", "")

    output_bundle_p = extension_dir + "/extension.js"
    # get current dir
    current_dir = os.getcwd()
    os.chdir(os.path.dirname(package_json_p))
    deps_command = """node -p "Object.keys(require('./package.json').dependencies).concat(Object.keys(require('./package.json').devDependencies)).join(' -u ')" """
    deps = os.popen(deps_command).read().strip()
    

    browserify_command = f"npx browserify "+main_entry+" -u "+deps+" -u vscode -o "+output_bundle_p+" --no-builtin --no-commondir --no-builtins"
    process = subprocess.Popen(browserify_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    print(stderr.decode("utf-8"))
    
    if "Error: Can't walk dependency graph" in stderr.decode("utf-8"):
        # get fs/promises from Error: Can't walk dependency graph: Cannot find module 'fs/promises' from 
        get_dependency_module = stderr.decode("utf-8").split("Error: Can't walk dependency graph: Cannot find module '")[1].split("' from")[0]
        
        while get_dependency_module != "" and len(get_dependency_module) < 30:
            # install dependency module
            deps = deps + " -u " + get_dependency_module
            new_command = f"npx browserify "+main_entry+" -u "+deps+" -u vscode -o "+output_bundle_p+" --no-builtin --no-commondir --no-builtins"

            # run browserify again
            process = subprocess.Popen(new_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            if "Error: Can't walk dependency graph" in stderr.decode("utf-8"):
                get_dependency_module = stderr.decode("utf-8").split("Error: Can't walk dependency graph: Cannot find module '")[1].split("' from")[0]
            else:
                break

    os.chdir(current_dir)



def test_one_file():
    source_p = "PATH/TO/TabNine.tabnine-vscode-3.67.0.vsix" # the path of the extension to unpack
    dest_dir = "PATH/TO/UPPACK/tabnine" # the path to save the unpacked extension
    unpack_extension(source_p, dest_dir)

if __name__ == "__main__":
    test_one_file()