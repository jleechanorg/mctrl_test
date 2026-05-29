"""Contract tests verifying slot naming conventions in tasks.md match shared_plan.md."""
import re
import os
import unittest

class TestContract(unittest.TestCase):
    """Verify all 20 merge-train slots follow the ao-slot-XX naming convention."""

    def test_all_slots_match(self):
        shared_plan_path = 'merge_train_e2e/shared_plan.md'
        tasks_path = 'merge_train_e2e/tasks.md'
        
        self.assertTrue(os.path.exists(shared_plan_path), f"{shared_plan_path} not found")
        self.assertTrue(os.path.exists(tasks_path), f"{tasks_path} not found")
            
        with open(shared_plan_path, 'r') as f:
            shared_plan_content = f.read()
            
        with open(tasks_path, 'r') as f:
            tasks_content = f.read()
            
        for i in range(1, 21):
            slot_id = f"{i:02d}"
            slot_name = f"slot-{slot_id}"
            
            # 1. Define expected completion token strictly
            # All slots use ao-slot-XX
            expected_prefix = "ao-"
            expected_token = f"complete by {expected_prefix}slot-{slot_id}"
            # 2. Check tasks.md for the correct contract spec

            # We use \b to ensure no trailing characters (like slot-010 matching slot-01)
            # We strictly enforce the expected prefix (no optional (ao-)?)
            task_pattern = (
                rf"## {slot_name} task.*?"
                rf"- heading: ## {slot_name}\n"
                rf"- required edit: replace `status: pending` with\n\s+"
                rf"`status: ({expected_token})\b`"
            )
            task_match = re.search(task_pattern, tasks_content, re.DOTALL)
            self.assertIsNotNone(task_match, f"{slot_name} task not found or invalid required edit in tasks.md (expected: {expected_token})")
            
            # 3. Check shared_plan.md status
            # It can be 'pending' OR the expected token.
            # If it's 'complete by ...', it must match expected_token exactly.
            sp_status_pattern = rf"## {slot_name}\nstatus: (pending|complete by [^\n]+)"
            sp_match = re.search(sp_status_pattern, shared_plan_content)
            self.assertIsNotNone(sp_match, f"{slot_name} heading or status line not found in shared_plan.md")
            
            sp_status = sp_match.group(1).strip()
            if sp_status != "pending":
                # Ensure it matches expected_token exactly (no extra chars at end of line)
                self.assertEqual(
                    sp_status, 
                    expected_token, 
                    f"Mismatch for {slot_name} in shared_plan.md: expected '{expected_token}', found '{sp_status}'"
                )

if __name__ == "__main__":
    unittest.main()
