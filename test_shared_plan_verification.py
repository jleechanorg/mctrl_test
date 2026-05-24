import os

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
