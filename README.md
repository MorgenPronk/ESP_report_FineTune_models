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

