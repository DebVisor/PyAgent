#!/usr/bin/env python3
"""Tests for CI workflow."""

from pathlib import Path

import yaml


def test_ci_runs_pytest() -> None:
    """The CI workflow should include a step that runs pytest."""
    with open(".github/workflows/ci.yml", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    steps = data["jobs"]["test"]["steps"]
    assert any("pytest" in (step.get("run") or "") for step in steps)


def test_ci_does_not_run_shared_precommit_profile() -> None:
    """The CI workflow should not duplicate the local-only shared precommit profile."""
    with open(".github/workflows/ci.yml", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    steps = data["jobs"]["test"]["steps"]
    assert not any("python scripts/ci/run_checks.py --profile precommit" in (step.get("run") or "") for step in steps)


def test_setup_md_has_local_testing_section() -> None:
    """docs/setup.md must have a Local Testing section documenting pre-commit + pytest."""
    content = Path("docs/setup.md").read_text(encoding="utf-8")
    assert "## Local Testing" in content, (
        "docs/setup.md must contain a '## Local Testing' section that documents "
        "how to run pre-commit and pytest locally (prj0000075 AC-05)"
    )


def test_ci_has_mypy_strict_lane_blocking_step() -> None:
    """CI must contain a strict-lane mypy command.

    Returns:
        None.

    """
    with open(".github/workflows/ci.yml", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    steps = data["jobs"]["test"]["steps"]
    expected_command = "python -m mypy --config-file mypy-strict-lane.ini"
    assert any(expected_command in (step.get("run") or "") for step in steps), (
        "CI must include a strict-lane mypy run command: python -m mypy --config-file mypy-strict-lane.ini"
    )


def test_ci_mypy_strict_lane_step_is_blocking() -> None:
    """CI strict-lane mypy command must not be softened by skip/continue patterns.

    Returns:
        None.

    """
    with open(".github/workflows/ci.yml", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    steps = data["jobs"]["test"]["steps"]
    strict_steps = [step for step in steps if "mypy-strict-lane.ini" in (step.get("run") or "")]
    assert strict_steps, "Expected at least one CI step that runs mypy with mypy-strict-lane.ini."

    for step in strict_steps:
        run_cmd = step.get("run") or ""
        assert "|| true" not in run_cmd and "||true" not in run_cmd, (
            "Strict-lane mypy CI command must be blocking; soft-fail operator found."
        )
        assert "continue-on-error" not in step, "Strict-lane mypy CI step must not set continue-on-error."
        assert "set +e" not in run_cmd, "Strict-lane mypy CI step must not disable fail-fast semantics."
