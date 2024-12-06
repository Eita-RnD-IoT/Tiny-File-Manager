import os
import shutil
import json

jobsite = []

# Define the directory containing your files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILES_PATH = os.path.join(BASE_DIR, 'JSON', 'file_path.json')
if os.path.exists(FILES_PATH):
        with open(FILES_PATH, 'r') as file:
            try:
                file_path_data = json.load(file)
                source_dir = file_path_data["CSV"]["csv_files"]
                destination_dir = file_path_data["CSV"]["csv_files"]
                jobsite_json_path = file_path_data["JSON"]["jobsite"]
            except json.JSONDecodeError:
                print("\nfile_path.json existed but unable to load files.")
else:
    print("\nfile_path.json is not existed.")

# source_dir = 'C:\Data\Documents\Arduino\Eita Stock Inventory\Excel\Auto Download\\auto_download8\output_csv_files1'  # Change this to your source directory
# destination_dir = 'C:\Data\Documents\Arduino\Eita Stock Inventory\Excel\Auto Download\\auto_download8\output_csv_files1\Jobsite'  # Change this to your destination directory

# Create the destination directory if it doesn't exist
os.makedirs(destination_dir, exist_ok=True)

# Loop through all files in the source directory
for filename in os.listdir(source_dir):
    if filename.endswith('.csv'):
        # Split the filename at the hyphens
        parts = filename.split('-')
        
        # Ensure there are enough parts to process
        if len(parts) > 2:
            # Extract the important part (the second part)
            important_part = parts[1].strip()

            # Format the jobsite name as a dictionary object and append to the list
            jobsite_name = {"jobsite": important_part}
            jobsite.append(jobsite_name)            
            
            # Create a new directory for this important part in the destination directory
            important_dir = os.path.join(destination_dir, important_part)
            os.makedirs(important_dir, exist_ok=True)
            
            # Move the file to the corresponding directory
            source_file_path = os.path.join(source_dir, filename)
            destination_file_path = os.path.join(important_dir, filename)
            shutil.move(source_file_path, destination_file_path)

with open(jobsite_json_path, 'w') as file:
    json.dump(jobsite, file, indent=4)

print("Files organized successfully.")
