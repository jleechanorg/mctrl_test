import re
import os
import unittest

class TestContract(unittest.TestCase):
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
            
            # Check shared_plan.md
            sp_match = re.search(rf"## {slot_name}\nstatus: (complete by (ao-)?slot-{slot_id})", shared_plan_content)
            self.assertIsNotNone(sp_match, f"{slot_name} not found or invalid status in shared_plan.md")
            
            sp_status = sp_match.group(1)
            
            # Check tasks.md
            # Heading: ## slot-XX task
            # Required edit: replace `status: pending` with `status: XXX`
            task_pattern = rf"## {slot_name} task.*?- heading: ## {slot_name}\n- required edit: replace `status: pending` with\n\s+`(status: (complete by (ao-)?slot-{slot_id}))`"
            task_match = re.search(task_pattern, tasks_content, re.DOTALL)
            
            self.assertIsNotNone(task_match, f"{slot_name} task not found or invalid required edit in tasks.md")
                
            task_status = task_match.group(2)
            
            self.assertEqual(sp_status, task_status, f"Mismatch for {slot_name}: shared_plan='{sp_status}', tasks='{task_status}'")

if __name__ == "__main__":
    unittest.main()
