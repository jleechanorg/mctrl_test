import os
import pytest

def test_slot_09_is_ao_complete():
    """
    Verify that slot-09 in shared_plan.md is marked as 'complete by ao-slot-09'.
    This is the target state for PR #390.
    """
    plan_path = "merge_train_e2e/shared_plan.md"
    assert os.path.exists(plan_path), f"{plan_path} does not exist"
    
    with open(plan_path, "r") as f:
        content = f.read()
    
    expected_line = "status: complete by ao-slot-09"
    # Find the slot-09 section
    parts = content.split("## slot-09")
    assert len(parts) > 1, "## slot-09 heading not found"
    
    # Check if the next non-empty line after ## slot-09 contains the expected status
    slot_09_content = parts[1].split("##")[0].strip()
    assert expected_line in slot_09_content, f"Slot 09 status is wrong: {slot_09_content}"

@pytest.mark.parametrize("slot_num", [f"{i:02d}" for i in range(1, 21)])
def test_all_slots_status_complete(slot_num):
    """
    Verify that all slots from 01 to 20 are marked as complete.
    """
    plan_path = "merge_train_e2e/shared_plan.md"
    with open(plan_path, "r") as f:
        content = f.read()
    
    slot_header = f"## slot-{slot_num}"
    expected_status = f"status: complete by ao-slot-{slot_num}"
    
    assert slot_header in content, f"{slot_header} not found in plan"
    
    parts = content.split(slot_header)
    slot_content = parts[1].split("##")[0].strip()
    assert expected_status in slot_content, f"Slot {slot_num} status is wrong or missing"
