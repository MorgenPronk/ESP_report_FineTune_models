import os
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, Seq2SeqTrainer, Seq2SeqTrainingArguments
from datasets import Dataset
import torch

def preprocess_data(examples, tokenizer, max_input_length=512, max_output_length=512):
    inputs = tokenizer(
        examples["input"], max_length=max_input_length, truncation=True, padding="max_length"
    )
    labels = tokenizer(
        examples["output"], max_length = max_output_length, truncation=True, padding="max_length"
    )
    input["labels"] = labels["input_ids"]
    return inputs

def fine_tune_model(config):
    """
    Fine-tunes a pre-trained Hugging Face model using the dataset in JSONL format
    :param config:
    :return:
    """
    # Load configuration
    dataset_path = config["fine_tune"]["dataset_path"]
    model_name = config["fine_tune"]["model_name"]
    output_dir = config["fine_tune"]["output_dir"]
    num_epochs = config["fine_tune"].get("num_epochs", 3)
    batch_size = config["fine_tune"].get("batch_size", 8)
    learning_rate = config["fine_tune"].get("learning_rate", 5e-5)

    # Check available hardware
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    pring(f"Using device: {device}")

    # Load dataset
    dataset = Dataset.from_json(dataset_path)
    dataset = dataset.train_test_split(test_size=0.1)
    train_dataset = dataset["train"]
    val_dataset = dataset["test"]

    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(device)

    # Preprocess datasets
    train_dataset = train_dataset.map(lambda x: preprocess_data(x, tokenizer), batched=True)
    val_dataset = val_dataset.map(lambda x: preprocess_data(x, tokenizer), batched=True)

    # Define training arguments
    training_args = Seq2SeqTrainingArguments(
        output_dir=output_dir,
        evaluation_strategy="steps",
        save_strategy="steps",
        logging_dir=os.path.join(output_dir, "logs"),
        learning_rate=learning_rate,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        num_train_epochs=num_epochs,
        predict_with_generate=True,
        fp16=torch.cuda.is_available(),
        save_total_limit=3,
    )

    # Initialize the trainer
    trainer = Seq2SeqTrainer(
        model = model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        tokenizer=tokenizer,
    )

    # Fine-tune the model
    print("Starting fine-tuning...")
    trainer.train()

    # Save the fine-tuned model
    print("Saving fine-tuned model...")
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)

    print(f"Model saved to {output_dir}")

def main(config):
    """
    Entry point for the fine-tuning step in the pipeline
    :param config:
    :return:
    """

    fine_tune_model(config)

