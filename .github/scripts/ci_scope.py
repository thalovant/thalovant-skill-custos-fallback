"""Keep checks visible while avoiding test installs for prose-only changes.

Unknown events, missing history, and changes outside the allowlist run all tests.
Package jobs always run separately, because README changes affect distributions.
"""
import json
import os
import subprocess
from pathlib import Path, PurePosixPath


def prose_only(paths):
    return bool(paths) and all(
        path in {"README.md", "REFERENCE.md", "CHANGELOG.md"}
        or (PurePosixPath(path).parts[0] == "docs" and path.endswith(".md"))
        for path in paths
    )


def should_test(event_name, event):
    if event_name == "pull_request":
        # checkout uses GitHub's test merge; its first parent is the base branch.
        base = "HEAD^1"
    elif event_name == "push":
        base = event.get("before", "")
        if not base or set(base) == {"0"}:
            return True
    else:
        return True
    result = subprocess.run(
        ["git", "diff", "--name-only", "--no-renames", "-z", base, "HEAD", "--"],
        capture_output=True, check=False,
    )
    if result.returncode:
        return True
    paths = [p for p in result.stdout.decode("utf-8", errors="replace").split("\0") if p]
    return not prose_only(paths)


if __name__ == "__main__":
    try:
        event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
        run = should_test(os.environ.get("GITHUB_EVENT_NAME", ""), event)
    except (OSError, ValueError, KeyError, TypeError):
        run = True
    with open(os.environ["GITHUB_OUTPUT"], "a") as output:
        output.write(f"run_tests={str(run).lower()}\n")
    print("Run full checks" if run else "Prose-only change: package checks still run")
