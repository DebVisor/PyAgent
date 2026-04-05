# Current Memory - 4plan

## Metadata
- agent: @4plan
- lifecycle: OPEN -> IN_PROGRESS -> DONE|BLOCKED
- updated_at: 2026-04-04
- rollover: At new project start, append this file's entries to history.4plan.memory.md in chronological order, then clear Entries.

## prj0000127 - mypy-strict-enforcement

| Field | Value |
|---|---|
| task_id | prj0000127-mypy-strict-enforcement |
| owner_agent | @4plan |
| source | user request + `mypy-strict-enforcement.project.md` + `mypy-strict-enforcement.think.md` + `mypy-strict-enforcement.design.md` + `mypy.ini` + `pyproject.toml` |
| created_at | 2026-04-04 |
| updated_at | 2026-04-04 |
| status | DONE |
| lifecycle | OPEN -> IN_PROGRESS -> DONE |
| chunk_boundaries | Chunk A warn-phase planning tasks `T-MYPY-001..T-MYPY-006`; Chunk B required-phase planning tasks `T-MYPY-007..T-MYPY-010` |
| acceptance_criteria_scope | Strict command contract, config authority contract, allowlist drift control, warn->required promotion threshold, rollback taxonomy checkpoints |
| dependency_order | `T-MYPY-001 || T-MYPY-002` -> `T-MYPY-003` -> `T-MYPY-004 || T-MYPY-005` -> `T-MYPY-006` -> `T-MYPY-007` -> `T-MYPY-008` -> `T-MYPY-009` -> `T-MYPY-010` |
| handoff_target | @5test |
| artifact_paths | `docs/project/prj0000127-mypy-strict-enforcement/mypy-strict-enforcement.plan.md` |
| branch | prj0000127-mypy-strict-enforcement (validated PASS before artifact writes) |
| first_red_slice | `T-MYPY-001` on `tests/docs/test_agent_workflow_policy_docs.py` with selector `python -m pytest -q tests/docs/test_agent_workflow_policy_docs.py -k "prj0000127 or mypy"` |
| validation_evidence | pending run in current session (docs policy selector) |

### Lesson Entry

| Field | Value |
|---|---|
| Pattern | Phased type-enforcement plans are most reliable when warn and required gates are modeled as separate milestones with explicit rollback checkpoints. |
| Root cause | Plans that skip mode-transition contracts tend to mix advisory and blocking behavior, creating ambiguous execution ownership between @6code and @7exec. |
| Prevention | Require per-task mode labels (RED/GREEN/EXEC), explicit promotion thresholds, and lane-level rollback criteria in the initial plan artifact. |
| First seen | 2026-04-04 |
| Seen in | prj0000127-mypy-strict-enforcement |
| Recurrence count | 1 |
| Promotion status | CANDIDATE |

## prj0000125 - llm-gateway-lessons-learned-fixes

| Field | Value |
|---|---|
| task_id | prj0000125-llm-gateway-lessons-learned-fixes |
| owner_agent | @4plan |
| source | user request + design.md (4 waves) + project.md + gateway_core.py + test_gateway_core_orchestration.py + ADR-0009 |
| created_at | 2026-04-04 |
| updated_at | 2026-04-04 |
| status | DONE |
| lifecycle | OPEN -> IN_PROGRESS -> DONE |
| chunk_boundaries | Single plan file (6 tasks total: T-LGW2-001..T-LGW2-006) |
| wave_a_tasks | T-LGW2-001 (RED: budget_denied), T-LGW2-002 (RED: provider_exception), T-LGW2-003 (RED: degraded_telemetry), T-LGW2-004 (GREEN: fail-closed handle()) |
| wave_b_tasks | T-LGW2-005 (RED: ordering skeleton), T-LGW2-006 (GREEN: event_log fixture) |
| wave_c_status | DONE — completed in commit 1c16acfde6; rg NOT_STARTED docs/project/prj0000124-llm-gateway/ returns 0 matches; ADR 0009 Part 2 present |
| wave_d_status | DONE — decision recorded in design.md; gateway_core.py snake_case COMPLIANT; no rename |
| acceptance_criteria_scope | AC-A1, AC-A2, AC-A3, AC-B1, AC-B2 (C1/C2/D1 already satisfied) |
| dependency_order | T-LGW2-001 + T-LGW2-002 + T-LGW2-003 (parallel) -> T-LGW2-004; T-LGW2-005 -> T-LGW2-006; convergence: T-LGW2-004 + T-LGW2-006 -> @7exec |
| handoff_target | @5test |
| artifact_paths | docs/project/prj0000125-llm-gateway-lessons-learned-fixes/llm-gateway-lessons-learned-fixes.plan.md |
| commit_sha | af64828b3f |
| branch | prj0000125-llm-gateway-lessons-learned-fixes (PASS) |
| governance_gate | python -m pytest -q tests/docs/test_agent_workflow_policy_docs.py -> 17 passed |
| first_red_slice | T-LGW2-001: test_budget_denied_does_not_call_provider in tests/core/gateway/test_gateway_core_orchestration.py |

### @5test Handoff Directive

