import json
from pathlib import Path

STATE_FILE = Path("./configs/finetune_pipeline_state.json")  # Updated location

def load_state():
    """
    Load the state from the state file.
    """
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    else:
        return {
            "scrape": "pending",
            "download": "pending",
            "finetune": "pending",
        }

def save_state(state):
    """
    Save the current state to the state file.
    """
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)  # Ensure `configs/` exists
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

def update_state(step, status):
    """
    Update the state of a specific step.
    """
    state = load_state()
    state[step] = status
    save_state(state)

def check_step_completed(step):
    """
    Check if a specific step is marked as completed.
    """
    state = load_state()
    return state.get(step) == "completed"
