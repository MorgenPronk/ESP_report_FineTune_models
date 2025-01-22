import os
import json
from pipeline.utils.pipeline_state_tracker import check_step_completed, update_state
from pipeline.utils.pdf_extraction import get_text_from_pdf
from pipeline.utils.excel_extraction import get_text_from_excel

def log_missing_files(missing_files, log_path):
    """
    Logs the missing files to a specified path.

    Args:
        missing_files (list): List of file names that could not be found.
        log_path (str): Path to save the log file.
    """
    log_dir = os.path.dirname(log_path)
    os.makedirs(log_dir, exist_ok=True)

    with open(log_path, "w") as file:
        file.write("The following files could not be found:\n")
        for missing_file in missing_files:
            file.write(f"{missing_file}\n")
    print(f"Missing files logged to: {log_path}")

def extract_text_and_enrich(jsonl_path, download_folder, output_jsonl, log_file_path):
    """
    Extracts text from files listed in the JSONL dataset and enriches the dataset with the extracted text.

    Args:
        jsonl_path (str): Path to the JSONL file.
        download_folder (str): Directory containing the downloaded files.
        output_jsonl (str): Path to save the enriched JSONL file.
        log_file_path (str): Path to save the list of missing files.

    Returns:
        None: Saves the enriched dataset to a JSONL file and logs missing files.
    """
    if check_step_completed("finetune_enrich_jsonl"):
        print("Enrich_jsonl step already completed. Skipping...")
        return

    # Ensure the directory for log_file_path exists
    log_dir = os.path.dirname(log_file_path)
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
        with open(log_file_path, "w") as log_file:
            log_file.write("The following files were not found:\n")
            for missing_file in missing_files:
                log_file.write(f"{missing_file}\n")
        print(f"Missing files logged to {log_file_path}")

    # Update state
    update_state("finetune_enrich_jsonl", "completed")