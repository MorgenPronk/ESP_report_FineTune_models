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
## Run scrape
python docflow.py scrape --input-path ./data/raw --output-path ./data/processed

## Run fine-tune
python docflow.py finetune --excel-path ./configs/training_data.xlsx --output-path ./data/training

## Run download
python docflow.py download --folder-id <FOLDER_ID> --local-path ./data/downloads


# Intended file structure

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
