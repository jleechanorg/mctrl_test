import re

ALLOWED_REPOS = frozenset(["jleechanorg/jleechanclaw", "jleechanorg/worldarchitect.ai"])

_REPO_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def validate_repo_target(repo: str, allowed: frozenset = ALLOWED_REPOS) -> None:
    if not _REPO_PATTERN.fullmatch(repo):
        raise ValueError(f"Repository '{repo}' must use owner/name format")

    if repo not in allowed:
        raise ValueError(f"Repository '{repo}' is not in the allowlist")


def resolve_repo_target(repo_input: str | None, default_repo: str) -> str:
    selected_repo = default_repo if repo_input is None else repo_input
    validate_repo_target(selected_repo)
    return selected_repo
