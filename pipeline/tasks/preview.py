from pipeline.utils.pipeline_state_tracker import check_step_completed, update_state

def preview_document(file_path):
    """
    Dummy function for document preview.
    """
    if check_step_completed("preview"):
        print("Preview step already completed. Skipping...")
        return

    print(f"Previewing document: {file_path}...")
    # Simulate task completion
    update_state("preview", "completed")
    print("Preview step completed.")
