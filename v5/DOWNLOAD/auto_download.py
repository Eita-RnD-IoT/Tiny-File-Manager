from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import json
import getpass
import os
import requests
from datetime import datetime
import zipfile
import re
from urllib.parse import urlparse, parse_qs
from pathlib import Path
import shutil

# Ensure paths are absolute
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILES_PATH = os.path.join(BASE_DIR, 'JSON', 'file_path.json')
if os.path.exists(FILES_PATH):
        with open(FILES_PATH, 'r') as file:
            try:
                file_path_data = json.load(file)
                credentials_file_json_path = file_path_data["JSON"]["credentials"]
                csv_path_link_json_path = file_path_data["JSON"]["csv_download_link"]
                url_json_path = file_path_data["JSON"]["url"]
                download_csv_json_path = file_path_data["CSV"]["csv_files"]
                xpath_json_path = file_path_data["JSON"]["x_path"]
                zip_csv_json_path = file_path_data["CSV"]["zip_csv"]
            except json.JSONDecodeError:
                print("\nfile_path.json existed but unable to load files.")
else:
    print("\nfile_path.json is not existed.")

credentials_file = os.path.join(BASE_DIR, credentials_file_json_path)
csv_path_link = os.path.join(BASE_DIR, csv_path_link_json_path)
tiny_file_manager_url = os.path.join(BASE_DIR, url_json_path)

print(f"Credential file path: {credentials_file}")
print(f"CSV Link file path: {csv_path_link}")

download_dir = os.path.join(BASE_DIR, download_csv_json_path)
os.makedirs(download_dir, exist_ok=True)

print(f"\nDownloaded CSV path: {download_dir}")

if os.path.exists(tiny_file_manager_url):
        with open(tiny_file_manager_url, 'r') as file:
            try:
                url = json.load(file)
                TINY_FILE_MANAGER = url["tiny_file_manager"]
            except json.JSONDecodeError:
                print("\nurl.json existed but unable to load files.")
else:
    print("\nurl.json is not existed.")

print(f"\nAccessing URL: {TINY_FILE_MANAGER}")

if os.path.exists(xpath_json_path):
        with open(xpath_json_path, 'r') as file:
            try:
                xpath = json.load(file)
                username_xpath = xpath["download"]["username_xpath"]
                password_xpath = xpath["download"]["password_xpath"]
                signin_button_xpath = xpath["download"]["signin_button_xpath"]
                token_xpath = xpath["download"]["token_xpath"]
                csv_files_xpath = xpath["download"]["csv_files_xpath"]

                print("\nLoaded X Path successfully")
            except json.JSONDecodeError:
                print("\nurl.json existed but unable to load files.")
else:
    print("\nurl.json is not existed.")

# Define the download path
def get_download_path():
    zip_download_dir = os.path.join(BASE_DIR, zip_csv_json_path)
    os.makedirs(zip_download_dir, exist_ok=True)
    return zip_download_dir

# Load credentials from the file if it exists
def load_credentials():
    if os.path.exists(credentials_file):
        with open(credentials_file, 'r') as file:
            try:
                credentials = json.load(file)
            except json.JSONDecodeError:
                credentials = {}
    else:
        credentials = {}
    return credentials

# Save credentials to the file
def save_credentials(username, password):
    with open(credentials_file, 'w') as file:
        json.dump({"username": username, "password": password}, file)

# Prompt the user for credentials
def prompt_for_credentials():
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")
    save_credentials(username, password)
    return username, password

# Function to display and amend credentials
def display_and_amend_credentials(credentials):
    print("\nCurrent Credentials:")
    print(f"Username: {credentials.get('username')}")
    # print(f"Password: {'*' * len(credentials.get('password', ''))}")
    print(f"Password: {credentials.get('password', '')}")

    amend = input("\nDo you want to amend these credentials? (y/n): ").strip().lower()
    if amend == 'y':
        username = input("Enter new username (leave blank to keep current): ") or credentials.get('username')
        password = getpass.getpass("Enter new password (leave blank to keep current): ") or credentials.get('password')
        save_credentials(username, password)
        return username, password
    else:
        return credentials.get('username'), credentials.get('password')

# Function to handle the login using Selenium and extract the token
def login_with_selenium(username, password, browser):
    try:
        browser.get(TINY_FILE_MANAGER)

        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, username_xpath))
        ).send_keys(username)
        
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, password_xpath))
        ).send_keys(password)

        # Wait for the page to load and look for the token
        token = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, token_xpath))
        ).get_attribute('value')  # Adjust the attribute as needed
        
        WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, signin_button_xpath))
        ).click()

        logging.info("Login successful")
        return token  # Return the token after a successful login
    except Exception as e:
        logging.error(f"Login failed: {e}")
        return None

