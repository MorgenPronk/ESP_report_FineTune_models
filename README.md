## TODO List for ESP Report Project

### Step 1: Project Setup
- [x] Set up virtual environment
- [x] Initialize Git repository
- [x] Add `.gitignore` file

### Step 2: Model Fine-Tuning
- [ ] Prepare dataset in JSONL format
  - [ ] make a function to take excel into JSONL
    - [x] function that gets the sanitized name equivalent
    - [x] check how many matches we get of the QC data and the extracted text examples that we have
    - [x] find and download missing files (currently 43)
    - [ ] scrap text from the finetuning examples
      - [ ] formalize the tool that takes the text
      - 
- [ ] Fine-tune Llama 3.2 model
- [ ] Save fine-tuned model in `models/` directory

### Step 3: Inference Script
- [ ] Write inference script
- [ ] Test model predictions with sample data

### Step 4: Deployment
- [ ] Push model to Hugging Face Hub
- [ ] Deploy model using Hugging Face Inference Endpoint

## Additional Ideas:
- General AI where one person can just ask questions about any of the documents
- General AI where you can ask questions about one document
- How to make general AI from structured data, that can ask questions about any of the wells
  - This is likely something that has already been done
  - How to prevent it from answering questions from other people's wells

# Example CLI Commands
## Finetune pipeline orchestrator
python docflow.py finetune_orchestrator --config-path ./configs/config.json

## Finetune using prepared jsonl file
python docflow.py finetune_excel_to_jsonl --input-excel-path ./datasets/finetuning_examples/AI_Training_Install_Reports.xlsx --output-jsonl-path ./datasets/finetuning_examples/finetuning_data.jsonl

# CLI Commands for DocFlow

This document outlines all available CLI commands for the DocFlow tool. These commands include core pipeline tasks, state management, and placeholders for future functionality.

---

## **Core Commands**

### 1. Reset Pipeline State
Resets the state of all pipeline tasks to `pending`.

```
python docflow.py reset
```
Expected behavior:
- Resets `pipeline_state.json` with all tasks set to `pending`.

### 2. Run full Finetuning Pipeline
Executes all finetune tasks in sequence using the orchestrator
```
python docflow.py finetune_orchestrator --config-path ./configs/config.json
```
Expected Behavior:
- Executes all tasks in sequence, skipping already completed ones
- prints messages indicating task progress and completion

### 3. Run Individual Tasks
These commands allow you to run each task independently.

#### Convert Excel to JSONL
Converts a prepared excel file, that has human scraped data, to the JSONL format required for finetuning.
```commandline
python docflow.py finetune_excel_to_jsonl --input-excel-path "./datasets/finetuning_examples/AI Training_Install Reports.xlsx" --output-jsonl-path "./datasets/finetuning_examples/finetuning_data.jsonl"
```
Expected Behavior:
- Task executes and updates the state
- prints a message indicating successful execution.

#### Download Documents
Searches files that match name in given google drive and downloads them.
```
python docflow.py finetune_download_docs --jsonl-path ./datasets/finetuning_examples/finetuning_data.jsonl --download-folder ./datasets/google_drive_downloads --google-drive-folder-id your-folder-id
```
Expected Behavior:
- Task executes and updates the state
- prints a message indicating successful execution

#### Fine-tune the Model
Simulates fine-tuning the model using the enriched JSONL file
```commandline
python docflow.py finetune_model --enriched-jsonl-path ./datasets/finetuning_examples/enriched_dataset.jsonl --model-output-path ./models/fine_tuned_model
```
### CLI Help Commands
#### General Help
```
python docflow.py --help
```
Expected Behavior:
- Lists all available commands with descriptions.

#### Task-Specific Help
```
python docflow.py finetune_excel_to_jsonl --help
python docflow.py finetune_download_docs --help
python docflow.py finetune_model --help
python docflow.py finetune_orchestrator --help
python docflow.py preview --help
```
Expected Behavior:
- Displays the correct arguments and descriptions for each command.

# Intended file structure
```
docflow/
│
├── docflow.py              # Main entry point for the CLI
│
├── pipeline/               # Core functionality and modular tasks
│   ├── __init__.py         # Makes this directory a Python module
│   │
│   ├── tasks/              # Specific tasks (e.g., scraping, fine-tuning)
│   │   ├── scrape.py       # Step 1 and 3 combined into a scrape task
│   │   ├── download.py     # Step 2: Downloading files
│   │   ├── finetune.py     # Step 4: Fine-tuning the model
│   │   └── orchestrate.py  # Optional: Task orchestration logic (replaces pipeline_controller.py)
│
│   ├── utils/              # Reusable utilities
│   │   ├── drive.py        # Google Drive interaction
│   │   ├── text_extraction.py # Text extraction logic
│   │   ├── logging.py      # Logging utilities
│   │   ├── config.py       # Configuration loader
│   │   └── file_handling.py # File management utilities
│   │
│   ├── preprocess.py       # Handles document preparation (e.g., OCR, cleaning)
│   ├── postprocess.py      # Handles formatting outputs (e.g., JSONL creation)
│   └── finetune.py         # Core logic for LLM fine-tuning
│
├── configs/                # Configuration and credential files
│   ├── config.json         # General configuration (paths, defaults, etc.)
│   ├── credentials.json    # Credentials for Google Drive or other services
│   ├── pipeline_state.json # handles the states for the pipeline
│
├── data/                   # All input/output data
│   ├── raw/                # Raw input documents (PDFs, etc.)
│   ├── processed/          # Processed documents
│   ├── jsonl/              # JSONL outputs
│   └── training/           # Fine-tuning datasets
│
├── models/                 # Trained and fine-tuned models
│   ├── base_model/         # Base model checkpoint
│   ├── fine_tuned/         # Fine-tuned model versions
│   └── checkpoints/        # Training checkpoints
│
├── tests/                  # Unit and integration tests
│   ├── test_tasks.py       # Tests for task modules (scrape, finetune, etc.)
│   ├── test_utils.py       # Tests for utility functions
│   ├── test_end_to_end.py  # Integration tests for the CLI
│
├── logs/                   # Logs for debugging and usage tracking
│   ├── main.log            # Centralized log file
│
├── .env                    # Environment variables for sensitive info
├── .gitignore              # Git ignore file
├── README.md               # Documentation for the project
└── requirements.txt        # Python dependencies
```