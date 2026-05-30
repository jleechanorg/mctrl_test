from merge_train_demo.multi_func import alpha, beta, gamma, delta

def test_alpha():
    assert alpha(2) == 4

def test_beta():
    assert beta(3) == 9

def test_gamma():
    assert gamma(2) == 8

def test_delta():
    assert delta(5) == -6
    doc = delta.__doc__ or ""
    assert "negated" not in doc, f"Docstring still contains outdated term: {doc}"
