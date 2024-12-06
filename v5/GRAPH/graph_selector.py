import os
import subprocess
import json
import shutil
import sys
import time

DIRECTORY_JSON = "JSON/dir.json"
if os.path.exists(DIRECTORY_JSON):
        with open(DIRECTORY_JSON, 'r') as file:
            try:
                dir_data = json.load(file)
                ROOT = dir_data["root"]
                MEASUREMENT = dir_data["measurement"][0]["measurement_root"]
                DOWNLOAD = dir_data["download"][0]["download_root"]
                DOWNLOAD_JSON = dir_data["download"][2]["download_json"]
                MEASUREMENT_JSON = dir_data["measurement"][1]["measurement_json"]
                MEASUREMENT_DATA_ANALYSIS = dir_data["measurement"][2]["measurement_data_analysis"]
                GRAPH = dir_data["graph"][0]["graph_root"]
                GRAPH_JSON = dir_data["graph"][1]["graph_json"]
                
            except json.JSONDecodeError:
                print("\dir.json existed but unable to load files.")
else:
    print("JSON\dir.json is not existed.")
    time.sleep(2)  
    sys.exit(1)
    
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def check_required_data_analysis_folder(measurement_folder, tools):

    # Change directory to "MEASUREMENT/JSON/Data Analysis" to check he avaibility of files
    measurement_data_analysis_dir = os.path.join(ROOT, MEASUREMENT_DATA_ANALYSIS)
    os.chdir(measurement_data_analysis_dir)

    if os.path.exists(measurement_folder):
        print(f"{measurement_folder} is present.\n")
        return True
    
    print(f"\nError: The following important Folder: {measurement_folder} is missing.")
    print("\nPlease acquire all required Data Analysis folders before running this program.")
    print(f"Please run the -MEASUREMENT and select tool: {tools} for computing the result.")
    time.sleep(10)
    return False

def execute_script(script, measurement_folder, tools):
    # Check if the required "MEASUREMENT/JSON/Data Analysis" folder is present
    if check_required_data_analysis_folder(measurement_folder, tools):
        graph_dir = os.path.join(ROOT, GRAPH)
        os.chdir(graph_dir)
        script_path = os.path.join(graph_dir, script)
        if os.path.exists(script_path):
            print(f"\nRunning {script}...")
            try:
                # Use subprocess to run the script
                subprocess.run(['python', script_path], check=True)
                print(f"--- Finished executing {script} ---\n")
                print("\n--- RETURNING ---")
            except subprocess.CalledProcessError as e:
                print(f"Error while executing {script}: {e}")
        else:
            print(f"{script} not found. Skipping...")

def execute_measurement_script(script):
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
        print("1. Brake Opening and Closing Count")
        print("2. Door Opening and Closing Count")
        print("3. Floor Count Travelled by a Lift")
        print("4. Mode of Floor Count")
        print("5. Floor Mileage Travelled by a Lift")
        print("r. Return to Main Menu")
        
        selector = input("\nSelect an option (1-5 or r): ").strip().lower()
        
        try:
            if selector == '1':
                execute_measurement_script('brake_count.py')
            elif selector == '2':
                execute_measurement_script('door_count.py')
            elif selector == '3':
                execute_measurement_script('floor_count.py')
            elif selector == '4':
                execute_measurement_script('mode_floor_count.py')
            elif selector == '5':
                execute_measurement_script('mileage_floor.py')
            elif selector == 'r':
                print("Returning to Graph Selector...")
                time.sleep(2)
                break
            else:
                print("Invalid selection. Please choose a valid option.")

        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")
            

def main():

    while True:
        print("\n\033[1mGraph Selector\033[0m")

        graph_dir = os.path.join(ROOT, GRAPH)

        if not os.path.exists(graph_dir):
            print(f"\nError: The directory {graph_dir} does not exist.")
            break

        # Change to 'GRAPH' directory
        os.chdir(graph_dir)
        print("Options:")
        print("1. Graphs of Door Opening and Closing Cycles")
        print("2. Graphs of Brakes Opening and Closing Counts")
        print("3. Graphs of Floor Counts")
        print("4. Graphs of Floor Mileage")
        print("5. -(Graphs of Mode of Floor Count)")
        print("0. Export GRAPH")
        print("-MEASUREMENT")
        print("e. Exit program")
        
        print("\nSelect -MEASUREMENT if some requried folders are missing!!!!")
        selector = input("Select an option (1-5 or 0 or -MEASUREMENT or e): ").strip().lower()
        
        try:
            if selector == '1':  
                execute_script('graph_door_cycles.py', 'DOOR OPENING AND CLOSING CYCLE COUNT', 'door_count.py')
                time.sleep(5)
                clear_screen()
            elif selector == '2':
                execute_script('graph_brake_cycles.py', 'BRAKE OPENING AND CLOSING COUNT', 'brake_count.py')
                time.sleep(5)
                clear_screen()
            elif selector == '3':
                execute_script('graph_floor_count.py', 'FLOOR COUNT', 'floor_count.py')
                time.sleep(5)
                clear_screen()
            elif selector == '4':
                execute_script('graph_floor_mileage.py', 'MILEAGE', 'mileage_floor.py')
                time.sleep(5)
                clear_screen()
            elif selector == '5':
                execute_script('graph_floor_mode.py', 'MODE FLOOR COUNT', 'mode_floor_count.py')
                time.sleep(5)
                clear_screen()
            elif selector == '0':
                print("\n--- CURRENT NOT AVAILABLE ---")
                time.sleep(5)
                clear_screen()
            elif selector == '-measurement':
                execute_measurement()
                clear_screen()
            elif selector == 'e':
                print("Program ended by user.")
                break
            else:
                print("Invalid selection. Please choose a valid option.")

        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")
        
        finally:
            # Revert to the original working directory
            os.chdir(graph_dir)
            original_dir = os.getcwd()
            print(f"Reverted back to original directory: {original_dir}")

if __name__ == "__main__":
    main()
