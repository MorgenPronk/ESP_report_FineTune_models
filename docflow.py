import argparse
from pipeline.tasks.finetune_excel_to_jsonl import finetune_excel_to_jsonl
from pipeline.tasks.finetune_download_docs import finetune_download_docs
from pipeline.tasks.finetune_model import finetune_model
from pipeline.tasks.finetune_orchestrator import orchestrate_finetuning_pipeline
from pipeline.utils.pipeline_state_tracker import save_state

def reset_pipeline_state():
    """
    Resets the pipeline state to 'pending' for all steps.
    This allows tasks to be re-executed as if starting from scratch.
    """
    default_state = {
        "excel_to_jsonl": "pending",
        "download_docs": "pending",
        "finetune_model": "pending",
    }
    save_state(default_state)
    print("Pipeline state has been reset.")

def main():
    """
    Main entry point for the CLI.
    Defines and handles all commands for the pipeline, including finetuning and placeholders.
    """
    parser = argparse.ArgumentParser(description="Pipeline CLI for document processing and fine-tuning")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: Reset the pipeline state
    parser_reset = subparsers.add_parser("reset", help="Reset the pipeline state to pending")

    # Command: Finetune - Convert Excel to JSONL
    parser_finetune_excel_to_jsonl = subparsers.add_parser(
        "finetune_excel_to_jsonl", help="Convert Excel to JSONL for finetuning"
    )
    parser_finetune_excel_to_jsonl.add_argument("--input-excel-path", type=str, required=True, help="Path to the input Excel file")
    parser_finetune_excel_to_jsonl.add_argument("--output-jsonl-path", type=str, required=True, help="Path to save the JSONL file")

    # Command: Finetune - Download Documents
    parser_finetune_download_docs = subparsers.add_parser(
        "finetune_download_docs", help="Download documents for finetuning"
    )
    parser_finetune_download_docs.add_argument("--jsonl-path", type=str, required=True, help="Path to the JSONL file")
    parser_finetune_download_docs.add_argument("--download-folder", type=str, required=True, help="Path to save downloaded documents")
    parser_finetune_download_docs.add_argument("--google-drive-folder-id", type=str, required=True, help="Google Drive folder ID")

    # Command: Finetune - Fine-tune the Model
    parser_finetune_model = subparsers.add_parser(
        "finetune_model", help="Fine-tune the model using enriched JSONL"
    )
    parser_finetune_model.add_argument("--enriched-jsonl-path", type=str, required=True, help="Path to the enriched JSONL file")
    parser_finetune_model.add_argument("--model-output-path", type=str, required=True, help="Path to save the fine-tuned model")

    # Command: Orchestrate the Full Finetuning Pipeline
    parser_finetune_orchestrator = subparsers.add_parser(
        "finetune_orchestrator", help="Run the full finetuning pipeline"
    )
    parser_finetune_orchestrator.add_argument("--config-path", type=str, required=True, help="Path to the pipeline configuration file")

    # Placeholder Command: Scrape Documents
    parser_scrape = subparsers.add_parser("scrape", help="Scrape documents (placeholder)")

    # Placeholder Command: Preview Documents
    parser_preview = subparsers.add_parser("preview", help="Preview documents (placeholder)")
    parser_preview.add_argument("--file-path", type=str, required=True, help="Path to the document to preview")

    # Parse CLI arguments
    args = parser.parse_args()

    # Command Handlers
    if args.command == "reset":
        reset_pipeline_state()
    elif args.command == "finetune_excel_to_jsonl":
        finetune_excel_to_jsonl(args.input_excel_path, args.output_jsonl_path)
    elif args.command == "finetune_download_docs":
        finetune_download_docs(args.jsonl_path, args.download_folder, args.google_drive_folder_id)
    elif args.command == "finetune_model":
        finetune_model(args.enriched_jsonl_path, args.model_output_path)
    elif args.command == "finetune_orchestrator":
        from pipeline.utils.load_config import load_config
        config = load_config(args.config_path)
        orchestrate_finetuning_pipeline(config)
    elif args.command == "scrape":
        print("Scrape functionality is not yet implemented.")
    elif args.command == "preview":
        print(f"Preview functionality is not yet implemented. File: {args.file_path}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
