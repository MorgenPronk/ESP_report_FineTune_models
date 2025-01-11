from load_config import load_config
from script1_generate_jsonl import main as run_script1
from script2_download_files import main as run_script2
from script3_extract_text import main as run_script3
from script4_finetune_model import main as run_script4

def main(config_path):
    """
    Orchestrates the pipeline by passing configurations to each step.
    """
    config = load_config(config_path)

    try:
        print("Step 1: Generating JSONL file...")
        run_script1(config)

        print("Step 2: Downloading files from Google Drive...")
        run_script2(config)

        print("Step 3: Extracting text from documents...")
        run_script3(config)

        print("Step 4: Fine-tuning the model...")
        run_script4(config)  # Fine-tune the model

        print("Pipeline completed successfully!")
    except Exception as e:
        print("Pipeline failed!")
        raise e

if __name__ == "__main__":
    config_path = "../configs/config.json"
    main(config_path)
