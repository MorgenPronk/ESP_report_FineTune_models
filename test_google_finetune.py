import json

in_path = './datasets/finetuning_examples/vertex_dataset.jsonl'
out_path = 'datasets/finetuning_examples/gemini_dataset.json'


training_dataset = []
# Read the JSONL file and transform each record
with open(in_path, "r") as infile, open(out_path, "w") as outfile:
    for i, line in enumerate(infile):
        if i in [25, 27, 28]:
            continue
        record = json.loads(line)
        text_input = record.get("text_input", "").strip()
        # Flatten the 'output' dictionary into a string
        output = str(record.get("output",
                                "")).strip()  # "\n".join(f"{key}: {value}" for key, value in record.get("output", {}).items() if value)
        training_dataset.append({"text_input": text_input, "output": output})
        # Add only non-empty examples
    json.dump(training_dataset, outfile, indent=4)

import pipeline.tasks.google_finetune
