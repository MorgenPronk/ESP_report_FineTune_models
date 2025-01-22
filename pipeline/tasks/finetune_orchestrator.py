from pipeline.tasks.finetune_excel_to_jsonl import finetune_excel_to_jsonl
from pipeline.tasks.finetune_download_docs import finetune_download_docs
from pipeline.tasks.finetune_model import finetune_base_model, finetune_instruct_model
from pipeline.utils.load_config import validate_config
from pipeline.utils.dataset_cleaner import filter_valid_data
from pipeline.utils.pipeline_state_tracker import check_step_completed, update_state

def orchestrate_finetuning_pipeline(config):
    """
    Orchestrates the finetuning pipeline.

    Args:
        config (dict): Loaded configuration dictionary.
    """
    print("Starting finetuning pipeline...")

    # Validate required keys
    validate_config(config["file_paths"], ["input_excel_path", "output_jsonl_path", "download_folder", "enriched_jsonl_path", "filtered_jsonl_path"])
    validate_config(config["task_settings"], ["google_drive_folder_id", "fine_tune"])

    # Step 1: Convert Excel to JSONL
    print("Step 1: Converting Excel to JSONL...")
    finetune_excel_to_jsonl(
        config["file_paths"]["input_excel_path"],
        config["file_paths"]["output_jsonl_path"]
    )

    # Step 2: Download Documents
    print("Step 2: Downloading documents...")
    finetune_download_docs(
        config["file_paths"]["output_jsonl_path"],
        config["file_paths"]["download_folder"],
        config["task_settings"]["google_drive_folder_id"]
    )

    # Step 3: Filter Invalid Data
    print("Step 3: Filtering invalid data...")
    valid_records_count = filter_valid_data(
        config["file_paths"]["enriched_jsonl_path"],
        config["file_paths"]["filtered_jsonl_path"]
    )
    # Usually states updates are with tasks, but here we will update in the orchestrator
    update_state("finetune_jsonl_empty_remove", "completed")
    print(f"Filtered dataset saved with {valid_records_count} valid records.")

    if valid_records_count == 0:
        print("No valid data found for fine-tuning. Pipeline terminated.")
        return

    # Step 4: Fine-tune the Model
    print("Step 4: Fine-tuning the model...")
    fine_tune_settings = config["task_settings"]["fine_tune"]
    model_type = fine_tune_settings.get("model_type", "base")  # Default to base model

    if model_type == "instruct":
        finetune_instruct_model(
            model_name=fine_tune_settings["model_name"],
            dataset_path=config["file_paths"]["filtered_jsonl_path"],
            output_dir=fine_tune_settings["output_dir"],
            num_epochs=fine_tune_settings.get("num_epochs", 3),
            batch_size=fine_tune_settings.get("batch_size", 8),
            learning_rate=fine_tune_settings.get("learning_rate", 5e-5),
            eval_split=fine_tune_settings.get("eval_split", 0.1),
        )
    elif model_type == "base":
        finetune_base_model(
            model_name=fine_tune_settings["model_name"],
            dataset_path=config["file_paths"]["filtered_jsonl_path"],
            output_dir=fine_tune_settings["output_dir"],
            num_epochs=fine_tune_settings.get("num_epochs", 3),
            batch_size=fine_tune_settings.get("batch_size", 8),
            learning_rate=fine_tune_settings.get("learning_rate", 5e-5),
            eval_split=fine_tune_settings.get("eval_split", 0.1),
        )
    else:
        print(f"Unknown model type '{model_type}'. Please specify 'base' or 'instruct' in the configuration.")
        return

    print("Finetuning pipeline completed.")
