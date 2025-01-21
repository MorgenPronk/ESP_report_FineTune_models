# # from pipeline.utils.pipeline_state_tracker import check_step_completed, update_state
# # from excel_to_jsonl import excel_to_jsonl as convert_excel_to_jsonl
# #
# # def finetune_excel_to_jsonl(input_excel_path, output_jsonl_path):
# #     if check_step_completed("excel_to_jsonl"):
# #         print("Excel to JSONL step already completed. Skipping...")
# #         return
# #
# #     print(f"Converting Excel file {input_excel_path} to JSONL at {output_jsonl_path}...")
# #     convert_excel_to_jsonl(input_excel_path, output_jsonl_path)
# #     update_state("excel_to_jsonl", "completed")
# #     print("Excel to JSONL step completed.")
#
#
# ### DUMMY IMPLIMENTATION FOR TESTING
# from pipeline.utils.pipeline_state_tracker import check_step_completed, update_state
#
# def finetune_excel_to_jsonl(input_excel_path, output_jsonl_path):
#     if check_step_completed("excel_to_jsonl"):
#         print("Excel to JSONL step already completed. Skipping...")
#         return
#
#     print(f"Dummy: Simulating conversion of {input_excel_path} to {output_jsonl_path}...")
#     update_state("excel_to_jsonl", "completed")
#     print("Excel to JSONL step completed.")

import pandas as pd
import json
import re
from pipeline.utils.pipeline_state_tracker import check_step_completed, update_state


def serialize_datetime(value):
    """
    Serializes datetime values, replacing NaT with None or a default string.

    Args:
        value (datetime): The value to serialize.

    Returns:
        str or None: The serialized value.
    """
    if pd.isna(value):  # Handle NaT or NaN
        return None
    elif isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d")
    return value


def extract_instances(row, prefix, fields):
    """
    Extract instances dynamically for components with numbered columns.

    Args:
        row (pd.Series): A row of data from the DataFrame.
        prefix (str): Column prefix (e.g., "Pump", "Motor").
        fields (list): List of subfields to extract for each instance (e.g., ["", "Series", "Stages"]).

    Returns:
        List[dict]: List of extracted instances for the component.
    """
    instances = []
    grouped_columns = {}

    # Combine all fields into a single regex pattern
    pattern = re.compile(rf"^{prefix} (\d+)(?: ({'|'.join(fields)}))?$")

    # Group columns by instance number
    for col in row.index:
        match = pattern.match(col)
        if match:
            instance_num, field = match.groups()
            # Assign "type" for empty field matches
            if not field or field.strip() == "":
                field = "type"
            grouped_columns.setdefault(instance_num, {}).update({field: row[col]})

    # Build instances from grouped columns
    for instance_num, instance_data in grouped_columns.items():
        if any(pd.notna(value) for value in instance_data.values()):  # Only include non-empty instances
            instances.append(instance_data)

    return instances


def excel_to_jsonl(input_excel_path, output_jsonl_path):
    """
    Converts an Excel file to a JSONL file for fine-tuning.

    Args:
        input_excel_path (str): Path to the input Excel file.
        output_jsonl_path (str): Path where the output JSONL file will be saved.

    Returns:
        None: The function writes a JSONL file to the specified location.
    """
    # Define the task instruction (common for all examples)
    instruction = """
    Extract the following information from the report if available:
    (Detailed instructions provided in the original script)
    """

    # Step 1: Read the Excel file
    df_temp = pd.read_excel(input_excel_path)
    dtypes = {col: str for col in df_temp.columns}
    dtypes["Install Date"] = "datetime64[ns]"
    df = pd.read_excel(input_excel_path, dtype=dtypes)

    # Initialize the output JSON list
    output_json = []

    # Iterate through the Excel rows to structure the data
    for _, row in df.iterrows():
        # Serialize datetime fields
        install_date = serialize_datetime(row["Install Date"])

        # Build the "output" section of the JSON
        output = {
            "Install Date": install_date,
            "Customer": row["Customer"],
            "Well Name": row["Well Name"],
            "API #": row["API #"],
            "Tubing Size": row["Tubing Size"],
            "Tubing Weight": row["Tubing Weight"],
            "Manufacturer": row["Manufacturer"],
            "Pumps": extract_instances(row, "Pump", fields=["", "Series", "# Stages"]),
            "Pump Tapers": extract_instances(row, "Calculated Pump Taper", ["", "Total # Stages"]),
            "Intakes/Gas Separators": extract_instances(row, "Intake/ Gas Sep", ["Series", "Model"]),
            "Seals/Protectors": extract_instances(row, "Seal/Protector", ["Series", "Model"]),
            "Motors": extract_instances(row, "Motor", ["Series", "Model", "HP", "V", "A"]),
            "Calculated": {
                "Total Horsepower": row["Calculated Total Motor HP"],
                "Total Voltage": row["Calculated Total Motor V"],
                "Total Amperage": row["Calculated Total Motor A"]
            },
            "Sensors": [
                {
                    "Series": row["Sensor Series"],
                    "Manufacturer": row["Sensor Manufacturer"],
                    "Model": row["Sensor Model"],
                    "Depth": row["Sensor Depth"]
                }
            ],
            "Cable": [
                {
                    "AWG": row["Main Cable AWG"],
                    "KV": row["Cable KV"],
                    "Profile": row["Cable Profile"]
                }
            ],
            "VSD": [
                {
                    "Manufacturer": row["VSD Manufacturer"],
                    "Type": row["VSD Type"],
                    "KVA": row["VSD KVA"],
                    "A": row["VSD A"]
                }
            ]
        }

        # Add this record to the dataset
        output_json.append({
            "instruction": instruction,
            "document": f"{row['File Name']}",
            "output": output
        })

    # Save the JSONL file
    with open(output_jsonl_path, "w") as jsonl_file:
        for entry in output_json:
            jsonl_file.write(json.dumps(entry) + "\n")

    print(f"Dataset converted and saved as '{output_jsonl_path}'")


def finetune_excel_to_jsonl(input_excel_path, output_jsonl_path):
    """
    Executes the Excel to JSONL conversion task for fine-tuning.

    Args:
        input_excel_path (str): Path to the input Excel file.
        output_jsonl_path (str): Path to save the resulting JSONL file.
    """
    if check_step_completed("excel_to_jsonl"):
        print("Excel to JSONL step already completed. Skipping...")
        return

    print(f"Converting Excel file {input_excel_path} to JSONL at {output_jsonl_path}...")
    excel_to_jsonl(input_excel_path, output_jsonl_path)
    update_state("excel_to_jsonl", "completed")
    print("Excel to JSONL step completed.")

