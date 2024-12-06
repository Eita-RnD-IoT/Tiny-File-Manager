import pandas as pd
import os
import json

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

def analyze_lift(lift_folder, lift_name):
    """Analyze all CSV files in a given lift folder."""
    results = {
        'total_counts': {'_mb1s': {'0': 0, '1': 0}, '_mb2s': {'0': 0, '1': 0}, 'cycles': 0},
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
            
            try:
                df = pd.read_csv(file_path)
                
                # Initialize a boolean mask for rows to keep
                to_keep = [True] * len(df)
                
                # Track deletions and cycles
                deleted_rows = []
                cycles = 0
                prev_state = None

                # Compare each row with the previous row to mark continuous duplicates and count cycles
                for i in range(len(df)):
                    current_state = (df['_mb1s'].iloc[i], df['_mb2s'].iloc[i])
                    
                    if i > 0:
                        if current_state == prev_state:
                            to_keep[i] = False
                            deleted_rows.append(i + 1)  # 1-based index for progress display
                        elif prev_state == (1, 1) and current_state == (0, 0):
                            cycles += 1
                    
                    prev_state = current_state

                # Drop the marked rows
                df_cleaned = df[to_keep].reset_index(drop=True)
            
                # Count occurrences of 0 and 1 for each variable
                counts_A = df_cleaned['_mb1s'].value_counts().to_dict()
                counts_B = df_cleaned['_mb2s'].value_counts().to_dict()
                
                # Store counts and cycles in the results under the file name
                results['files'][filename] = {
                    '_mb1s': {'0': counts_A.get(0, 0), '1': counts_A.get(1, 0)},
                    '_mb2s': {'0': counts_B.get(0, 0), '1': counts_B.get(1, 0)},
                    'cycles': cycles
                }
                
                # Update total counts and cycles
                results['total_counts']['_mb1s']['0'] += counts_A.get(0, 0)
                results['total_counts']['_mb1s']['1'] += counts_A.get(1, 0)
                results['total_counts']['_mb2s']['0'] += counts_B.get(0, 0)
                results['total_counts']['_mb2s']['1'] += counts_B.get(1, 0)
                results['total_counts']['cycles'] += cycles

            except pd.errors.EmptyDataError:
                print(f"Skipping empty file: {filename}")
            except Exception as e:
                print(f"Error reading {filename}: {e}")

    # Create the output directory if it doesn't exist
    os.makedirs(os.path.join(output_directory,"BRAKE OPENING AND CLOSING COUNT"), exist_ok=True)

    # Export results to JSON file in the output directory
    output_file_path = os.path.join(output_directory, "BRAKE OPENING AND CLOSING COUNT", f'BOCC-{lift_name}.json')
    with open(output_file_path, 'w') as json_file:
        json.dump(results, json_file, indent=4)

    print(f"Counts and cycles exported to {output_file_path}")

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
            analyze_lift(full_path, lift_folder)

# Run the analysis for all lifts
process_all_lifts()
