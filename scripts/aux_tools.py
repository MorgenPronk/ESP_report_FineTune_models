##File name: aux_tools.py

import json
import os
import re
import pandas as pd
import scripts.google_drive_file_finder as google_find
from scripts.load_config import load_config

def sanitize_filename(filename):
    """Sanitize the filename by removing or replacing problematic characters."""
    # Remove leading/trailing spaces
    filename = filename.strip()
    # Replace any kind of whitespace with underscores
    filename = re.sub(r'\s+', '_', filename)
    # Replace problematic characters with underscores or remove them
    filename = re.sub(r'[<>:"/\\|?*#]', '_', filename)  # Replace with underscore
    filename = re.sub(r'[()\[\]{}]', '', filename)  # Remove parentheses, brackets
    return filename

def excel_2_dataframe(file_path):

    df = pd.read_excel(file_path)

    return df

def excel_name_sanitize(file_path):

    df = pd.read_excel(file_path)
    df['sanitized file name'] = df['File Name'].apply(sanitize_filename)

    return df

def filename_check(names_to_check, dir_path):

    # Index all files in the directory into a set
    directory_files = set(os.listdir(dir_path))


    # Find which files exist and which are missing
    names_to_check = set(names_to_check)

    missing_files = names_to_check.difference(directory_files)

    return missing_files

def full_file_name_check(excel_file_path, doc_txt_dir_path):

    df = excel_name_sanitize(excel_file_path)
    names_to_check = df['sanitized file name']

    missing_files = filename_check(names_to_check, doc_txt_dir_path)

    return missing_files

def current_missing_files():
    excel_file_path = './datasets/AI Training_Install Reports.xlsx'
    doc_txt_dif_path= './datasets/Endeavor_ESP_reports_txt'
    missing = full_file_name_check(excel_file_path, doc_txt_dif_path)
    return missing

def download_fine_tuning_files(config_path, finetune_xls_file_path, download_folder, exact_match):
    df_finetune = pd.read_excel(finetune_xls_file_path)
    finetune_filenames = df_finetune["File Name"] #TODO: This is going to be an easy point of failure. The column might not be called this in the future
    config = load_config(config_path)
    service = google_find.authenticate_google_drive(config)
    # Replace with your Google Drive folder ID
    folder_id = '1XvHukPiinuqxDUthxJRQ0zTNY5ESUupq' # This is the "Install Report" folder
    # Search and download the files (with exact match or partial match as needed)
    google_find.download_files_from_list(service, folder_id, finetune_filenames, download_folder, exact_match)


if __name__ == '__main__':
    config_path = '../configs/config.json'
    CREDS_FILE = '../configs/credentials.json'
    xls_file = '../datasets/finetuning_examples/AI Training_Install Reports.xlsx'
    download_path = '../datasets/google_downloads'
    google_find = download_fine_tuning_files(config_path, xls_file, download_path, True)