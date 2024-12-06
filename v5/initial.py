import os
import subprocess
import json
import shutil
import sys
import time


DIRECTORY_JSON = "dir.json"
if os.path.exists(DIRECTORY_JSON):
        with open(DIRECTORY_JSON, 'r') as file:
            try:
                dir_data = json.load(file)
                ROOT = dir_data["root"]
                MEASUREMENT = dir_data["measurement"][0]["measurement_root"]
                DOWNLOAD = dir_data["download"][0]["download_root"]
                DOWNLOAD_JSON = dir_data["download"][2]["download_json"]
                MEASUREMENT_JSON = dir_data["measurement"][1]["measurement_json"]
                GRAPH = dir_data["graph"][0]["graph_root"]
                GRAPH_JSON = dir_data["graph"][1]["graph_json"]
                
            except json.JSONDecodeError:
                print("\dir.json existed but unable to load files.")
else:
    print("\dir.json is not existed.")

# List of scripts to execute within the 'DOWNLOAD' directory
scripts = ['auto_download.py', 'duplicate_check.py', 'organise_jobsite.py', 'data_deduplication.py']
measurement_scripts = ['brake_count.py', 'door_count.py', 'floor_count.py', 'mode_floor_count.py', 'mileage_floor.py']

REQUIRED_JSON_FILES = ['dir.json', 'DOWNLOAD/JSON/dir.json', 'MEASUREMENT/JSON/dir.json',
                       'DOWNLOAD/JSON/csv_path_link.json', 'DOWNLOAD/JSON/file_path.json', 
                       'DOWNLOAD/JSON/url.json', 'DOWNLOAD/JSON/x_path.json',
                       'GRAPH/JSON/dir.json'
                      ]

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def check_required_json_files(json_files):
    """
    Check if all required JSON files exist.
    If any file is missing, alert the user and exit the program.
    
    Parameters:
    - json_files (list): List of required JSON file paths.
    """
    missing_files = [file for file in json_files if not os.path.exists(file)]
    if missing_files:
        print("\nError: The following important JSON files are missing:")
        for file in missing_files:
            print(f"- {file}")
        print("\nPlease ensure all required JSON files are available before running the program.")
        sys.exit(1)
    else:
        print("All required JSON files are present.\n")
        time.sleep(2)
        clear_screen()

def copy_json_file_to_multiple_destinations(src_file, dest_dirs):
    print("\n\n")
    """
    Copy a single JSON file to multiple destination directories.
    
    Parameters:
    - src_file (str): Path to the source JSON file.
    - dest_dirs (list): List of destination directories.
    """
    for dest_dir in dest_dirs:
        # Ensure the destination directory exists
        os.makedirs(dest_dir, exist_ok=True)
        
        shutil.copy(src_file, dest_dir)
        print(f"Copied: {src_file} -> {dest_dir}")

def execute_script(script):
    script_path = os.path.join(os.getcwd(), script)
    if os.path.exists(script_path):
        print(f"\nRunning {script}...")
        try:
            # Use subprocess to run the script
            subprocess.run(['python', script_path], check=True)
            print(f"--- Finished executing {script} ---\n")
        except subprocess.CalledProcessError as e:
            print(f"Error while executing {script}: {e}")
    else:
        print(f"{script} not found. Skipping...")

def execute_measurement():      
    clear_screen()
    # Change to 'MEASUREMENT' directory
    os.chdir(os.path.join(ROOT, MEASUREMENT))
    current_measument_dir = os.getcwd()
    if not os.path.exists(current_measument_dir):
        print(f"\nError: The directory {current_measument_dir} does not exist.")
    else:
        print(f"\nCurrent directory: {current_measument_dir}")

    
    while True:
        print("\n\033[1mData Analyis\033[0m")
        print("Options:")
        print("0. All measurement tools")
        print("1. Brake Opening and Closing Count")
        print("2. Door Opening and Closing Count")
        print("3. Floor Count Travelled by a Lift")
        print("4. Mode of Floor Count")
        print("5. Floor Mileage Travelled by a Lift")
        print("r. Return to Main Menu")
        
        selector = input("\nSelect an option (0-5 or r): ").strip().lower()
        
        try:
            if selector == '0':
                for measurement_script in measurement_scripts:
                    execute_script(measurement_script)
            elif selector == '1':
                execute_script('brake_count.py')
            elif selector == '2':
                execute_script('door_count.py')
            elif selector == '3':
                execute_script('floor_count.py')
            elif selector == '4':
                execute_script('mode_floor_count.py')
            elif selector == '5':
                execute_script('mileage_floor.py')
            elif selector == 'r':
                print("Returning to Tiny File Manager Downloader...")
                time.sleep(2)
                break
            else:
                print("Invalid selection. Please choose a valid option.")

        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")

