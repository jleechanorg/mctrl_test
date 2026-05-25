import os
import pytest
import re

@pytest.mark.parametrize("slot_num", [f"{i:02d}" for i in range(1, 21)])
def test_all_slots_status_complete(slot_num):
    """
    Verify that all slots from 01 to 20 are either 'pending' or marked as 'complete by ao-slot-XX'.
    This version uses strict line-matching to prevent false positives from substrings.
    """
    plan_path = "merge_train_e2e/shared_plan.md"
    assert os.path.exists(plan_path), f"{plan_path} does not exist"
    
    with open(plan_path, "r") as f:
        content = f.read()
    
    slot_header = f"## slot-{slot_num}"
    assert slot_header in content, f"{slot_header} not found in plan"
    
    # Extract the status line for this specific slot
    # We look for the line immediately following the header
    pattern = rf"## slot-{slot_num}\nstatus: ([^\n]+)"
    match = re.search(pattern, content)
    assert match, f"Could not find status line for slot-{slot_num}"
    
    status = match.group(1).strip()
    
    # Valid statuses are 'pending' or 'complete by ao-slot-XX'
    expected_complete = f"complete by ao-slot-{slot_num}"
    
    if status != "pending":
        assert status == expected_complete, f"Slot {slot_num} has invalid status: '{status}' (expected 'pending' or '{expected_complete}')"
