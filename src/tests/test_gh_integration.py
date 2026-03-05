import pytest

from src.orchestration.gh_integration import (
    ALLOWED_REPOS,
    resolve_repo_target,
    validate_repo_target,
)


def test_validate_repo_target_blocks_unknown_repo() -> None:
    with pytest.raises(ValueError, match="allowlist"):
        validate_repo_target("example/unknown-repo")


def test_resolve_repo_target_uses_default_on_none() -> None:
    assert resolve_repo_target(None, "jleechanorg/jleechanclaw") == "jleechanorg/jleechanclaw"


def test_resolve_repo_target_raises_on_unknown_default() -> None:
    with pytest.raises(ValueError, match="allowlist"):
        resolve_repo_target(None, "example/not-allowed")


def test_validate_repo_target_enforces_owner_name_format() -> None:
    with pytest.raises(ValueError, match="owner/name"):
        validate_repo_target("badformat")


def test_allowed_repos_are_expected() -> None:
    assert ALLOWED_REPOS == frozenset(
        ["jleechanorg/jleechanclaw", "jleechanorg/worldarchitect.ai"]
    )
