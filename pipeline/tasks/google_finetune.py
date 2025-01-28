import google.generativeai as genai
from pipeline.utils.load_config import load_config
import pandas as pd
import seaborn as sns
import time
import json

# Load configuration
config = load_config("./configs/config.json")
genai.configure(api_key=config["google_genai"]["api_key"])

# Debugging
# List existing tuned models
for model_info in genai.list_tuned_models():
    print(model_info.name)


# Truncate training data based on token limits
def truncate_long_inputs(input_path, output_path, model, max_tokens=40000):
    with open(input_path, 'r') as f:
        data = json.load(f)

    for i, item in enumerate(data):
        text_input = item['text_input']
        token_count_response = model.count_tokens(text_input)  # Returns a CountTokensResponse
        token_count = token_count_response.total_tokens  # Access the total token count

        if token_count > max_tokens:
            print(f"Example {i} exceeds token limit ({token_count} tokens). Truncating...")
            tokens = model.tokenize(text_input)  # Tokenize the text
            truncated_tokens = tokens[:max_tokens]  # Truncate tokens
            item['text_input'] = model.detokenize(truncated_tokens)  # Convert tokens back to text

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=4)

    print("Token truncation complete. Updated data saved to:", output_path)


# Format training_data
def format_training_data():
    from pipeline.utils.Google_genai_jsonl_to_training_data import transform_jsonl_to_training_data

    input_path = "./datasets/finetuning_examples/no_blanks_dataset.jsonl"
    output_path = "./datasets/finetuning_examples/vertex_dataset.jsonl"

    # Transform JSONL to training data
    transform_jsonl_to_training_data(input_path, output_path)

    # Truncate inputs based on token count
    model = genai.GenerativeModel("models/gemini-1.5-flash")
    truncate_long_inputs(output_path, output_path, model)


# Train the model

base_model = "models/gemini-1.5-flash-001-tuning"
training_data = './datasets/finetuning_examples/gemini_dataset.json'

operation = genai.create_tuned_model(
    # Note: You can indicate an already tuned model to tune further
    # Set 'source_model="tunedModels/...'
    display_name="ESP_test_2",
    source_model=base_model,
    epoch_count=300,
    batch_size=10,
    learning_rate=0.001,
    training_data=training_data,
)

for status in operation.wait_bar():
    time.sleep(10)

result = operation.result()
print(result)

# Plot the loss curve
snapshots = pd.DataFrame(result.tuning_task.snapshots)
sns.lineplot(data=snapshots, x='epoch', y='mean_loss')

model = genai.GenerativeModel(model_name=result.name)

