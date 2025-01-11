from excel_to_jsonl import excel_to_jsonl

def main(config):
    input_excel_path = config["input_excel_path"]
    output_jsonl_path = config["output_jsonl_path"]
    excel_to_jsonl(input_excel_path, output_jsonl_path)

if __name__ == "__main__":
    from load_config import load_config
    config = load_config("../configs/config.json")
    main(config)
