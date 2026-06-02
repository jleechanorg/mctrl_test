import os
import re

def test_ci_workflow_triggers_on_all_pull_requests():
    ci_yml_path = os.path.join(os.path.dirname(__file__), ".github", "workflows", "ci.yml")
    assert os.path.exists(ci_yml_path), "ci.yml does not exist"
    
    with open(ci_yml_path, "r") as f:
        content = f.read()
        
    # Find pull_request trigger block
    pr_match = re.search(r"pull_request:\s*(.*?)(?=\n\S|$)", content, re.DOTALL)
    assert pr_match is not None, "pull_request trigger not found in ci.yml"
    
    pr_config = pr_match.group(1).strip()
    
    # Assert that no branch restrictions exist in the pull_request block
    assert "branches" not in pr_config, f"pull_request trigger restricts branches: {pr_config}"
