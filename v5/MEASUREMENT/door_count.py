import pandas as pd
import os
import json
from datetime import datetime

# Define base directories
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

# Function to count door cycles
def count_door_cycles(df):
    cycles = 0
    door_open = False
    for status in df['_lds']:
        if not door_open and status == 1:
            door_open = True
        elif door_open and status == 0:
            cycles += 1
            door_open = False
    return cycles

def analyze_lift(lift_folder, lift_name):
    """Analyze all CSV files in a given lift folder."""
    results = {
        'total_cycles': 0,
        'files': {}
    }

    # Loop through each CSV file in the lift folder
    for filename in os.listdir(lift_folder):
        if filename.endswith('.csv'):
            file_path = os.path.join(lift_folder, filename)
            
            # Check if the file is empty
            if os.path.getsize(file_path) == 0:
                print(f"Skipping empty file: {filename}")
                continue

            # Read the CSV file
            try:
                df = pd.read_csv(file_path)
                
                # Convert _gts to datetime
                df['_gts'] = pd.to_datetime(df['_gts'], errors='coerce')
                
                # Drop rows with invalid dates
                df = df.dropna(subset=['_gts'])
                
                # Sort by timestamp
                df = df.sort_values('_gts')
                
                # Count door cycles
                cycles = count_door_cycles(df)
                
                # Store cycles in the results under the file name
                results['files'][filename] = {
                    'cycles': cycles,
                    'date': df['_gts'].dt.date.iloc[0].isoformat() if not df.empty else None
                }
                
                # Update total cycles
                results['total_cycles'] += cycles

                print(f"Processed {filename}: {cycles} cycles")

            except pd.errors.EmptyDataError:
                print(f"Skipping empty file: {filename}")
            except Exception as e:
                print(f"Error reading {filename}: {e}")

    # Ensure the output directory exists
    if not os.path.exists(os.path.join(output_directory, "DOOR OPENING AND CLOSING CYCLE COUNT")):
        os.makedirs(os.path.join(output_directory, "DOOR OPENING AND CLOSING CYCLE COUNT"), exist_ok=True)

    # Export results to JSON
    output_file_path = os.path.join(output_directory, "DOOR OPENING AND CLOSING CYCLE COUNT", f'DC-{lift_name}.json')
    with open(output_file_path, 'w') as json_file:
        json.dump(results, json_file, indent=4)

    print(f"Door cycles count exported to {output_file_path}")

def process_all_lifts():
    """Process each lift folder under the main data directory."""
    # Navigate to the correct base folder
    os.chdir(csv_base_folder)

    current_csv_dir = os.getcwd()
    if not os.path.exists(current_csv_dir):
        print(f"\nError: The directory {current_csv_dir} does not exist.")
    else:
        print(f"\nCurrent directory: {current_csv_dir}")

    for lift_folder in os.listdir():
        full_path = os.path.join(current_csv_dir, lift_folder)
        print(f"Full Path: {full_path}")
        print(f"Lift Folder: {lift_folder}")
        if os.path.isdir(full_path):
            print(f"\nAnalyzing lift: {lift_folder}")
            analyze_lift(full_path, lift_folder)

# Run the analysis for all lifts
process_all_lifts()
