import os
import pandas as pd
import json

def get_folder_path():
    # Global variable for folder path
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
    return csv_base_folder, output_directory


def calculate_mileage(df):
    mileage = 0
    origin = None
    prev_mb1s = prev_mb2s = 0

    for _, row in df.iterrows():
        current_floor = int(row['_lfls'])
        current_mb1s = int(row['_mb1s'])
        current_mb2s = int(row['_mb2s'])

        if origin is None:
            origin = current_floor

        if prev_mb1s == 0 and prev_mb2s == 0 and current_mb1s == 1 and current_mb2s == 1:
            # Lift starts moving
            origin = current_floor
        elif prev_mb1s == 1 and prev_mb2s == 1 and current_mb1s == 0 and current_mb2s == 0:
            # Lift stops
            mileage += abs(current_floor - origin)
            origin = current_floor

        prev_mb1s, prev_mb2s = current_mb1s, current_mb2s

    return mileage

def process_csv_files(csv_base_folder):
    total_mileage = 0
    file_mileages = {}

    for filename in os.listdir(csv_base_folder):
        if filename.endswith('.csv'):
            file_path = os.path.join(csv_base_folder, filename)

            # Extract lift name from the filename
            parts = filename.split('-')
            if len(parts) > 1:
                lift_name = parts[1].strip()

            df = pd.read_csv(file_path)
            mileage = calculate_mileage(df)
            total_mileage += mileage
            file_mileages[filename] = mileage

    return total_mileage, file_mileages, lift_name

def output_to_json(total_mileage, file_mileages, output_directory, lift_name):
    result = {
        "total_mileage": total_mileage,
        "file_mileages": file_mileages
    }

    os.makedirs(os.path.join(output_directory,"MILEAGE"), exist_ok=True)

    output_file = os.path.join(output_directory,"MILEAGE", f"M-{lift_name}.json")
    with open(output_file, 'w') as jsonfile:
        json.dump(result, jsonfile, indent=2)

    print(f"Results have been written to {output_file}")

def main():
    csv_base_folder, output_directory = get_folder_path()

    print(f"\nProcessing all lifts in: {csv_base_folder}")

    for item in os.listdir(csv_base_folder):
        item_path = os.path.join(csv_base_folder, item)

        if os.path.isdir(item_path):
            # Process directories containing CSV files
            print(f"Processing folder: {item}")
            try:
                total_mileage, file_mileages, lift_name = process_csv_files(item_path)
                output_to_json(total_mileage, file_mileages, output_directory, lift_name)
            except Exception as e:
                print(f"An error occurred in folder '{item}': {e}")
        elif item.endswith('.csv'):
            # Process individual CSV files in the base folder
            print(f"Processing file: {item}")
            try:
                df = pd.read_csv(item_path)
                mileage = calculate_mileage(df)
                lift_name = os.path.splitext(item)[0]  # Use filename (without extension) as lift name
                file_mileages = {item: mileage}
                total_mileage = mileage
                output_to_json(total_mileage, file_mileages, output_directory, lift_name)
            except Exception as e:
                print(f"An error occurred with file '{item}': {e}")
        else:
            print(f"Skipping unsupported item: {item}")

if __name__ == "__main__":
    main()
