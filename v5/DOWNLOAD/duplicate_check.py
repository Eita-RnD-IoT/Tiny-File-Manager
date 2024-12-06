import os
import hashlib
import json
import shutil

def hash_file(file_path):
    """Generate a hash for a file."""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read()
        while buf:
            hasher.update(buf)
            buf = f.read(4096)  # Read in chunks to handle large files
    return hasher.hexdigest()

def hash_folder(folder_path):
    """Generate a combined hash for all files in a folder."""
    folder_hasher = hashlib.md5()
    for root, _, files in os.walk(folder_path):
        for file in sorted(files):  # Sort files to maintain consistent hashing
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path):
                file_hash = hash_file(file_path)
                folder_hasher.update(file_hash.encode())
    return folder_hasher.hexdigest()

def find_and_remove_duplicates(directory):
    """Find and remove duplicate files and folders in a directory and its subdirectories."""
    file_hashes = {}     # To store hashes of individual files
    folder_hashes = {}   # To store hashes of entire folders

    # Step 1: Remove duplicate files within all subdirectories
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            
            # Check if it's a CSV file (optional filtering)
            if file.lower().endswith('.csv') and os.path.isfile(file_path):
                file_hash = hash_file(file_path)
                
                # Check if the file is already seen
                if file_hash in file_hashes:
                    print(f"Duplicate file found: {file_path}. Deleting...")
                    print(f"Hash: {file_hash}")
                    os.remove(file_path)
                else:
                    file_hashes[file_hash] = file_path

    # Step 2: Check for duplicate folders
    for root, dirs, _ in os.walk(directory, topdown=False):
        for folder in dirs:
            folder_path = os.path.join(root, folder)
            
            if os.path.isdir(folder_path):
                folder_hash = hash_folder(folder_path)
                
                if folder_hash in folder_hashes:
                    print(f"Duplicate folder found: {folder_path}. Deleting folder...")
                    shutil.rmtree(folder_path)
                else:
                    folder_hashes[folder_hash] = folder_path

# Specify the directory containing the CSV files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILES_PATH = os.path.join(BASE_DIR, 'JSON', 'file_path.json')

if os.path.exists(FILES_PATH):
    with open(FILES_PATH, 'r') as file:
        try:
            file_path_data = json.load(file)
            csv_directory = file_path_data["CSV"]["csv_files"]
        except json.JSONDecodeError:
            print("\nfile_path.json existed but unable to load files.")
else:
    print("\nfile_path.json does not exist.")
    csv_directory = None

# Find and remove duplicates
if csv_directory and os.path.exists(csv_directory):
    print(f"Searching for duplicates in: {csv_directory}")
    find_and_remove_duplicates(csv_directory)
else:
    print("CSV directory not found or invalid.")
