import json
from pathlib import Path
from pipeline.utils.pipeline_state_tracker import (
    load_state,
    save_state,
    update_state,
    check_step_completed,
)

TEST_STATE_FILE = Path("./configs/test_pipeline_state.json")

def setup_function():
    """
    Set up a clean test state file before each test.
    """
    state = {
        "scrape": "pending",
        "download": "pending",
        "finetune": "pending",
        "preview": "pending",
    }
    with open(TEST_STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

def teardown_function():
    """
    Clean up the test state file after each test.
    """
    if TEST_STATE_FILE.exists():
        TEST_STATE_FILE.unlink()

def test_load_state():
    state = load_state()
    assert state["scrape"] == "pending"

def test_update_state():
    update_state("scrape", "completed")
    state = load_state()
    assert state["scrape"] == "completed"

def test_check_step_completed():
    update_state("scrape", "completed")
    assert check_step_completed("scrape") is True
    assert check_step_completed("download") is False
