## File name: finetune_download_docs.py
## Task for the finetuning pipeline

import json
import os
from pipeline.utils.pipeline_state_tracker import check_step_completed, update_state
from pipeline.utils.google_drive_file_finder import (
    authenticate_google_drive,
    download_files_from_list,
)
import logging

logger = logging.getLogger(__name__)

def get_file_names_from_jsonl(jsonl_path):
    """
    Extracts file names from the JSONL dataset.

    Args:
        jsonl_path (str): Path to the JSONL file.

    Returns:
        list: List of file names.
    """
    file_names = []
    with open(jsonl_path, "r") as file:
        for line in file:
            record = json.loads(line)
            if "document" in record:
                file_names.append(record["document"])
    return file_names

def log_missing_files(missing_files):
    """
    Logs the missing files to a 'missing_files.txt' file in the logs directory.

    Args:
        missing_files (list): List of file names that could not be found.
    """
    logs_directory = "./logs"
    os.makedirs(logs_directory, exist_ok=True)

    missing_files_path = os.path.join(logs_directory, "missing_files.txt")
    with open(missing_files_path, "w") as file:
        file.write("The following files could not be found in Google Drive:\n")
        for missing_file in missing_files:
            file.write(f"{missing_file}\n")
    print(f"Missing files logged to: {missing_files_path}")

def finetune_download_docs(jsonl_path, download_folder, google_drive_folder_id):
    """
    Downloads files listed in a JSONL file from Google Drive to a specified folder.

    Args:
        jsonl_path (str): Path to the JSONL file containing file names.
        download_folder (str): Path to the folder where files will be downloaded.
        google_drive_folder_id (str): Google Drive folder ID to search files in.

    Raises:
        ValueError: If the `google_drive_folder_id` is missing or invalid.
    """
    # Validate the folder ID
    if not google_drive_folder_id or google_drive_folder_id == "no-folder-id-set":
        raise ValueError(
            "Invalid Google Drive folder ID. Ensure a valid folder ID is specified in the config file or as an argument."
        )

    # Check if the step has already been completed
    if check_step_completed("download_docs"):
        print("Download step already completed. Skipping...")
        return

    #logger.info(f"Downloading documents listed in {jsonl_path} to {download_folder}...")
    print(f"Downloading documents listed in {jsonl_path} to {download_folder}...")

    # Authenticate with Google Drive
    service = authenticate_google_drive({"google_drive_credentials_file": "./configs/credentials.json"})

    # Extract file names from the JSONL dataset
    file_names = get_file_names_from_jsonl(jsonl_path)
    logger.info(f"Extracted file names: {file_names}") # Debugging

    # Download the files from Google Drive
    found_files = download_files_from_list(service=service,
                                           folder_id=google_drive_folder_id,
                                           file_names=file_names,
                                           download_folder=download_folder,
                                           exact_match=True,
                                           list_findable=True,
                                           )

    # Identify missing files
    missing_files = set(file_names) - set(found_files.keys())
    if missing_files:
        log_missing_files(list(missing_files))

    # Update the state tracker
    update_state("download_docs", "completed")
    print("Download documents step completed.")
