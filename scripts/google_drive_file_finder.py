##File name: google_drive_file_finder.py
import os
import io
import json
import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request
import googleapiclient.errors
from scripts.load_config import load_config
import logging

def log_to_file(message, log_file="output_log.txt"):
    """
    Writes a message to the specified log file.

    :param message: (str) The message to log.
    :param log_file: (str) The path to the log file.
    :return:
    """
    with open(log_file, "a") as f: # Open in append mode
        f.write(message + "\n")

# Scopes needed to access the files in Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def authenticate_google_drive(config):
    """
    Authenticate with the Google Drive API using OAuth 2.0.

    Args:
        config (dict): config dictionary converted from a JSON file.

    Returns:
        service: Authenticated Google Drive API service instance.
    """

    creds = None
    creds_file = config.get("google_drive_credentials_file")

    if os.path.exists(creds_file):
        try:
            creds = Credentials.from_authorized_user_file(creds_file, SCOPES)
        except ValueError:
            print("Invalid token.json file. Regenerating token...")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Prompt user to authenticate and generate new token.json
            flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
            creds = flow.run_local_server(port=0)
            with open(creds_file, "w") as token:
                token.write(creds.to_json())

    service = build('drive', 'v3', credentials=creds)
    return service


def list_all_files(service, folder_id, output_file="./listed_files.txt"):
    """
    List all files and folders within the given folder and its subfolders, handling pagination.

    Args:
        service: Authenticated Google Drive API service instance.
        folder_id: ID of the Google Drive folder to start listing from.

    Returns:
        None: Prints the files and folders found to the console.
    """
    print(f"...Listing all findable files in folder and subfolders of folder id {folder_id}")
    log_to_file(f"Listing all files in folder ID: {folder_id} and saving to {output_file}")
    folders_to_search = [folder_id]

    while folders_to_search:
        current_folder = folders_to_search.pop()
        query = f"'{current_folder}' in parents and trashed=false"

        page_token = None
        while True:
            results = service.files().list(
                q=query,
                fields="nextPageToken, files(id, name, mimeType)",
                pageToken=page_token
            ).execute()

            items = results.get('files', [])
            for item in items:
                log_to_file(f"File: {item['name']}, ID: {item['id']}, MIME Type: {item['mimeType']}")
                # If it's a folder, add it to the search list
                if item['mimeType'] == 'application/vnd.google-apps.folder':
                    folders_to_search.append(item['id'])

            # Check if there are more pages to fetch
            page_token = results.get('nextPageToken', None)
            if not page_token:
                break

def search_files_recursively(service, folder_id, file_names, exact_match=True):
    """
    Search for specific files by name in a Google Drive folder and its subfolders, handling pagination.

    Args:
        service: Authenticated Google Drive API service instance.
        folder_id: ID of the Google Drive folder to start searching from.
        file_names: List of file names to search for.
        exact_match: Boolean to specify if the search should be exact (True) or partial (False).

    Returns:
        dict: A dictionary with file names as keys and their corresponding file IDs as values.
    """
    found_files = {}
    folders_to_search = [folder_id]

    # Normalize file names for case-insensitive comparison
    normalized_file_names = [name.strip().lower() for name in file_names]

    while folders_to_search:
        current_folder = folders_to_search.pop()
        query = f"'{current_folder}' in parents and trashed=false"

        # Pagination setup
        page_token = None
        while True:
            try:
                results = service.files().list(
                    q=query,
                    fields="nextPageToken, files(id, name, mimeType)",
                    pageToken=page_token
                ).execute()

                items = results.get('files', [])
                if not items:
                    break

                for item in items:
                    # If it's a folder, add it to the search list
                    if item['mimeType'] == 'application/vnd.google-apps.folder':
                        folders_to_search.append(item['id'])
                    # Check for file match based on the exact_match parameter
                    elif exact_match:
                        if item['name'].strip().lower() in normalized_file_names:
                            found_files[item['name']] = item['id']
                    else:
                        if any(name in item['name'].strip().lower() for name in normalized_file_names):
                            found_files[item['name']] = item['id']

                # Check if there are more pages to fetch
                page_token = results.get('nextPageToken', None)
                if not page_token:
                    break

            except googleapiclient.errors.HttpError as e:
                print(f"Error during API call: {e}")
                break

    return found_files


