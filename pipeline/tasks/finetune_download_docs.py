# from pipeline.utils.pipeline_state_tracker import check_step_completed, update_state
# from google_drive_file_finder import authenticate_google_drive, download_files_from_list
#
# def finetune_download_docs(jsonl_path, download_folder, google_drive_folder_id):
#     if check_step_completed("download_docs"):
#         print("Download step already completed. Skipping...")
#         return
#
#     print(f"Downloading documents listed in {jsonl_path} to {download_folder}...")
#     service = authenticate_google_drive({})
#     file_names = get_file_names_from_jsonl(jsonl_path)
#
#     download_files_from_list(
#         service=service,
#         folder_id=google_drive_folder_id,
#         file_names=file_names,
#         download_folder=download_folder,
#         exact_match=True,
#         list_findable=True
#     )
#     update_state("download_docs", "completed")
#     print("Download documents step completed.")
#
# def get_file_names_from_jsonl(jsonl_path):
#     with open(jsonl_path, "r") as file:
#         return [json.loads(line)["document"] for line in file if "document" in json.loads(line)]
#

### DUMMY IMPLIMENTATION FOR TESTING
from pipeline.utils.pipeline_state_tracker import check_step_completed, update_state

def finetune_download_docs(jsonl_path, download_folder, google_drive_folder_id):
    if check_step_completed("download_docs"):
        print("Download step already completed. Skipping...")
        return

    print(f"Dummy: Simulating downloading documents from {jsonl_path} to {download_folder}...")
    update_state("download_docs", "completed")
    print("Download documents step completed.")


