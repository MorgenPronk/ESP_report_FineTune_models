import json
def load_config(config_path="../configs/config.json"): #relative to where you are running the file...
    with open(config_path, "r") as f:
        return json.load(f)