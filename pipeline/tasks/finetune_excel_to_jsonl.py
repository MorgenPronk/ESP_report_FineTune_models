# from pipeline.utils.pipeline_state_tracker import check_step_completed, update_state
# from excel_to_jsonl import excel_to_jsonl as convert_excel_to_jsonl
#
# def finetune_excel_to_jsonl(input_excel_path, output_jsonl_path):
#     if check_step_completed("excel_to_jsonl"):
#         print("Excel to JSONL step already completed. Skipping...")
#         return
#
#     print(f"Converting Excel file {input_excel_path} to JSONL at {output_jsonl_path}...")
#     convert_excel_to_jsonl(input_excel_path, output_jsonl_path)
#     update_state("excel_to_jsonl", "completed")
#     print("Excel to JSONL step completed.")


### DUMMY IMPLIMENTATION FOR TESTING
from pipeline.utils.pipeline_state_tracker import check_step_completed, update_state

def finetune_excel_to_jsonl(input_excel_path, output_jsonl_path):
    if check_step_completed("excel_to_jsonl"):
        print("Excel to JSONL step already completed. Skipping...")
        return

    print(f"Dummy: Simulating conversion of {input_excel_path} to {output_jsonl_path}...")
    update_state("excel_to_jsonl", "completed")
    print("Excel to JSONL step completed.")
