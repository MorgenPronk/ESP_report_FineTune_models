import json
import logging

def filter_valid_data(input_jsonl, output_jsonl):
    """
    Filters out entries with text set to 'File not found' from the input JSONL file.

    Args:
        input_jsonl (str): Path to the input JSONL file.
        output_jsonl (str): Path to save the filtered JSONL file.

    Returns:
        int: The number of valid entries written to the output file.
    """
    logger = logging.getLogger(__name__)
    valid_count = 0

    with open(input_jsonl, "r") as infile, open(output_jsonl, "w") as outfile:
        for line in infile:
            record = json.loads(line)
            if record.get("text", "").strip() != "File not found":
                json.dump(record, outfile)
                outfile.write("\n")
                valid_count += 1

    logger.info(f"Filtered data saved to: {output_jsonl}")
    logger.info(f"Total valid records: {valid_count}")
    return valid_count
