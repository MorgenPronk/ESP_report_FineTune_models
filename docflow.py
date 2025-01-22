## File name: docflow.py
## Main entry point for CLI tool

import argparse
from pipeline.tasks.finetune_excel_to_jsonl import finetune_excel_to_jsonl
from pipeline.tasks.finetune_download_docs import finetune_download_docs
from pipeline.tasks.finetune_orchestrator import orchestrate_finetuning_pipeline
from pipeline.utils.pipeline_state_tracker import save_state
from pipeline.utils.load_config import load_config
from pipeline.tasks.finetune_enrich_jsonl import extract_text_and_enrich
from pipeline.tasks.finetune_model import (finetune_base_model, finetune_instruct_model)
import logging
import os

# Ensure the logs directory exists
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Configure logging
log_file = os.path.join(log_dir, "pipeline.log") # Log file path
logging.basicConfig(
    level = logging.INFO, # Change to DEBUG for more detailed logs
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def reset_pipeline_state():
    """
    Resets the pipeline state to 'pending' for all steps.
    This allows tasks to be re-executed as if starting from scratch.
    """
    default_state = {
    "finetune_excel_to_jsonl": "pending",
    "finetune_download_docs": "pending",
    "finetune_enrich_jsonl": "pending",
    "finetune_jsonl_empty_remove": "pending",
    "finetune_model": "pending"
}
    save_state(default_state)
    print("Pipeline state has been reset.")

def main():
    """
    Main entry point for the CLI.
    Defines and handles all commands for the pipeline, including finetuning and placeholders.
    """
    # Load the configuration file
    try:
        config = load_config("./configs/config.json")
    except FileNotFoundError:
        print("Warning: Config file not found. Using fallback defaults.")
        config = {}

    # Take values from the config file for use here
    # Extract default Google Drive folder ID from config or handle missing key
    default_google_drive_folder_id = config.get("task_settings", {}).get("google_drive_folder_id")

    if not default_google_drive_folder_id:
        print(
            "Warning: 'google_drive_folder_id' is missing in the config file. "
            "Ensure it is specified in the arguments when running the 'finetune_download_docs' command."
        )
        default_google_drive_folder_id = "no-folder-id-set"

    # CLI Argument Parser
    parser = argparse.ArgumentParser(description="Pipeline CLI for document processing and fine-tuning")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: Reset the pipeline state
    parser_reset = subparsers.add_parser("reset", help="Reset the pipeline state to pending")

    # Command: Finetune - Convert Excel to JSONL
    parser_finetune_excel_to_jsonl = subparsers.add_parser(
        "finetune_excel_to_jsonl", help="Convert Excel to JSONL for finetuning"
    )
    parser_finetune_excel_to_jsonl.add_argument("--input_excel_path",
                                                type=str, default="./datasets/finetuning_examples/AI Training_Install Reports.xlsx",
                                                help="Path to the input Excel file (default: './datasets/finetuning_examples/AI Training_Install Reports.xlsx')"
                                                )
    parser_finetune_excel_to_jsonl.add_argument("--output_jsonl_path",
                                                default="./datasets/finetuning_examples/finetuning_data.jsonl",
                                                help="Path to save the JSONL file (default: './datasets/finetuning_examples/finetuning_data.jsonl')"
                                                )
    # Command: Finetune - Download Documents
    parser_finetune_download_docs = subparsers.add_parser(
        "finetune_download_docs", help="Download documents for finetuning"
    )
    parser_finetune_download_docs.add_argument("--jsonl_path",
                                               type=str,
                                               default="./datasets/finetuning_examples/finetuning_data.jsonl",
                                               help="Path to the JSONL file"
                                               )
    parser_finetune_download_docs.add_argument("--download_folder",
                                               type=str,
                                               default="./datasets/google_drive_downloads",
                                               help="Path to save downloaded documents"
                                               )
    parser_finetune_download_docs.add_argument("--google_drive_folder_id",
                                               type=str,
                                               default=default_google_drive_folder_id,
                                               help=f"Google Drive folder ID (default: {default_google_drive_folder_id})"
                                               )

    # Command: Finetune - Enrich JSONL
    parser_finetune_enrich_jsonl = subparsers.add_parser(
        "finetune_enrich_jsonl", help="Enrich JSONL with text extracted from documents"
    )
    parser_finetune_enrich_jsonl.add_argument("--jsonl_path",
                                              type=str,
                                              default="./datasets/finetuning_examples/finetuning_data.jsonl",
                                              help="Path to the input JSONL file"
                                              )
    parser_finetune_enrich_jsonl.add_argument("--download_folder",
                                              type=str,
                                              default="./datasets/google_drive_downloads",
                                              help="Directory containing downloaded files",
                                              )
    parser_finetune_enrich_jsonl.add_argument("--output_jsonl",
                                              type=str,
                                              default="./datasets/finetuning_examples/enriched_dataset.jsonl",
                                              help="Path to save the enriched JSONL file",
                                              )
    parser_finetune_enrich_jsonl.add_argument("--log_missing_files",
                                              type=str,
                                              default="./logs/missing_files.txt",
                                              help="Path to save missing files log")

    # Subparser for fine-tuning base model
    base_parser = subparsers.add_parser("finetune_base_model", help="Fine-tune a base model")
    base_parser.add_argument("--model_name", type=str, required=True, help="Pre-trained model name or path")
    base_parser.add_argument("--dataset_path", type=str, required=True, help="Path to the dataset (JSONL)")
    base_parser.add_argument("--output_dir", type=str, required=True, help="Directory to save the fine-tuned model")
    base_parser.add_argument("--num_epochs", type=int, default=3, help="Number of training epochs")
    base_parser.add_argument("--batch_size", type=int, default=8, help="Batch size")
    base_parser.add_argument("--learning_rate", type=float, default=5e-5, help="Learning rate")
    base_parser.add_argument("--eval_split", type=float, default=0.1, help="Proportion of dataset for evaluation")

    # Subparser for fine-tuning instruction model
    instruct_parser = subparsers.add_parser("finetune_instruction_model", help="Fine-tune an instruction-tuned model")
    instruct_parser.add_argument("--model_name", type=str, required=True, help="Pre-trained model name or path")
    instruct_parser.add_argument("--dataset_path", type=str, required=True, help="Path to the dataset (JSONL)")
    instruct_parser.add_argument("--output_dir", type=str, required=True, help="Directory to save the fine-tuned model")
    instruct_parser.add_argument("--num_epochs", type=int, default=3, help="Number of training epochs")
    instruct_parser.add_argument("--batch_size", type=int, default=8, help="Batch size")
    instruct_parser.add_argument("--learning_rate", type=float, default=5e-5, help="Learning rate")
    instruct_parser.add_argument("--eval_split", type=float, default=0.1, help="Proportion of dataset for evaluation")

    # Command: Orchestrate the Full Finetuning Pipeline
    parser_finetune_orchestrator = subparsers.add_parser(
        "finetune_orchestrator", help="Run the full finetuning pipeline"
    )

    # Placeholder Command: Scrape Documents
    parser_scrape = subparsers.add_parser("scrape", help="Scrape documents (placeholder)")

    # Placeholder Command: Preview Documents
    parser_preview = subparsers.add_parser("preview", help="Preview documents (placeholder)")
    parser_preview.add_argument("--file_path", type=str, required=True, help="Path to the document to preview")

    # Parse CLI arguments
    args = parser.parse_args()

    # Command Handlers
    if args.command == "reset":
        reset_pipeline_state()
    elif args.command == "finetune_excel_to_jsonl":
        finetune_excel_to_jsonl(args.input_excel_path, args.output_jsonl_path)
    elif args.command == "finetune_download_docs":
        google_drive_folder_id = args.google_drive_folder_id
        finetune_download_docs(args.jsonl_path, args.download_folder, google_drive_folder_id)
    elif args.command == "finetune_enrich_jsonl":
        extract_text_and_enrich(args.jsonl_path, args.download_folder, args.output_jsonl, args.log_missing_files)
    elif args.command == "finetune_base_model":
        finetune_base_model(
            model_name=args.model_name,
            dataset_path=args.dataset_path,
            output_dir=args.output_dir,
            num_epochs=args.num_epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
            eval_split=args.eval_split,
        )
    elif args.command == "finetune_instruction_model":
        finetune_instruct_model(
            model_name=args.model_name,
            dataset_path=args.dataset_path,
            output_dir=args.output_dir,
            num_epochs=args.num_epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
            eval_split=args.eval_split,
        )
    elif args.command == "finetune_orchestrator":
        orchestrate_finetuning_pipeline(config)
    elif args.command == "scrape":
        print("Scrape functionality is not yet implemented.")
    elif args.command == "preview":
        print(f"Preview functionality is not yet implemented. File: {args.file_path}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
