from pipeline.utils.pipeline_state_tracker import check_step_completed, update_state

def scrape_documents(input_path, output_path):
    """
    Dummy function for document scraping.
    """
    if check_step_completed("scrape"):
        print("Scrape step already completed. Skipping...")
        return

    print(f"Scraping documents from {input_path} and saving to {output_path}...")
    # Simulate task completion
    update_state("scrape", "completed")
    print("Scrape step completed.")
