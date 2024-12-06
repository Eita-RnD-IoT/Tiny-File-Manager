import os
import json
import pandas as pd
from collections import Counter
import subprocess

PYTHON_FLOOR_COUNT = "floor_count.py"

def get_json_file_path():
    # Define base directories
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DIR_PATH = os.path.join(BASE_DIR, 'JSON', 'dir.json')
    if os.path.exists(DIR_PATH):
            with open(DIR_PATH, 'r') as file:
                try:
                    dir_path_data = json.load(file)
                    root = dir_path_data["root"]
                    floor_count_json_path = dir_path_data["measurement"][2]["measurement_data_analysis"]
                except json.JSONDecodeError:
                    print("\ndir.json existed but unable to load files.")
    else:
        print("\nfile_path.json is not existed.")

    output_mode =  os.path.join(root, floor_count_json_path)
    floor_count_json_dir =  os.path.join(root, floor_count_json_path, "FLOOR COUNT")

    if not os.path.exists(floor_count_json_dir):
        print('\nUnable to access folder "Data Analysis/FLOOR COUNT"')
        print("To utilise this script, floor_count.py shall be executed before this script...")
        if os.path.exists(PYTHON_FLOOR_COUNT):
            print(f"\nRunning {PYTHON_FLOOR_COUNT}...")
            try:
                # Use subprocess to run the script
                subprocess.run(['python', PYTHON_FLOOR_COUNT], check=True)
                print(f"--- Finished executing {PYTHON_FLOOR_COUNT} ---\n")
            except subprocess.CalledProcessError as e:
                print(f"Error while executing {PYTHON_FLOOR_COUNT}: {e}")
        else:
            print(f"{PYTHON_FLOOR_COUNT} not found. Skipping...")
            return

    process_all_lifts(floor_count_json_dir, output_mode)

def process_all_lifts(floor_count_json_dir, output_mode):
    print(f"\nProcessing JSON files in: {floor_count_json_dir}")
    available_files = os.listdir(floor_count_json_dir)
    print(f"Available files: {available_files}")

    for fc_json in available_files:
        if fc_json.endswith('.json'):
            try:
                # Generate full path for the JSON file
                file_path = os.path.join(floor_count_json_dir, fc_json)
                print(f"Processing file: {file_path}")

                # Read and process the JSON file
                data = read_json_file(file_path)
                total_mode, file_modes = calculate_modes(data)

                # Extract lift name from the filename
                parts = fc_json.split('-')
                if len(parts) > 1:
                    lift_name = parts[1].strip()
                    write_results_to_json(total_mode, file_modes, output_mode, lift_name)
            except FileNotFoundError:
                print(f"File not found: {file_path}. Skipping...")
            except ValueError as ve:
                print(f"ValueError for file {fc_json}: {ve}")
            except Exception as e:
                print(f"An error occurred with file {fc_json}: {str(e)}")

def read_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)
    
def calculate_modes(data):
    total_counts = Counter()
    file_modes = {}

    for file_name, floor_counts in data["files"].items():
        if floor_counts:
            # Filter out floor 0
            filtered_counts = {floor: count for floor, count in floor_counts.items() if int(floor) != 0}
            if filtered_counts:
                df = pd.DataFrame.from_dict(filtered_counts, orient='index', columns=['count'])
                file_modes[file_name] = int(float(df['count'].idxmax()))
                total_counts.update(filtered_counts)
            else:
                print(f"Warning: No non-zero floor counts found for file {file_name}.")
        else:
            print(f"Warning: No floor counts found for file {file_name}.")

    if not total_counts:
        print("Warning: No non-zero counts available to calculate the total mode.")
        total_mode = None
    else:
        total_mode = int(float(pd.Series(total_counts).idxmax()))

    return total_mode, file_modes



def write_results_to_json(total_mode, file_modes, output_mode, lift_name):
    results = {
        "total_mode": total_mode,
        "file_modes": file_modes
    }

    # Create the output directory if it doesn't exist
    os.makedirs(os.path.join(output_mode,"MODE FLOOR COUNT"), exist_ok=True)
    
    # Export results to JSON file in the output directory
    output_file_path = os.path.join(output_mode, "MODE FLOOR COUNT", f'MFC-{lift_name}.json')
    with open(output_file_path, 'w') as json_file:
        json.dump(results, json_file, indent=4)

    print(f"Counts and cycles exported to {output_file_path}")

if __name__ == "__main__":
    get_json_file_path()