import pandas as pd
import os
import json

def deduplicate_csv(input_file, output_file, ignore_columns):
    """Deduplicate rows in a CSV file based on specified columns."""
    try:
        df = pd.read_csv(input_file)
        df.fillna(0, inplace=True)

        # Drop the columns that should be ignored for deduplication
        columns_to_check = df.columns.difference(ignore_columns)
        # print(f"Columns considered for deduplication: {columns_to_check.tolist()}")

        # Create a 'concatenate' column by combining all non-ignored columns
        df['concatenate'] = df[columns_to_check].astype(str).agg(' '.join, axis=1)

        # Check if the 'concatenate' column was created successfully
        column_name = 'concatenate'
        if column_name not in df.columns:
            print(f"Column '{column_name}' not found in the DataFrame.")
        else:
            print(f"Using column: {column_name}")

            # Identify duplicates by comparing each row with the previous row
            to_keep = [True] * len(df)
            deleted_rows = []

            for i in range(1, len(df)):
                if df[column_name].iloc[i] == df[column_name].iloc[i - 1]:
                    to_keep[i] = False
                    deleted_rows.append(i + 1)  # 1-based index

            # Report number of rows deleted
            print(f"Total rows to delete: {len(deleted_rows)}")
            # print(f"Rows deleted: {deleted_rows}")

            # Drop duplicates and save the cleaned DataFrame
            df_cleaned = df[to_keep].drop(columns=['concatenate']).reset_index(drop=True)
            df_cleaned.to_csv(output_file, index=False)
            print(f"Cleaned data saved to {output_file}")

    except Exception as e:
        print(f"Error processing file {input_file}: {e}")


def process_all_csv_files(input_dir, output_dir, ignore_columns):
    """Process all CSV files in a directory and its subdirectories."""
    os.makedirs(output_dir, exist_ok=True)

    # Use os.walk() to find all CSV files recursively
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith('.csv'):
                input_file_path = os.path.join(root, file)
                
                # Maintain the same folder structure in the output directory
                relative_path = os.path.relpath(root, input_dir)
                output_folder = os.path.join(output_dir, relative_path)
                os.makedirs(output_folder, exist_ok=True)
                
                output_file_path = os.path.join(output_folder, file)

                # Deduplicate the CSV file
                print(f"Processing file: {input_file_path}")
                deduplicate_csv(input_file_path, output_file_path, ignore_columns)


# Load paths from file_path.json
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILES_PATH = os.path.join(BASE_DIR, 'JSON', 'file_path.json')

if os.path.exists(FILES_PATH):
    with open(FILES_PATH, 'r') as file:
        try:
            file_path_data = json.load(file)
            input_directory = file_path_data["CSV"]["csv_files"]
            output_directory = file_path_data["CSV"]["data_deduplication"]
        except json.JSONDecodeError:
            print("\nfile_path.json exists but unable to load files.")
else:
    print("\nfile_path.json does not exist.")
    input_directory = None
    output_directory = None

# Specify columns to ignore during deduplication
ignore_columns = ['id', '_gts', 'created_at']

# Process all CSV files if directories are set correctly
if input_directory and output_directory and os.path.exists(input_directory):
    print(f"Starting deduplication in: {input_directory}")
    process_all_csv_files(input_directory, output_directory, ignore_columns)
else:
    print("Invalid or missing input/output directory.")
