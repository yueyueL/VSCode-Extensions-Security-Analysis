import os
import json
import multiprocessing
import urllib.parse

def download_vsix(extension):
    extension_id = extension.get('extensionId')
    versions = extension.get('versions', [])
    
    if versions:
        latest_version = versions[0]
        files = latest_version.get('files', [])
        
        for file in files:
            if file.get('assetType') == 'Microsoft.VisualStudio.Services.VSIXPackage':
                download_url = file.get('source')
                if download_url:
                    # Ensure the filename is URL-safe
                    safe_extension_id = urllib.parse.quote(extension_id, safe='')
                    output_file = f"data/vsix/{safe_extension_id}.vsix"
                    
                    # Create the data/vsix directory if it doesn't exist
                    os.makedirs('data/vsix', exist_ok=True)
                    
                    # Use wget to download the file
                    command = f'wget -q -O "{output_file}" "{download_url}"'
                    os.system(command)
                    print(f"Downloaded: {extension_id}")
                    return
    
    print(f"Failed to download: {extension_id}")

def main():
    # Load the JSON file
    with open('data/vscode_extension_original.json', 'r') as f:
        extensions = json.load(f)
    
    # Create a pool of workers
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    
    # Use the pool to download VSIXs in parallel
    pool.map(download_vsix, extensions)
    
    # Close the pool and wait for all processes to finish
    pool.close()
    pool.join()

if __name__ == "__main__":
    main()
