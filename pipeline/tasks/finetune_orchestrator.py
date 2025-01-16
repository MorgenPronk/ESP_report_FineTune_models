from pipeline.tasks.finetune_excel_to_jsonl import finetune_excel_to_jsonl
from pipeline.tasks.finetune_download_docs import finetune_download_docs
from pipeline.tasks.finetune_model import finetune_model
from pipeline.utils.load_config import validate_config

def orchestrate_finetuning_pipeline(config):
    """
    Orchestrates the finetuning pipeline.

    Args:
        config (dict): Loaded configuration dictionary.
    """
    print("Starting finetuning pipeline...")

    # Validate required keys
    validate_config(config["file_paths"], ["input_excel_path", "output_jsonl_path", "download_folder", "enriched_jsonl_path"])
    validate_config(config["task_settings"], ["google_drive_folder_id", "fine_tune"])

    # Step 1: Convert Excel to JSONL
    finetune_excel_to_jsonl(
        config["file_paths"]["input_excel_path"],
        config["file_paths"]["output_jsonl_path"]
    )

    # Step 2: Download Documents
    finetune_download_docs(
        config["file_paths"]["output_jsonl_path"],
        config["file_paths"]["download_folder"],
        config["task_settings"]["google_drive_folder_id"]
    )

    # Step 3: Fine-tune the Model
    finetune_model(
        config["file_paths"]["enriched_jsonl_path"],
        config["task_settings"]["fine_tune"]["output_dir"]
    )

    print("Finetuning pipeline completed.")
