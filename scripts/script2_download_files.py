import json
from google_drive_file_finder import authenticate_google_drive, download_files_from_list

def main(config):
    # Extract configuration parameters
    jsonl_path = config["output_jsonl_path"]
    download_folder = config["download_folder"]
    google_drive_folder_id = config["google_drive_folder_id"]

    # Authenticate with Google Drive
    service = authenticate_google_drive(config)

    # Extract file names from the JSONL dataset
    file_names = get_file_names_from_jsonl(jsonl_path)
    print(f"Extracted file names: {file_names}")

    # Download the files from Google Drive
    download_files_from_list(
        service=service,
        folder_id=google_drive_folder_id,
        file_names=file_names,
        download_folder=download_folder,
        exact_match=True,
        list_findable=True
    )

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
