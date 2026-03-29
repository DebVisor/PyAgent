# Current Memory - 0master

## Metadata
- agent: @0master
- lifecycle: OPEN -> IN_PROGRESS -> DONE|BLOCKED
- updated_at: 2026-03-29
- rollover: At new project start, append this file's entries to history.0master.memory.md in chronological order, then clear Entries.

## Entries

## 2026-03-29 — Agent workflow hardening from lessons-learned sweep

- Scope: reviewed all agent instruction files and cross-checked recurring blockers from history memory logs.
- Changes applied:
	- Raised @0master pre-delegation scorecard with two additional hard-gate categories: docs-policy readiness and pre-commit baseline readiness.
	- Upgraded @1project `<project>.git.md` template to modern Branch Plan / Scope Validation / Failure Disposition format to prevent docs-policy drift.
	- Added @7exec interruption handling rule: repeated `KeyboardInterrupt`/inconclusive full-suite runs now block handoff.
	- Added @7exec mandatory docs-policy gate before @8ql handoff.
	- Added @8ql mandatory exact failing-selector rerun evidence for blocker-remediation passes.
	- Added @9git docs-only closure preflight for repo-wide `run-precommit-checks` baseline debt visibility.
	- Added project-artifact docs-policy validation command in operational inputs for all agents (`0master`..`9git`).
- Rationale:
	- Addresses recurring failures seen in history memory: missing `## Branch Plan` in project git artifacts, inconclusive interrupted validation runs, and docs-only git closures blocked late by repo-wide pre-commit debt.
- Next actions:
	- Validate policy docs tests and architecture ADR governance tests.
	- If green, keep these rules as active hardening baseline.

## 2026-03-29 — Cross-link rollout to shared governance checklist

- Scope: created one canonical governance checklist and linked all ten agent files to consume it at task start.
- Changes applied:
	- Added `.github/agents/governance/shared-governance-checklist.md` as the shared source for branch/scope/docs-policy and handoff-evidence gates.
	- Updated `.github/agents/0master.agent.md` through `.github/agents/9git.agent.md` operational sections to read and apply the shared checklist.
- Validation:
	- `pytest tests/docs/test_agent_workflow_policy_docs.py tests/docs/test_architecture_adr_governance.py` -> `15 passed`.

## 2026-03-29 — CI shard-1 coverage gate remediation

- Trigger: GitHub Actions run 23716956870 failed at job `Run tests (shard 1/10)`, step `Coverage gate (stage 1)`.
- Root cause: gate executed only governance tests while measuring `--cov=tests`, which produced synthetic low total coverage.
- Direction accepted: switch gate to `--cov=src` and run tests that actually execute `src`.
- Change delegated to @6code:
	- `.github/workflows/ci.yml` coverage gate command updated to:
	  - `pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=40 -q`
- Validation evidence:
	- `pytest tests/structure/test_ci_yaml.py tests/ci/test_workflow_count.py -q` -> `13 passed`.
	- New gate command run locally -> `Required test coverage of 40% reached. Total coverage: 94.48%`.

