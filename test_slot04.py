import re
import os

def test_slot_04_verification_comment():
    shared_plan_path = 'merge_train_e2e/shared_plan.md'
    assert os.path.exists(shared_plan_path)
    
    with open(shared_plan_path, 'r') as f:
        content = f.read()
        
    # Check that ## slot-04 section contains our verified comment
    pattern = r"## slot-04\nstatus: complete by ao-slot-04\n<!-- verified by antigravity -->"
    assert re.search(pattern, content) is not None
