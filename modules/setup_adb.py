import os
import zipfile
import requests
import shutil

def setup_adb():
    url = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
    dest_zip = "platform-tools.zip"
    extract_path = "adb_tools"
    
    if os.path.exists(os.path.join(extract_path, "platform-tools", "adb.exe")):
        print("ADB already installed.")
        return

    print(f"Downloading ADB from {url}...")
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(dest_zip, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    f.write(chunk)
        print("Download complete.")
        
        print("Extracting...")
        with zipfile.ZipFile(dest_zip, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
            
        print("Done. ADB is at: ./adb_tools/platform-tools/adb.exe")
        
    except Exception as e:
        print(f"Setup Failed: {e}")
        # Cleanup bad zip
        if os.path.exists(dest_zip):
            os.remove(dest_zip)

if __name__ == "__main__":
    setup_adb()
