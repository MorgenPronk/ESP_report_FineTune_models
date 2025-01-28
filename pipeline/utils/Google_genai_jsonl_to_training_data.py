## Google_genai_jsonl_to_training_data.py

import json

def transform_jsonl_to_training_data(input_jsonl_path, output_json_path):
    """
    Transforms a JSONL file into a JSON file formatted for training on Vertex AI.

    Args:
        input_jsonl_path (str): Path to the input JSONL file.
        output_json_path (str): Path to save the transformed JSON file.

    """
    training_data = []

    # Read the JSONL file and transform each record
    with open(input_jsonl_path, "r") as infile, open(output_json_path, "w") as outfile:
        for line in infile:
            record = json.loads(line)
            text_input = record.get("text", "").strip()
            # Flatten the 'output' dictionary into a string
            output = str(record.get("output", "")).strip() #"\n".join(f"{key}: {value}" for key, value in record.get("output", {}).items() if value)

            # Add only non-empty examples
            if text_input and output:
                transformed_record = {"text_input": text_input, "output": output}
                outfile.write(json.dumps(transformed_record) + "\n")

    print(f"Transformed data saved to {output_json_path}")


def truncate_long_inputs(input_file, output_file, max_length=40000):
    # Load the JSON file
    with open(input_file, 'r') as f:
        data = json.load(f)

    # Iterate through the list and truncate long text_input fields
    for i, item in enumerate(data):
        if len(item['text_input']) > max_length:
            print(f"Truncating 'text_input' in item {i} (length: {len(item['text_input'])})")
            item['text_input'] = item['text_input'][:max_length]

    # Save the modified JSON to the output file
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)

    print("Truncation complete. Saved to:", output_file)

def go_go():
    import_path = "./datasets/finetuning_examples/no_blanks_dataset.jsonl"
    output_path = "./datasets/finetuning_examples/vertex_dataset.jsonl"
    transform_jsonl_to_training_data(import_path, output_path)