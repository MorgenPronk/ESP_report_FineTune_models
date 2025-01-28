## finetune_model.py

import os
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True" # help manage memory fragmentation
import json
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments
import datasets
import torch

print(f'GPU available: {torch.cuda.is_available()}')
# Helper function to flatten JSON object to text
def flatten_json_to_text(json_obj):
    """
    Flattens a JSON object into a plain text representation.

    Args:
        json_obj (dict): The JSON object to flatten.

    Returns:
        str: Flattened JSON object as a text string.
    """
    return "\n".join(f"{key}: {value}" for key, value in json_obj.items() if value)

# Fine-Tune Base Model
def finetune_base_model(model_name, dataset_path, output_dir, num_epochs=3, batch_size=8, learning_rate=5e-5, eval_split=0.1):
    # Load and preprocess dataset
    data = []
    with open(dataset_path, "r") as file:
        for line in file:
            record = json.loads(line)
            input_text = record.get("text", "").strip()
            output_text = flatten_json_to_text(record.get("output", {}))
            if input_text and output_text:  # Ensure both fields are non-empty
                data.append({"input": input_text, "output": output_text})

    dataset = datasets.Dataset.from_list(data)
    train_dataset, eval_dataset = dataset.train_test_split(test_size=eval_split).values()

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    # Assign a padding token if not already defined
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Move the model to GPU if available
    if torch.cuda.is_available():
        model = model.cuda()

    # Tokenizer preprocessing function
    def preprocess(examples):
        inputs = examples["input"]
        targets = examples["output"]
        model_inputs = tokenizer(inputs, truncation=True, padding="max_length", max_length=512)
        labels = tokenizer(targets, truncation=True, padding="max_length", max_length=512).input_ids
        model_inputs["labels"] = labels
        return model_inputs

    tokenized_train = train_dataset.map(preprocess, batched=True)
    tokenized_eval = eval_dataset.map(preprocess, batched=True)

    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=num_epochs,
        per_device_train_batch_size=batch_size,
        learning_rate=learning_rate,
        evaluation_strategy="steps",
        eval_steps=50,
        save_steps=50,
        logging_dir="./logs",
        logging_steps=100,
        log_level="debug",
        no_cuda=False,
        # fp16=True, # Enable mixed percision training
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_eval,
        tokenizer=tokenizer,
    )

    trainer.train()
    trainer.save_model(output_dir)
    print(f"Model fine-tuned and saved at {output_dir}")

# Fine-Tune Instruction Model
def finetune_instruct_model(model_name, dataset_path, output_dir, num_epochs=3, batch_size=8, learning_rate=5e-5, eval_split=0.1):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Load and preprocess dataset
    data = []
    with open(dataset_path, "r") as file:
        for line in file:
            record = json.loads(line)
            instruction = record.get("instruction", "").strip()
            input_text = record.get("text", "").strip()
            combined_input = f"{instruction}\n\n{input_text}" if instruction else input_text
            output_text = flatten_json_to_text(record.get("output", {}))
            if combined_input and output_text:  # Ensure both fields are non-empty
                data.append({"input": combined_input, "output": output_text})

    dataset = datasets.Dataset.from_list(data)
    train_dataset, eval_dataset = dataset.train_test_split(test_size=eval_split).values()

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    # Assign a padding token if not already defined
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Move the model to GPU if available
    if torch.cuda.is_available():
        model = model.cuda()

    # Tokenizer preprocessing function
    def preprocess(examples):
        inputs = examples["input"]
        targets = examples["output"]
        model_inputs = tokenizer(inputs, truncation=True, padding="max_length", max_length=512)
        labels = tokenizer(targets, truncation=True, padding="max_length", max_length=512).input_ids
        model_inputs["labels"] = labels
        return model_inputs

    tokenized_train = train_dataset.map(preprocess, batched=True)
    tokenized_eval = eval_dataset.map(preprocess, batched=True)

    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=num_epochs,
        per_device_train_batch_size=batch_size,
        learning_rate=learning_rate,
        evaluation_strategy="steps",
        eval_steps=50,
        save_steps=50,
        logging_dir="./logs",
        logging_steps=100,
        log_level="debug",
        no_cuda=False,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_eval,
        tokenizer=tokenizer,
    )

    trainer.train()
    trainer.save_model(output_dir)
    print(f"Model fine-tuned and saved at {output_dir}")
