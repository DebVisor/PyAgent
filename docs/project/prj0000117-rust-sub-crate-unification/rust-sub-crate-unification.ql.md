# rust-sub-crate-unification - Quality & Security Review

_Agent: @8ql | Date: 2026-04-03 | Branch: prj0000117-rust-sub-crate-unification_
_Status: BLOCKED_

## Scope
| File | Change type |
|------|-------------|
| tests/rust/test_workspace_unification_contracts.py | Validated |
| tests/ci/test_ci_workspace_unification_contracts.py | Validated |
| tests/ci/test_ci_workflow.py | Validated |
| tests/docs/test_agent_workflow_policy_docs.py | Baseline validated |
| .github/workflows/ci.yml | Security sanity reviewed |
| rust_core/src/hardware.rs | Security/quality finding surfaced by clippy |

## Part A - Security Findings
| ID | Severity | File | Line | Rule | Description |
|----|----------|------|------|------|-------------|
| QL-117-001 | MEDIUM | rust_core/src/hardware.rs | 71 | clippy -D warnings | `AMD_NPU_STATUS_UNAVAILABLE` dead code fails `cargo clippy -p rust_core --all-features -- -D warnings`. |
| QL-117-002 | MEDIUM | rust_core/Cargo.toml | 1 | workspace package resolution | `cargo clippy -p pyagent-crdt --all-features -- -D warnings` returned `cannot specify features for packages outside of workspace`. |

## Part B - Quality Gaps
| # | Type | Description | Responsible agent | Blocking? |
|---|------|-------------|-------------------|-----------|
| 1 | Rust lint gate | rust_core clippy check failed due to dead code warning elevated to error. | @6code | YES |
| 2 | Rust workspace contract | pyagent-crdt clippy command cannot resolve package in current workspace context. | @6code | YES |
| 3 | Docs baseline | `tests/docs/test_agent_workflow_policy_docs.py` has known legacy missing file (`prj0000005`) unrelated to project scope. | BASELINE_QUALITY_DEBT | NO |

## Part C - Lessons Written
| Pattern | Agent memory file | Recurrence | Promoted to agent rule? |
|---------|------------------|-----------|------------------------|
| Rust gate commands must map to actual workspace package names before final gate. | .github/agents/data/current.8ql.memory.md | 1 | No (CANDIDATE) |

## OWASP Coverage
| Category | Status | Notes |
|----------|--------|-------|
| A01 Broken Access Control | PASS | No permission broadening; `contents: read` only in CI workflow. |
| A03 Injection | PASS | No unsafe workflow context interpolation in `run:` steps observed. |
| A05 Security Misconfiguration | PASS | No `pull_request_target`; workflow scope remains lightweight and least-privilege. |
| A06 Vulnerable and Outdated Components | PASS | No new dependency audit delta requested in this gate. |
| A08 Software and Data Integrity Failures | PASS | No unexpected third-party action changes observed in reviewed workflow. |

## Evidence
- `git branch --show-current` -> `prj0000117-rust-sub-crate-unification`
- `git pull` -> `Already up to date.`
- `python -m pytest -q tests/rust/test_workspace_unification_contracts.py tests/ci/test_ci_workspace_unification_contracts.py tests/ci/test_ci_workflow.py` -> `15 passed`
- `python -m pytest -q tests/docs/test_agent_workflow_policy_docs.py` -> `1 failed, 16 passed` (known baseline legacy file missing)
- `ruff check tests/rust/test_workspace_unification_contracts.py tests/ci/test_ci_workspace_unification_contracts.py tests/ci/test_ci_workflow.py` -> `All checks passed!`
- `cargo clippy -p rust_core --all-features -- -D warnings` -> FAILED (`dead_code` at `rust_core/src/hardware.rs:71`)
- `cargo clippy -p pyagent-crdt --all-features -- -D warnings` -> FAILED (`cannot specify features for packages outside of workspace`)
- `.github/workflows/ci.yml` sanity -> explicit `permissions: contents: read`; single rust benchmark smoke step present; no unexpected broadening.

## Verdict
| Gate | Status |
|------|--------|
| Security (workflow sanity + scoped lint gates) | ❌ FAIL |
| Plan vs delivery | ✅ PASS |
| AC vs test coverage | ✅ PASS |
| Docs vs implementation | ✅ PASS (known baseline exception) |
| **Overall** | **BLOCKED -> @6code** |