Start with all 4 RED tasks in a single session (parallel-safe, independent test functions):
- T-LGW2-001: `test_budget_denied_does_not_call_provider` — budget allowed=False must block provider execution
- T-LGW2-002: `test_provider_exception_returns_failed_result` — provider raise must return failed result without propagation
- T-LGW2-003: `test_degraded_telemetry_result_still_returned` — emit_result raise must return with telemetry.degraded=True
- T-LGW2-005: `test_event_log_ordering_detects_reversed_execution` — shared event_log skeleton (stubs not yet wired, so FAILS)

All four tests must FAIL against the current gateway_core.py before handoff to @6code.



| Field | Value |
|---|---|
| task_id | prj0000124-llm-gateway |
| owner_agent | @4plan |
| source | user request + `llm-gateway.project.md` + `llm-gateway.think.md` + `llm-gateway.design.md` + ADR-0009 |
| created_at | 2026-04-04 |
| updated_at | 2026-04-04 |
| status | DONE |
| lifecycle | OPEN -> IN_PROGRESS -> DONE |
| chunk_boundaries | Phase 1 MVP tasks T-LGW-001..T-LGW-011.5 (bounded slices sized for ~10 code and ~10 test files max per sprint wave); Phase 2 hardening tasks T-LGW-012..T-LGW-015.5; Phase 3 acceleration tasks T-LGW-016..T-LGW-018 |
| acceptance_criteria_scope | AC-GW-001..AC-GW-008 mapped to explicit tasks, owners, file scopes, and deterministic commands |
| dependency_order | Phase 1 contract foundation -> phase-1 convergence -> phase-2 hardening -> phase-2 convergence -> phase-3 parity and service seam |
| handoff_target | @5test |
| artifact_paths | docs/project/prj0000124-llm-gateway/llm-gateway.plan.md |
| branch | prj0000124-llm-gateway (validated PASS before artifact writes) |
| first_red_slice | RED-SLICE-LGW-001 on `tests/core/gateway/test_gateway_core_orchestration.py` with fail-closed sequence assertions and selector `python -m pytest -q tests/core/gateway/test_gateway_core_orchestration.py -k fail_closed` |
| validation_evidence | python -m pytest -q tests/docs/test_agent_workflow_policy_docs.py -> 17 passed in 9.00s |

### Lesson Entry

| Field | Value |
|---|---|
| Pattern | Large split-plane plans stay executable when each task declares owner, explicit file list, AC mapping, and at least one deterministic selector. |
| Root cause | Placeholder plans and vague tasks create downstream ambiguity between @5test, @6code, @7exec, and @8ql gates. |
| Prevention | Enforce mandatory task schema (objective, files, owner, dependencies, validation command, AC mapping) and include explicit convergence steps for parallel-safe waves. |
| First seen | 2026-03-28 |
| Seen in | prj0000093-projectmanager-ideas-autosync; prj0000122-jwt-refresh-token-support; prj0000124-llm-gateway |
| Recurrence count | 3 |
| Promotion status | PROMOTED_TO_HARD_RULE |

## prj0000122 - jwt-refresh-token-support

| Field | Value |
|---|---|
| task_id | prj0000122-jwt-refresh-token-support |
| owner_agent | @4plan |
| source | user request + project overview + think artifact + design artifact + ADR-0008 |
| created_at | 2026-04-04 |
| updated_at | 2026-04-04 |
| status | DONE |
| lifecycle | OPEN -> IN_PROGRESS -> DONE |
| chunk_boundaries | Chunk C1 (T-JRT-001..T-JRT-006) for red contracts and bounded backend implementation; Chunk C2 (T-JRT-007..T-JRT-009) for execution, quality, and git closure |
| acceptance_criteria_scope | AC-JRT-001..AC-JRT-009 mapped to IFACE-JRT-001..IFACE-JRT-009 with explicit owners, target files, and validation commands |
| dependency_order | Parallel red wave (T-JRT-001 || T-JRT-002 || T-JRT-003) -> T-JRT-004 -> T-JRT-005 -> T-JRT-006 -> T-JRT-007 -> T-JRT-008 -> T-JRT-009 |
| handoff_target | @5test |
| artifact_paths | docs/project/prj0000122-jwt-refresh-token-support/jwt-refresh-token-support.plan.md |
| branch | prj0000122-jwt-refresh-token-support (validated PASS before artifact writes) |
| first_red_slice | T-JRT-001 only: create `tests/test_backend_refresh_sessions.py` with temp store-path fixture, bootstrap success/401, refresh success, replay 401, and no-plaintext-persistence assertions |
| validation_evidence | git branch --show-current -> prj0000122-jwt-refresh-token-support; c:/Dev/PyAgent/.venv/Scripts/python.exe -m pytest -q tests/docs/test_agent_workflow_policy_docs.py -> 17 passed in 6.41s |

### Lesson Entry

| Field | Value |
|---|---|
| Pattern | Red-wave planning is easier to hand off when parallel-safe test tasks are disjoint by file and merged through one explicit convergence artifact. |
| Root cause | Refresh-token work spans three test surfaces, and without a defined merge point the red phase can drift into overlapping ownership. |
| Prevention | Keep the first red wave file-disjoint, reserve shared artifact edits for one convergence task, and require deterministic selectors per file. |
| First seen | 2026-04-04 |
| Seen in | prj0000122-jwt-refresh-token-support |
| Recurrence count | 1 |
| Promotion status | CANDIDATE |

