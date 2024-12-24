import os
import zipfile
import shutil
from concurrent.futures import ProcessPoolExecutor, as_completed

def unpack_vsix(vsix_file, output_dir):
    extension_id = os.path.splitext(os.path.basename(vsix_file))[0]
    extension_dir = os.path.join(output_dir, extension_id)
    
    # Create extension directory
    os.makedirs(extension_dir, exist_ok=True)
    
    try:
        with zipfile.ZipFile(vsix_file, 'r') as zip_ref:
            # Extract extension.vsixmanifest
            try:
                zip_ref.extract('extension.vsixmanifest', extension_dir)
            except KeyError:
                print(f"Warning: extension.vsixmanifest not found in {vsix_file}")
            
            # Extract extension folder
            for file in zip_ref.namelist():
                if file.startswith('extension/'):
                    zip_ref.extract(file, extension_dir)
        
        # Move contents of 'extension' folder to root of extension_dir
        extension_folder = os.path.join(extension_dir, 'extension')
        if os.path.exists(extension_folder):
            for item in os.listdir(extension_folder):
                s = os.path.join(extension_folder, item)
                d = os.path.join(extension_dir, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)
            shutil.rmtree(extension_folder)
        
        print(f"Unpacked: {extension_id}")
    except Exception as e:
        print(f"Error processing {vsix_file}: {str(e)}")

def main():
    vsix_dir = 'data/vsix'
    output_dir = 'data/code'
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Get list of VSIX files
    vsix_files = [os.path.join(vsix_dir, f) for f in os.listdir(vsix_dir) if f.endswith('.vsix')]
    
    # Use ProcessPoolExecutor for parallel processing
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(unpack_vsix, vsix_file, output_dir) for vsix_file in vsix_files]
        
        for future in as_completed(futures):
            future.result()  # This will raise any exceptions that occurred during execution

if __name__ == "__main__":
    main()