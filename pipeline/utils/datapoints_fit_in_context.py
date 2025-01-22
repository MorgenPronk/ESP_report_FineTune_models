from transformers import AutoTokenizer
import json

def filter_datapoints_within_context(jsonl_path, model_name):
    """
    Counts how many datapoints in a JSONL file fit within the model's context window.

    Args:
        jsonl_path (str): Path to the JSONL file containing the dataset.
        model_name (str): Name of the pre-trained model.

    Returns:
        int, int, int: The number of valid datapoints, the total number of datapoints,
                       and the context window size of the model.
    """
    # Load the tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    max_length = tokenizer.model_max_length  # Retrieve the model's context window size

    valid_count = 0
    total_count = 0

    # Iterate through the JSONL file
    with open(jsonl_path, "r") as file:
        for line in file:
            total_count += 1
            record = json.loads(line)

            # Get the text field
            text = record.get("text", "")

            # Tokenize and check token length
            tokenized_length = len(tokenizer.tokenize(text))
            if tokenized_length <= max_length:
                valid_count += 1

    return valid_count, total_count, max_length

# Example usage
if __name__ == "__main__":
    jsonl_path = "./datasets/finetuning_examples/enriched_dataset.jsonl"
    model_name = "distilgpt2"  # Replace with your model name
    valid_count, total_count, context_window = filter_datapoints_within_context(jsonl_path, model_name)
    print(f"{valid_count}/{total_count} datapoints fit within the context window ({context_window} tokens) of {model_name}.")