def convert_to_forward_slashes(path):
    """Converts all backslashes in a path to forward slashes."""
    return str(path).replace("\\", "/")

def graph(script):
    # Change to 'GRAPH' directory
    os.chdir(os.path.join(ROOT, GRAPH))
    current_graph_dir = os.path.join(os.getcwd(), script)
    print(f"Script Path: {current_graph_dir}")
    if os.path.exists(current_graph_dir):
        print(f"\nRunning {script} in a new terminal...")
        
        # Open a new terminal window to run the script
        if sys.platform == "win32":
            # Properly quote the path to handle spaces
            command = fr'python "{current_graph_dir}"'
            command = convert_to_forward_slashes(command)
            print(f"Executing: {command}")
            subprocess.run(
                f'start cmd /C {convert_to_forward_slashes(command)}',
                shell=True
            )
        elif sys.platform == "darwin":  # macOS
            subprocess.run(['open', '-a', 'Terminal', str(script_path)])
        else:  # Linux
            subprocess.run(['gnome-terminal', '--', 'python3', str(script_path)])
    else:
        print(f"{script} not found. Skipping...")

    time.sleep(2)
    clear_screen()
        

def main():
    # Save the original working directory
    original_dir = os.getcwd()

    # Read JSON from file
    with open(DIRECTORY_JSON, 'r') as file:
        json_data = json.load(file)

    # Update the 'root' value
    json_data['root'] = original_dir

    # Write the updated JSON back to the file
    with open(DIRECTORY_JSON, 'w') as file:
        json.dump(json_data, file, indent=4)

    source_file = 'dir.json'
    destination_directories = [DOWNLOAD_JSON, MEASUREMENT_JSON, GRAPH_JSON]

    copy_json_file_to_multiple_destinations(source_file, destination_directories)

    # Check if all required JSON files are present
    check_required_json_files(REQUIRED_JSON_FILES)

    while True:
        print("\n\033[1mTiny Manager CSV File Downloader\033[0m")

        original_dir = os.getcwd()

        download_dir = os.path.join(ROOT, DOWNLOAD)

        if not os.path.exists(download_dir):
            print(f"\nError: The directory {download_dir} does not exist.")
            break

        # Change to 'DOWNLOAD' directory
        os.chdir(download_dir)

        print("Options:")
        print("1. Run all scripts")
        print("2. Run auto_download.py only")
        print("3. Run duplicate_check.py only")
        print("4. Run organise_jobsite.py only")
        print("5. Run data_deduplication.py only")
        print("0. Run MEASUREMENT")
        print("g. Run GRAPH")
        print("e. Exit program")
        
        selector = input("\nSelect an option (1-5 or 0 or g or e): ").strip().lower()
        
        try:
            if selector == '1':
                for script in scripts:
                    execute_script(script)
                
                clear_screen()
            elif selector == '2':
                execute_script('auto_download.py')
                clear_screen()
            elif selector == '3':
                execute_script('duplicate_check.py')
                clear_screen()
            elif selector == '4':
                execute_script('organise_jobsite.py')
                clear_screen()
            elif selector == '5':
                execute_script('data_deduplication.py')
                clear_screen()
            elif selector == '0':
                execute_measurement()
            elif selector == 'g':
                print("\nOpening new terminal for GRAPH...")
                graph('graph_selector.py')
            elif selector == 'e':
                print("Program ended by user.")
                break
            else:
                print("Invalid selection. Please choose a valid option.")

        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")
        
        finally:
            # Revert to the original working directory
            os.chdir(ROOT)
            print(f"Reverted back to original directory: {original_dir}...")
            time.sleep(2)
            clear_screen()

if __name__ == "__main__":
    main()
