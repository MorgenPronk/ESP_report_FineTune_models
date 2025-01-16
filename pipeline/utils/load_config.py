import os
import json

def load_config(config_path):
    """
    Loads and validates the configuration file, resolving relative paths to absolute paths.

    Args:
        config_path (str): Path to the configuration file.

    Returns:
        dict: Parsed and resolved configuration dictionary.
    """
    with open(config_path, "r") as file:
        config = json.load(file)

    # Resolve relative paths to absolute paths
    for key, path in config.get("file_paths", {}).items():
        config["file_paths"][key] = os.path.abspath(path)

    return config

def validate_config(config, required_keys):
    """
    Validates that required keys are present in the configuration.

    Args:
        config (dict): Configuration dictionary.
        required_keys (list): List of required keys to validate.

    Raises:
        KeyError: If any required key is missing.
    """
    for key in required_keys:
        if key not in config:
            raise KeyError(f"Missing required key in config: {key}")
