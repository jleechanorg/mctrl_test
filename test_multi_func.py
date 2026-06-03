"""Tests for merge_train_demo/multi_func.py — symbol-level lock demo."""

import os
import ast

from merge_train_demo.multi_func import (
    alpha,
    beta,
    gamma,
    delta,
    helper_a,
    helper_b,
    helper_c,
    helper_d,
    helper_e,
    helper_f,
)
from merge_train_demo.multi_func_2 import (
    alpha2,
    beta2,
    gamma2,
    delta2,
    epsilon2,
    zeta2,
)


class TestAlpha:
    """Worker A owns alpha — these verify baseline behavior."""

    def test_positive(self):
        assert alpha(3) == 6

    def test_zero(self):
        assert alpha(0) == 0

    def test_negative(self):
        assert alpha(-4) == -8


class TestBeta:
    """Worker B owns beta — these verify Worker B's implementation (x*x+100)."""

    def test_positive(self):
        assert beta(3) == 109

    def test_zero(self):
        assert beta(0) == 100

    def test_negative(self):
        assert beta(-3) == 109

    def test_one(self):
        assert beta(1) == 101

    def test_string_input(self):
        assert beta("3") == 109


class TestGamma:
    """Unreserved — verify baseline."""

    def test_positive(self):
        assert gamma(2) == 8

    def test_zero(self):
        assert gamma(0) == 0

    def test_negative(self):
        assert gamma(-2) == -8

    def test_one(self):
        assert gamma(1) == 1


class TestDelta:
    """Worker C2 owns delta — primary test surface for this PR."""

    def test_positive(self):
        assert delta(5) == -6

    def test_zero(self):
        assert delta(0) == -1

    def test_negative(self):
        assert delta(-5) == 4

    def test_one(self):
        assert delta(1) == -2

    def test_minus_one(self):
        assert delta(-1) == 0

    def test_large(self):
        assert delta(1000) == -1001


class TestHelpers:
    """Tests for the helper functions in multi_func.py."""

    def test_helper_a(self):
        assert helper_a(3) == 3
        assert helper_a(0) == 0
        assert helper_a(-5) == -5

    def test_helper_b(self):
        assert helper_b(3) == 4
        assert helper_b(0) == 1
        assert helper_b(-5) == -4

    def test_helper_c(self):
        assert helper_c(3) == 2
        assert helper_c(0) == -1
        assert helper_c(-5) == -6

    def test_helper_d(self):
        assert helper_d(3) == 30
        assert helper_d(0) == 0
        assert helper_d(-5) == -50

    def test_helper_e(self):
        assert helper_e(3) == 300
        assert helper_e(0) == 0
        assert helper_e(-5) == -500

    def test_helper_f(self):
        assert helper_f(3) == 3000
        assert helper_f(0) == 0
        assert helper_f(-5) == -5000


class TestMultiFunc2:
    """Tests for the functions in multi_func_2.py."""

    def test_alpha2(self):
        assert alpha2(5) == 1005
        assert alpha2(0) == 1000

    def test_beta2(self):
        assert beta2(5) == 2005
        assert beta2(0) == 2000

    def test_gamma2(self):
        assert gamma2(5) == 3005
        assert gamma2(0) == 3000

    def test_delta2(self):
        assert delta2(5) == 4005
        assert delta2(0) == 4000

    def test_epsilon2(self):
        assert epsilon2(5) == 5005
        assert epsilon2(0) == 5000

    def test_zeta2(self):
        assert zeta2(5) == 6005
        assert zeta2(0) == 6000


class TestCodeQuality:
    """Verifies PEP 8 and quality constraints on the source files."""

    def test_imports_at_top_of_file(self):
        for name in ["multi_func.py", "multi_func_2.py"]:
            file_path = os.path.join(os.path.dirname(__file__), "merge_train_demo", name)
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
                
            seen_function = False
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    seen_function = True
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    assert not seen_function, f"Import statement found after a function definition in {name} at line {node.lineno}"

    def test_docstrings_contain_symbol_level_demo_phrase(self):
        # Every demo module docstring must contain the phrase "symbol-level lock demo"
        for name in ["multi_func.py", "multi_func_2.py"]:
            file_path = os.path.join(os.path.dirname(__file__), "merge_train_demo", name)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            tree = ast.parse(content)
            docstring = ast.get_docstring(tree)
            assert docstring and "symbol-level lock demo" in docstring, f"{name} docstring is missing required phrase 'symbol-level lock demo'"


class TestFileDomains:
    """Verifies merge_train lock log registration mapping."""

    def test_file_domains_yaml_valid(self):
        yaml_path = os.path.join(os.path.dirname(__file__), "merge_train_demo", "file_domains.yaml")
        with open(yaml_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Parse a nested YAML structure using a robust indentation stack
        parsed = {}
        stack = [] # list of (indent, key)

        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            indent = len(line) - len(line.lstrip())

            # Pop off the stack all elements with indentation >= current indentation
            while stack and stack[-1][0] >= indent:
                stack.pop()

            # Parse list item
            if stripped.startswith("-"):
                val = stripped[1:].strip().strip('"').strip("'")
                if stack:
                    parent_key = stack[-1][1]
                    # Resolve path to nested container
                    parent_container = parsed
                    for _, k in stack[:-1]:
                        parent_container = parent_container[k]
                    if parent_key not in parent_container or not isinstance(parent_container[parent_key], list):
                        parent_container[parent_key] = []
                    parent_container[parent_key].append(val)
            # Parse key-value mapping
            elif ":" in stripped:
                key, val = stripped.split(":", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")

                # Resolve path to nested container
                parent_container = parsed
                for _, k in stack:
                    if k not in parent_container:
                        parent_container[k] = {}
                    parent_container = parent_container[k]

                if val:
                    parent_container[key] = val
                else:
                    parent_container[key] = {}
                stack.append((indent, key))

        # Assert domains key exists
        assert "domains" in parsed, "domains key not found in file_domains.yaml structure"

        # Assert both demo and demo2 are registered
        assert "demo" in parsed["domains"], "demo domain missing from file_domains.yaml"
        assert "demo2" in parsed["domains"], "demo2 domain missing from file_domains.yaml"

        # Deep verification of paths and owners for demo
        demo_config = parsed["domains"]["demo"]
        assert len(demo_config["paths"]) > 0, "demo domain paths list is empty"
        assert "@jleechan2015" in demo_config["owners"], "demo domain owner is incorrect"
        for path in demo_config["paths"]:
            # Verify paths referenced actually exist in the repository root
            full_path = os.path.join(os.path.dirname(__file__), path)
            assert os.path.isfile(full_path), f"File {path} registered in demo domain does not exist"

        # Deep verification of paths and owners for demo2
        demo2_config = parsed["domains"]["demo2"]
        assert len(demo2_config["paths"]) > 0, "demo2 domain paths list is empty"
        assert "@jleechan2015" in demo2_config["owners"], "demo2 domain owner is incorrect"
        for path in demo2_config["paths"]:
            # Verify paths referenced actually exist in the repository root
            full_path = os.path.join(os.path.dirname(__file__), path)
            assert os.path.isfile(full_path), f"File {path} registered in demo2 domain does not exist"