def download_file_from_drive(service, file_id, destination):
    """
    Download a file from Google Drive by its file ID.

    Args:
        service: Authenticated Google Drive API service instance.
        file_id: ID of the file to download.
        destination: Local path to save the downloaded file.

    Returns:
        None: Saves the file to the specified destination.
    """
    try:
        # Try downloading the file as binary
        request = service.files().get_media(fileId=file_id)
        with io.FileIO(destination, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Download {int(status.progress() * 100)}% complete.")
    except googleapiclient.errors.HttpError as e:
        # Handle files that need to be exported (Google Docs Editors files)
        if 'fileNotDownloadable' in str(e):
            file_metadata = service.files().get(fileId=file_id, fields="mimeType").execute()
            mime_type = file_metadata.get('mimeType')
            export_mime_map = {
                'application/vnd.google-apps.document': 'application/pdf',
                'application/vnd.google-apps.spreadsheet': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'application/vnd.google-apps.presentation': 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            }
            export_mime = export_mime_map.get(mime_type)
            if export_mime:
                request = service.files().export_media(fileId=file_id, mimeType=export_mime)
                with io.FileIO(destination, 'wb') as fh:
                    downloader = MediaIoBaseDownload(fh, request)
                    done = False
                    while not done:
                        status, done = downloader.next_chunk()
                        print(f"Export {int(status.progress() * 100)}% complete.")
            else:
                print(f"Cannot export file with MIME type: {mime_type}")
        else:
            raise

def download_files_from_list(service, folder_id, file_names, download_folder, exact_match=True, list_findable=False):
    """
    Search for specific files in Google Drive and download them to a local directory.

    Args:
        service: Authenticated Google Drive API service instance.
        folder_id: ID of the Google Drive folder to start searching from.
        file_names: List of file names to search for.
        download_folder: Local folder to save downloaded files.
        exact_match: Boolean to specify if the search should be exact (True) or partial (False).

    Returns:
        None: Downloads the files and logs missing files.
    """
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    # List all files for debugging purposes
    if list_findable == True:
        list_all_files(service, folder_id)

    # Search for the files recursively
    print("Searching for files recursively...")
    found_files = search_files_recursively(service, folder_id, file_names, exact_match=exact_match)

    # Log found files
    print("Files Found:")
    for name in found_files:
        print(f" - {name}")

    for file_name, file_id in found_files.items():
        print(f"Downloading {file_name}...")
        destination = os.path.join(download_folder, file_name)
        download_file_from_drive(service, file_id, destination)
        print(f"Downloaded {file_name} to {destination}")

    # Report missing files
    missing_files = set(file_names) - set(found_files.keys())
    if missing_files:
        missing_files_path = os.path.join(download_folder, 'missing_files.txt')
        with open(missing_files_path, 'w') as missing_file_log:
            missing_file_log.write("The following files were not found:\n")
            for missing_file in missing_files:
                missing_file_log.write(f"{missing_file}\n")
        print(f"Missing files logged to {missing_files_path}")

if __name__ == '__main__':
    # config file location
    config_file_path = "../configs/config.json"

    # load config
    config = load_config(config_file_path)

    # Authenticate and get the Drive service
    service = authenticate_google_drive(config)

    # Specify the Google Drive folder ID
    folder_id = '1XvHukPiinuqxDUthxJRQ0zTNY5ESUupq'

    # Specify the list of file names to search for
    file_names = pd.Series(["ESP Install Report Ledahl 5402 42-33 2BX.pdf", "B-18 (2).pdf", "B-18 NC115, H-47 NC115 & J-21 NC186 Well Testing Results Report.pdf"])

    # Specify the local folder to download files
    download_folder = '../datasets/google_drive_downloads'

    # Search and download files with exact matching enabled
    download_files_from_list(service, folder_id, file_names, download_folder, exact_match=True)
