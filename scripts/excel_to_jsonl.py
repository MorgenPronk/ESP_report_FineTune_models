##File name: finetune_excel_to_jsonl.py

import pandas as pd
import json
import re
import os

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

    Install Date
    Customer
    Well Name
    API #
    Tubing Size
    Tubing Weight
    Manufacturer

    for each pump in the report:
    - Pump type
    - Pump Series
    - Pump number of Stages

    for each pump taper in the report:
    - taper type
    - total number of Stages

    for each intake/gas separator
    - model
    - series

    for each Seal/Protector
    - series
    - model

    for each motor
    - manufacturer
    - series
    - model
    - horsepower
    - voltage
    - amperage

    calculated total horsepower
    calculated total voltage
    calculated total amperage

    sensor series
    sensor manufacturer
    sensor model
    sensor depth

    main cable AWG
    Cable KV
    Cable Profile

    VSD Manufacturer
    VSD Type
    VSD KVA
    VSD A
    """

    # Step 1: Read the Excel file
    df_temp = pd.read_excel(input_excel_path)
    dtypes = {col: str for col in df_temp.columns}
    dtypes["Install Date"] = "datetime64[ns]"
    df = pd.read_excel(input_excel_path, dtype=dtypes)

    # Initialize the output JSON list
    output_json = []

    # Function to handle datetime serialization
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

    # Function to extract instances dynamically based on column headers
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
            "Motor Manufacturer": row["Motor Manufacturer"],
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


def jsonl_to_dataframe(jsonl_file_path):
    """
    Converts a JSONL file into a pandas DataFrame with expanded fields for comparison.

    Args:
        jsonl_file_path (str): Path to the JSONL file.

    Returns:
        pd.DataFrame: A DataFrame containing the JSONL data with expanded fields.
    """
    data = []
    with open(jsonl_file_path, "r") as file:
        for line in file:
            # Parse each line as a JSON object
            obj = json.loads(line)
            output = obj.get("output", {})

            # Expand lists of dictionaries into separate fields
            expanded = {}
            for key, value in output.items():
                if isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            for subkey, subvalue in item.items():
                                expanded[f"{key}_{i+1}_{subkey}"] = subvalue
                        else:
                            expanded[f"{key}_{i+1}"] = item
                else:
                    expanded[key] = value

            flat_obj = {
                "instruction": obj.get("instruction"),
                "document": obj.get("document"),
                **expanded
            }
            data.append(flat_obj)

    return pd.DataFrame(data)


def compare_dataframes(original_df, converted_df, save_folder):
    """
    Compares two DataFrames, prints differences, and saves all outputs to files.

    Args:
        original_df (pd.DataFrame): Original DataFrame from Excel.
        converted_df (pd.DataFrame): DataFrame converted from JSONL.
        save_folder (str): Folder where outputs (differences, DataFrames) will be saved.

    Returns:
        None: Prints the comparison results.
    """
    # Ensure the save folder exists
    os.makedirs(save_folder, exist_ok=True)

    # Align indices
    original_df = original_df.reset_index(drop=True)
    converted_df = converted_df.reset_index(drop=True)

    # Standardize column names
    original_df.columns = original_df.columns.str.strip()
    converted_df.columns = converted_df.columns.str.strip()

    # Apply column mapping to the converted DataFrame
    column_mapping = {
        "Install Date": "Install Date",
        "Customer": "Customer",
        "Well Name": "Well Name",
        "API #": "API #",
        "Tubing Size": "Tubing Size",
        "Tubing Weight": "Tubing Weight",
        "Manufacturer": "Manufacturer",
        "Pumps_1_type": "Pump 1",
        "Pumps_1_Series": "Pump 1 Series",
        "Pumps_1_# Stages": "Pump 1 # Stages",
        "Pumps_2_type": "Pump 2",
        "Pumps_2_Series": "Pump 2 Series",
        "Pumps_2_# Stages": "Pump 2 # Stages",
        "Pump Tapers_1_type": "Calculated Pump Taper 1",
        "Pump Tapers_1_Total # Stages": "Calculated Pump Taper 1 Total # Stages",
        "Pump Tapers_2_type": "Calculated Pump Taper 2",
        "Pump Tapers_2_Total # Stages": "Calculated Pump Taper 2 Total # Stages",
        "Intakes/Gas Separators_1_Series": "Intake/ Gas Sep 1 Series",
        "Intakes/Gas Separators_1_Model": "Intake/ Gas Sep 1 Model",
        "Intakes/Gas Separators_2_Series": "Intake/ Gas Sep 2 Series",
        "Intakes/Gas Separators_2_Model": "Intake/ Gas Sep 2 Model",
        "Seals/Protectors_1_Series": "Seal/Protector 1 Series",
        "Seals/Protectors_1_Model": "Seal/Protector 1 Model",
        "Motors_1_Series": "Motor 1 Series",
        "Motors_1_Model": "Motor 1 Model",
        "Motors_1_HP": "Motor 1 HP",
        "Motors_1_V": "Motor 1 V",
        "Motors_1_A": "Motor 1 A",
        "Calculated_Total Horsepower": "Calculated Total Motor HP",
        "Calculated_Total Voltage": "Calculated Total Motor V",
        "Calculated_Total Amperage": "Calculated Total Motor A",
        "Sensors_1_Series": "Sensor Series",
        "Sensors_1_Manufacturer": "Sensor Manufacturer",
        "Sensors_1_Model": "Sensor Model",
        "Sensors_1_Depth": "Sensor Depth",
        "Cable_1_AWG": "Main Cable AWG",
        "Cable_1_KV": "Cable KV",
        "Cable_1_Profile": "Cable Profile",
        "VSD_1_Manufacturer": "VSD Manufacturer",
        "VSD_1_Type": "VSD Type",
        "VSD_1_KVA": "VSD KVA",
        "VSD_1_A": "VSD A"
    }
    converted_df = converted_df.rename(columns=column_mapping)

    # Save DataFrames for inspection
    original_file = os.path.join(save_folder, "original_dataframe.pkl")
    converted_file = os.path.join(save_folder, "converted_dataframe.pkl")
    original_df.to_pickle(original_file)
    converted_df.to_pickle(converted_file)

    # Save as CSV for easier viewing
    original_csv_file = os.path.join(save_folder, "original_dataframe.csv")
    converted_csv_file = os.path.join(save_folder, "converted_dataframe.csv")
    original_df.to_csv(original_csv_file, index=False)
    converted_df.to_csv(converted_csv_file, index=False)

    print(f"Saved original DataFrame to: {original_file} and {original_csv_file}")
    print(f"Saved converted DataFrame to: {converted_file} and {converted_csv_file}")

    # Align columns
    original_columns = set(original_df.columns)
    converted_columns = set(converted_df.columns)

    # Check for missing or extra columns
    missing_in_original = converted_columns - original_columns
    missing_in_converted = original_columns - converted_columns

    if missing_in_original:
        print(f"Columns in converted DataFrame but missing in original: {missing_in_original}")
    if missing_in_converted:
        print(f"Columns in original DataFrame but missing in converted: {missing_in_converted}")

    # Retain only common columns for comparison
    common_columns = original_columns & converted_columns
    original_df = original_df[sorted(common_columns)]
    converted_df = converted_df[sorted(common_columns)]

    # Compare DataFrames
    if original_df.equals(converted_df):
        print("The DataFrames are identical!")
    else:
        print("Differences found between the DataFrames:")
        differences = original_df.compare(converted_df, align_axis=0)

        # Save differences to a file
        differences_file = os.path.join(save_folder, "differences.csv")
        differences.to_csv(differences_file)
        print(f"Saved differences to: {differences_file}")


def validate_conversion(original_excel_path, jsonl_file_path):
    """
    Validates that the JSONL conversion matches the original Excel data.

    Args:
        original_excel_path (str): Path to the original Excel file.
        jsonl_file_path (str): Path to the JSONL file.

    Returns:
        None: Prints validation results.
    """
    # Load original Excel file
    original_df = pd.read_excel(original_excel_path)

    # Convert JSONL to DataFrame
    converted_df = jsonl_to_dataframe(jsonl_file_path)

    # Extract folder path from JSONL save path
    save_folder = os.path.dirname(jsonl_file_path)

    # Compare DataFrames
    compare_dataframes(original_df, converted_df, save_folder)


if __name__ == "__main__":
    # Set the paths for excel and save
    excel_path = '../datasets/finetuning_examples/AI Training_Install Reports.xlsx'
    save_path = '../datasets/finetuning examples/finetuning_data.jsonl'
    # Do the conversion
    excel_to_jsonl(excel_path, save_path)

    # Validate the conversion
    validate_conversion(excel_path, save_path)
