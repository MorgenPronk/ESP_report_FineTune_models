## TODO List for ESP Report Project

### Misc
- [ ] Clean up the code and functionality currently and make modular so that we can experiment with different environments, machines, and models easier.
  - [ ] Probably need to know docker maybe for this? Not sure.
- [ ] make things pretty for a demo. Where we can show that it works
  - [ ] json to excel to more easily show the outputs.
  - [ ] drag and drop document feature. Maybe?

### Step 1: Project Setup
- [x] Set up virtual environment
- [x] Initialize Git repository
- [x] Add `.gitignore` file

### Step 2: Model Fine-Tuning
- [ ] Prepare dataset in JSONL format
  - [ ] make sure that `nan` is not used in json, and that `"` is used and not `'`. I.e. Make sure the JSON is valid.
  - [ ] make a function to take excel into JSONL
    - [x] function that gets the sanitized name equivalent
    - [x] check how many matches we get of the QC data and the extracted text examples that we have
    - [x] find and download missing files (currently 43)
    - [ ] scrap text from the finetuning examples
      - [ ] formalize the tool that takes the text


- [ ] Fine-tune using Gemini API
- [ ] Fine-tune Llama 3.2 model
- [ ] Save fine-tuned model in `models/` directory

### Step 3: Inference Script
- [ ] Write inference script
- [ ] Test model predictions with sample data

### Step 4: Deployment
- [ ] Push model to Hugging Face Hub
- [ ] Deploy model using Hugging Face Inference Endpoint

### Step x: Agents
- [ ] Have agents or langchain or something that can help make sure that the json is valid.

## Additional Ideas:
- General AI where one person can just ask questions about any of the documents
- General AI where you can ask questions about one document
- How to make general AI from structured data, that can ask questions about any of the wells
  - This is likely something that has already been done
  - How to prevent it from answering questions from other people's wells
- Make a tool where someone highlights the area where the data is located when they go through and scrape the data so I can know where and what can be dropped (or truncated from the document)
- finetune other models on lambda labs or google cloud
  - This is going to cost some money
    - Google cloud might be good because of it's gigantic context window - if we can still actually do that
    - It seems that it doesn't need a ton of examples to do a good job of scraping the data.
- Need to do something about post-processing the json artifacts. e.g. ('''json...''')

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
│   │   ├── finetune_excel_to_jsonl.py       # Step 1: info from people reviewed data in excel and put it into a jsonl format for the output of the finetuning
│   │   ├── finetune_download_docs.py     # Step 2: Looks through google drive and downloads files that were reviewed
│   │   ├── finetune_enrich_jsonl.py     # Step 4: takes the raw text and does OCR on the files so we have an input for the finetuning
│   │   ├── finetune_model.py  # Step 5: actually does the finetuning/training of the model
│   │   └── finetune_orchestrator.py # This runs the pipeline from start to finish
│
│   ├── utils/              # Reusable utilities
│   │   ├── datapoints_fit_in_context.py # Checks if the input fits in the context window
│   │   ├── dataset_cleaner.py 
│   │   ├── google_drive_file_finder.py        # Moves through google drive and finds a folder with a given name
│   │   ├── excel_extraction.py # Text extraction and OCR from excel files
│   │   ├── load_config.py # Loads the config file for the pipeline
│   │   ├── ocr_utils.py  # Does OCR for gathering text from files
│   │   ├── pdf_extraction.py # Does the raw text extraction for pdf files
│   │   └── pipeline_state_tracker.py # Tracks the state of each task on the pipeline
│   │
│   ├── preprocess.py       # Handles document preparation (e.g., OCR, cleaning)
│   ├── postprocess.py      # Handles formatting outputs (e.g., JSONL creation)
│   └── finetune.py         # Core logic for LLM fine-tuning
│
├── configs/                # Configuration and credential files
│   ├── config.json         # General configuration (paths, defaults, etc.)
│   ├── credentials.json    # Credentials for Google Drive or other services
│   ├── finetune_pipeline_state.json # handles the states for the pipeline
│
├── datasets/                   
│   ├── finetuning_examples/                # Raw input documents (PDFs, etc.)
│   │   ├── AI Training_install Reports.xlsx # Outputs information reviewed by people
│
├── logs/                   # Logs for debugging and usage tracking
│   ├── pipeline.log            # Centralized log file
│   ├── missing_files.txt   # Any files that couldn't be found in the google drive
│
├── .env                    # Environment variables for sensitive info
├── .gitignore              # Git ignore file
├── README.md               # Documentation for the project
└── requirements.txt        # Python dependencies
```