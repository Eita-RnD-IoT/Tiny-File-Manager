import os
import pandas as pd
import json
from collections import OrderedDict

# Limitation: Data acquired without identify the door opening and closing
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIR_PATH = os.path.join(BASE_DIR, 'JSON', 'dir.json')
if os.path.exists(DIR_PATH):
        with open(DIR_PATH, 'r') as file:
            try:
                dir_path_data = json.load(file)
                root = dir_path_data["root"]
                csv_dir = dir_path_data["download"][3]["download_deduplicate"]
                out_json_dir = dir_path_data["measurement"][2]["measurement_data_analysis"]
            except json.JSONDecodeError:
                print("\ndir.json existed but unable to load files.")
else:
    print("\nfile_path.json is not existed.")

csv_base_folder = os.path.join(root, csv_dir)
output_directory = os.path.join(root, out_json_dir)

def process_all_lifts():
    """Process each lift folder under the main data directory."""
    if not os.path.exists(csv_base_folder):
        print(f"\nError: The directory {csv_base_folder} does not exist.")
        return

    print(f"\nProcessing all lifts in: {csv_base_folder}")

    for lift_folder in os.listdir(csv_base_folder):
        full_path = os.path.join(csv_base_folder, lift_folder)
        if os.path.isdir(full_path):
            print(f"\nAnalyzing lift: {lift_folder}")
            process_lift_data(full_path, lift_folder)

def process_lift_data(lift_folder, lift_name):
    floor_counts = {}
    files_output = {}

    for filename in os.listdir(lift_folder):
        if filename.endswith('.csv'):
            file_path = os.path.join(lift_folder, filename)
            data = pd.read_csv(file_path)
            
            file_floor_counts = {}
            prev_mb1s = prev_mb2s = 1  # Assume lift starts in moving state
            
            for _, row in data.iterrows():
                current_mb1s = row['_mb1s']
                current_mb2s = row['_mb2s']
                current_floor = row['_lfls']
                
                # Check if lift has stopped (both mb1s and mb2s toggle from 1 to 0)
                if prev_mb1s == 1 and prev_mb2s == 1 and current_mb1s == 0 and current_mb2s == 0:
                    floor_counts[current_floor] = floor_counts.get(current_floor, 0) + 1
                    file_floor_counts[current_floor] = file_floor_counts.get(current_floor, 0) + 1
                
                prev_mb1s, prev_mb2s = current_mb1s, current_mb2s
            
            files_output[filename] = file_floor_counts

    return floor_counts, files_output, lift_name

def sort_floor_numbers(data):
    # Sort total floor numbers
    total_floors = data["total of floor number travelled by the lift"]
    sorted_total = OrderedDict(sorted(total_floors.items(), key=lambda x: int(x[0])))
    data["total of floor number travelled by the lift"] = sorted_total

    # Sort floor numbers for each file
    for file_name, file_data in data["files"].items():
        sorted_file_data = OrderedDict(sorted(file_data.items(), key=lambda x: int(x[0])))
        data["files"][file_name] = sorted_file_data

    return data

def output_to_json(floor_counts, files_output, lift_name):
    output_data = {
        "total of floor number travelled by the lift": floor_counts,
        "files": files_output
    }

    output_data = sort_floor_numbers(output_data)

    os.makedirs(os.path.join(output_directory,"FLOOR COUNT"), exist_ok=True)

    # Export results to JSON file in the output directory
    output_file_path = os.path.join(output_directory,"FLOOR COUNT", f'FC-{lift_name}.json')
    with open(output_file_path, 'w') as json_file:
        json.dump(output_data, json_file, indent=4)

    print(f"Counts and cycles exported to {output_file_path}")

def main():
    # Verify that `csv_base_folder` exists
    if not os.path.exists(csv_base_folder):
        print(f"\nError: The directory {csv_base_folder} does not exist.")
        return

    print(f"\nProcessing all lifts in: {csv_base_folder}")
    
    # Process each lift folder in the base folder
    for lift_folder in os.listdir(csv_base_folder):
        full_path = os.path.join(csv_base_folder, lift_folder)
        if os.path.isdir(full_path):  # Only process directories
            try:
                print(f"\nAnalyzing lift: {lift_folder}")
                floor_counts, files_output, lift_name = process_lift_data(full_path, lift_folder)
                output_to_json(floor_counts, files_output, lift_name)
            except FileNotFoundError:
                print(f"Error: The specified folder path '{full_path}' does not exist.")
            except Exception as e:
                print(f"An error occurred while processing {lift_folder}: {str(e)}")


if __name__ == "__main__":
    main()