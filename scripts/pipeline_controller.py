import os
from load_config import load_config
from script1_generate_jsonl import main as run_script1
from script2_download_files import main as run_script2
from script3_extract_text import main as run_script3
from script4_finetune_model import main as run_script4

def check_flag(flag_path):
    """Checks if a flag file exists."""
    return os.path.exists(flag_path)

def create_flag(flag_path):
    """Creates a flag file."""
    with open(flag_path, "w") as f:
        f.write("")

def main(config_path):
    """
    Orchestrates the pipeline by passing configurations to each step.
    """
    config = load_config(config_path)

    try:
        #TODO: There is a problem with "# Stages" being a number sometimes and a string in others. We need to fix it.

        # Step 1: Generate JSONL file
        flag_step1 = "../flags/generated_jsonl.flag"
        if not check_flag(flag_step1):
            print("Step 1: Generating JSONL file...")
            run_script1(config)
            create_flag(flag_step1)
        else:
            print("Step 1 already completed. Skipping...")

        # Step 2: Download files
        flag_step2 = "../flags/downloaded_files.flag"
        if not check_flag(flag_step2):
            print("Step 2: Downloading files from Google Drive...")
            run_script2(config)
            create_flag(flag_step2)
        else:
            print("Step 2 already completed. Skipping...")

        # Step 3: Extract text from documents
        flag_step3 = "../flags/extracted_text.flag"
        if not check_flag(flag_step3):
            print("Step 3: Extracting text from documents...")
            run_script3(config)
            create_flag(flag_step3)
        else:
            print("Step 3 already completed. Skipping...")

        # Step 4: Fine-tuning the model
        print("Step 4: Fine-tuning the model...")
        run_script4(config)

        print("Pipeline completed successfully!")
    except Exception as e:
        print("Pipeline failed!")
        raise e

if __name__ == "__main__":
    config_path = "../configs/config.json"
    main(config_path)