# Function to get CSV file links from the file management page
def get_csv_files(browser):
    csv_files = []
    try:
        rows = browser.find_elements(By.XPATH, csv_files_xpath)
        for row in rows:
            try:
                # Locate the <i> element and extract the link
                i_element = row.find_element(By.XPATH, './td[6]/a[2]')
                link = i_element.get_attribute('href')
                if link and link.endswith('.csv'):
                    csv_files.append(link)
            except Exception as e:
                logging.warning(f"Error finding CSV link in row: {e}")
    except Exception as e:
        logging.error(f"Error retrieving CSV files: {e}")
    return csv_files

# Function to save CSV links and token to a JSON file
def save_csv_links_to_json(csv_files, token):
    data = {
        "token": token,
        "csv_files": csv_files
    }
    with open(csv_path_link, 'w') as file:
        json.dump(data, file, indent=4)

# Function to extract the filename from a URL
def extract_filename_from_url(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    if 'dl' in query_params:
        filename = query_params['dl'][0]
        return filename
    else:
        return os.path.basename(parsed_url.path)

def get_session_cookies(browser):
    cookies = browser.get_cookies()
    session_cookies = {cookie['name']: cookie['value'] for cookie in cookies}
    return session_cookies

# Preload all filenames (including those in subdirectories)
existing_files = set()
for root, _, files in os.walk(download_dir):
    for file in files:
        existing_files.add(file)  # Add only the filenames (not full paths)

def download_csv_files(csv_files, download_dir, token, browser, username, password, session_cookies):
    for url in csv_files:
        try:
            filename = extract_filename_from_url(url)
            filepath = os.path.join(download_dir, filename)

            # Check if the file is in the preloaded set
            if filename in existing_files:
                logging.info(f"{filename} already exists. Skipping download.")
                continue

            # Attempt download with session cookies
            response = requests.post(url, data={"token": token}, cookies=session_cookies)

            # If unauthorized, re-login and retry
            if response.status_code == 401:
                logging.warning("Session expired, re-logging in")
                token = login_with_selenium(username, password, browser)
                session_cookies = get_session_cookies(browser)
                response = requests.post(url, data={"token": token}, cookies=session_cookies)

            if response.status_code == 200:
                with open(filepath, 'wb') as file:
                    file.write(response.content)
                logging.info(f"Downloaded {filename}")
            else:
                logging.error(f"Failed to download {url}: HTTP {response.status_code}")

        except Exception as e:
            logging.error(f"Error downloading {url}: {e}")

    print("\nOrganising the file.....")

    # Loop through all files in the source directory
    for filename in os.listdir(download_dir):
        if filename.endswith('.csv'):
            # Split the filename at the hyphens
            parts = filename.split('-')
            
            # Ensure there are enough parts to process
            if len(parts) > 2:
                # Extract the important part (the second part)
                important_part = parts[1].strip()      
                
                # Create a new directory for this important part in the destination directory
                important_dir = os.path.join(download_dir, important_part)
                os.makedirs(important_dir, exist_ok=True)
                
                # Move the file to the corresponding directory
                source_file_path = os.path.join(download_dir, filename)
                destination_file_path = os.path.join(important_dir, filename)
                shutil.move(source_file_path, destination_file_path)

# Function to compress files into a ZIP archive
def compress_to_zip(directory, output_path):
    zip_filename = f"csv_files_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    zip_filepath = os.path.join(output_path, zip_filename)
    with zipfile.ZipFile(zip_filepath, 'w') as zipf:
        for root, dirs, files in os.walk(directory):
            for file in files:
                zipf.write(os.path.join(root, file), file)
    logging.info(f"Files compressed into {zip_filepath}")

def main():
    credentials = load_credentials()

    if not credentials.get('username') or not credentials.get('password'):
        print("No credentials found or credentials are incomplete.")
        username, password = prompt_for_credentials()
    else:
        username, password = display_and_amend_credentials(credentials)

    chrome_options = Options()
    chrome_options.add_argument('--ignore-ssl-errors=yes')
    chrome_options.add_argument('--ignore-certificate-errors')
    # chrome_options.add_argument("-incognito")
    chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])

    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service, options=chrome_options)

    token = None
    while not token:
        token = login_with_selenium(username, password, browser)
        if not token:
            username, password = prompt_for_credentials()

    csv_files = get_csv_files(browser)
    save_csv_links_to_json(csv_files, token)
    logging.info(f"CSV file links and token saved to {csv_path_link}")

    # Get session cookies from the browser
    session_cookies = get_session_cookies(browser)

    download_csv_files(csv_files, download_dir, token, browser, username, password, session_cookies)
    
    output_path = get_download_path()
    compress_to_zip(download_dir, output_path)
    
    browser.quit()

    

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