| Field | Value |
|---|---|
| task_id | prj0000104-idea000014-processing |
| owner_agent | @4plan |
| source | @3design |
| created_at | 2026-03-30 |
| updated_at | 2026-03-30 |
| status | DONE |
| lifecycle | OPEN -> IN_PROGRESS -> DONE |
| chunk_boundaries | Single chunk for dependency-authority and parity workflow (T001-T013) |
| acceptance_criteria_scope | AC-001..AC-007 fully mapped to tasks and commands |
| dependency_order | @5test red -> @6code green -> @7exec runtime -> @8ql quality/security -> @9git handoff |
| handoff_target | @5test |
| artifact_paths | docs/project/prj0000104-idea000014-processing/idea000014-processing.plan.md |
| branch | prj0000104-idea000014-processing (validated PASS before artifact writes) |

### Lesson Entry

| Field | Value |
|---|---|
| Pattern | Plan handoff quality improves when AC-to-task mapping and command matrix are explicitly paired with owner phases. |
| Root cause | Placeholder plan content did not provide executable downstream sequencing or gate evidence requirements. |
| Prevention | Enforce mandatory task schema (objective, target files, acceptance criteria, validation command) and explicit red/green/runtime/quality/handoff gates. |
| First seen | 2026-03-28 |
| Seen in | prj0000093-projectmanager-ideas-autosync; prj0000104-idea000014-processing |
| Recurrence count | 2 |
| Promotion status | PROMOTED_TO_HARD_RULE |

## prj0000105 - idea000016-mixin-architecture-base

| Field | Value |
|---|---|
| task_id | prj0000105-idea000016-mixin-architecture-base |
| owner_agent | @4plan |
| source | @3design |
| created_at | 2026-03-30 |
| updated_at | 2026-03-30 |
| status | DONE |
| lifecycle | OPEN -> IN_PROGRESS -> DONE |
| chunk_boundaries | Two chunks: Chunk A (T001-T006), Chunk B (T007-T013) |
| acceptance_criteria_scope | AC-MX-001..AC-MX-009 mapped to tasks, files, and commands |
| dependency_order | @5test red -> @6code green -> @7exec runtime -> @8ql quality/security -> @9git handoff |
| handoff_target | @5test |
| artifact_paths | docs/project/prj0000105-idea000016-mixin-architecture-base/idea000016-mixin-architecture-base.plan.md |
| branch | prj0000105-idea000016-mixin-architecture-base (validated PASS before and after artifact update) |

### Lesson Entry

| Field | Value |
|---|---|
| Pattern | Project policy gate evidence must be conclusive; interrupted test runs are not valid closure evidence. |
| Root cause | Initial docs policy gate command execution was interrupted, leaving inconclusive state for required governance evidence. |
| Prevention | Re-run the exact required selector immediately and record only conclusive pass/fail output in the artifact. |
| First seen | 2026-03-30 |
| Seen in | prj0000105-idea000016-mixin-architecture-base |
| Recurrence count | 1 |
| Promotion status | CANDIDATE |

## prj0000106 - idea000080-smart-prompt-routing-system

| Field | Value |
|---|---|
| task_id | prj0000106-idea000080-smart-prompt-routing-system |
| owner_agent | @4plan |
| source | @3design |
| created_at | 2026-03-30 |
| updated_at | 2026-03-30 |
| status | DONE |
| lifecycle | OPEN -> IN_PROGRESS -> DONE |
| chunk_boundaries | Two chunks: Chunk A guardrail-first routing core (T-SPR-001..T-SPR-013), Chunk B ambiguity/fallback/telemetry (T-SPR-014..T-SPR-021) |
| acceptance_criteria_scope | AC-SPR-001..AC-SPR-008 fully mapped to executable tasks and validation commands |
| dependency_order | @5test red -> @6code green -> @7exec runtime -> @8ql quality/security -> @9git handoff |
| handoff_target | @5test |
| artifact_paths | docs/project/prj0000106-idea000080-smart-prompt-routing-system/idea000080-smart-prompt-routing-system.plan.md |
| branch | prj0000106-idea000080-smart-prompt-routing-system (validated PASS before artifact writes) |
| validation_evidence | python -m pytest -q tests/docs/test_agent_workflow_policy_docs.py -> 12 passed in 1.59s |

### Lesson Entry

| Field | Value |
|---|---|
| Pattern | AC-to-task mapping quality improves when each task embeds explicit owner handoff and executable command selectors. |
| Root cause | Placeholder plans without command-level selectors create ambiguity between @5test and @6code ownership boundaries. |
| Prevention | Require per-task owner sequencing in plan phases and include deterministic command selectors per AC mapping. |
| First seen | 2026-03-30 |
| Seen in | prj0000106-idea000080-smart-prompt-routing-system |
| Recurrence count | 1 |
| Promotion status | CANDIDATE |

