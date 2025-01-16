## script3_extract_text.py

import os
import json
from pdf_extraction import get_text_from_pdf
from excel_extraction import get_text_from_excel
from load_config import load_config

def extract_text_and_enrich(jsonl_path, download_folder, output_jsonl, log_missing_files):
    """
    Extracts text from files listed in the JSONL dataset and enriches the dataset with the extracted text.

    Args:
        jsonl_path (str): Path to the JSONL file.
        download_folder (str): Directory containing the downloaded files.
        output_jsonl (str): Path to save the enriched JSONL file.
        log_missing_files (str): Path to save the list of missing files.

    Returns:
        None: Saves the enriched dataset to a JSONL file and logs missing files.
    """
    # Ensure the directory for log_missing_files exists
    log_dir = os.path.dirname(log_missing_files)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    with open(jsonl_path, "r") as file:
        dataset = [json.loads(line) for line in file]

    enriched_data = []
    missing_files = []

    for record in dataset:
        file_name = record["document"]
        file_path = os.path.join(download_folder, file_name)

        # Check if the file exists
        if not os.path.exists(file_path):
            print(f"File missing: {file_name}")
            missing_files.append(file_name)
            # Add placeholder text for missing files
            record["text"] = "File not found"
            enriched_data.append(record)
            continue

        # Extract text based on file type
        text = ""
        try:
            if file_name.endswith(".pdf"):
                text = get_text_from_pdf(file_path)
            elif file_name.endswith(".xls") or file_name.endswith(".xlsx"):
                text = get_text_from_excel(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_name}")
        except Exception as e:
            print(f"Error extracting text from {file_name}: {e}")
            text = f"Error extracting text: {e}"

        # Add extracted text to record
        record["text"] = text
        enriched_data.append(record)

    # Save enriched dataset
    with open(output_jsonl, "w") as output_file:
        for entry in enriched_data:
            output_file.write(json.dumps(entry) + "\n")

    print(f"Enriched JSONL saved at {output_jsonl}")

    # Save missing files log
    if missing_files:
        with open(log_missing_files, "w") as log_file:
            log_file.write("The following files were not found:\n")
            for missing_file in missing_files:
                log_file.write(f"{missing_file}\n")
        print(f"Missing files logged to {log_missing_files}")

def main(config):
    """
    Main function to run the script. Uses default paths for now.
    """
    JSONL_PATH = config['output_jsonl_path']
    DOWNLOAD_FOLDER = config['download_folder']
    OUTPUT_JSONL_PATH = config['enriched_jsonl_path']
    LOG_MISSING_FILES = config['log_missing_files_path']
    extract_text_and_enrich(
        jsonl_path=JSONL_PATH,
        download_folder=DOWNLOAD_FOLDER,
        output_jsonl=OUTPUT_JSONL_PATH,
        log_missing_files=LOG_MISSING_FILES,
    )

if __name__ == "__main__":
    config = load_config('../configs/config.json')
    main(config)
