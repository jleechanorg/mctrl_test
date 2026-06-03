"""Tests for merge_train_demo/multi_func.py — symbol-level lock demo."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "merge_train_demo"))

from merge_train_demo.multi_func import alpha, beta, gamma, delta


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
        from merge_train_demo.multi_func import helper_a
        assert helper_a(3) == 3
        assert helper_a(0) == 0
        assert helper_a(-5) == -5

    def test_helper_b(self):
        from merge_train_demo.multi_func import helper_b
        assert helper_b(3) == 4
        assert helper_b(0) == 1
        assert helper_b(-5) == -4

    def test_helper_c(self):
        from merge_train_demo.multi_func import helper_c
        assert helper_c(3) == 2
        assert helper_c(0) == -1
        assert helper_c(-5) == -6

    def test_helper_d(self):
        from merge_train_demo.multi_func import helper_d
        assert helper_d(3) == 30
        assert helper_d(0) == 0
        assert helper_d(-5) == -50

    def test_helper_e(self):
        from merge_train_demo.multi_func import helper_e
        assert helper_e(3) == 300
        assert helper_e(0) == 0
        assert helper_e(-5) == -500

    def test_helper_f(self):
        from merge_train_demo.multi_func import helper_f
        assert helper_f(3) == 3000
        assert helper_f(0) == 0
        assert helper_f(-5) == -5000


class TestMultiFunc2:
    """Tests for the functions in multi_func_2.py."""

    def test_alpha2(self):
        from merge_train_demo.multi_func_2 import alpha2
        assert alpha2(5) == 1005
        assert alpha2(0) == 1000

    def test_beta2(self):
        from merge_train_demo.multi_func_2 import beta2
        assert beta2(5) == 2005
        assert beta2(0) == 2000

    def test_gamma2(self):
        from merge_train_demo.multi_func_2 import gamma2
        assert gamma2(5) == 3005
        assert gamma2(0) == 3000

    def test_delta2(self):
        from merge_train_demo.multi_func_2 import delta2
        assert delta2(5) == 4005
        assert delta2(0) == 4000

    def test_epsilon2(self):
        from merge_train_demo.multi_func_2 import epsilon2
        assert epsilon2(5) == 5005
        assert epsilon2(0) == 5000

    def test_zeta2(self):
        from merge_train_demo.multi_func_2 import zeta2
        assert zeta2(5) == 6005
        assert zeta2(0) == 6000


class TestCodeQuality:
    """Verifies PEP 8 and quality constraints on the source files."""

    def test_imports_at_top_of_file(self):
        import ast
        
        for name in ["multi_func.py", "multi_func_2.py"]:
            file_path = os.path.join(os.path.dirname(__file__), "merge_train_demo", name)
            with open(file_path, "r") as f:
                tree = ast.parse(f.read())
                
            seen_function = False
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    seen_function = True
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    assert not seen_function, f"Import statement found after a function definition in {name} at line {node.lineno}"

    def test_docstrings_contain_symbol_level_demo_phrase(self):
        # Every demo module docstring must contain the phrase "symbol-level lock demo"
        import ast
        for name in ["multi_func.py", "multi_func_2.py"]:
            file_path = os.path.join(os.path.dirname(__file__), "merge_train_demo", name)
            with open(file_path, "r") as f:
                content = f.read()
            tree = ast.parse(content)
            docstring = ast.get_docstring(tree)
            assert docstring and "symbol-level lock demo" in docstring, f"{name} docstring is missing required phrase 'symbol-level lock demo'"


class TestFileDomains:
    """Verifies merge_train lock log registration mapping."""

    def test_file_domains_yaml_valid(self):
        import yaml
        
        yaml_path = os.path.join(os.path.dirname(__file__), "merge_train_demo", "file_domains.yaml")
        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f)
            
        assert "domains" in data, "domains key not found in file_domains.yaml"
        domains = data["domains"]
        
        # Verify both domains are configured
        assert "demo" in domains, "demo domain missing from file_domains.yaml"
        assert "demo2" in domains, "demo2 domain missing from file_domains.yaml"
        
        # Verify paths mapping is correct
        assert "merge_train_demo/multi_func.py" in domains["demo"]["paths"]
        assert "merge_train_demo/multi_func_2.py" in domains["demo2"]["paths"]
