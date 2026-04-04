# llm-gateway-lessons-learned-fixes - Options

_Status: DONE_
_Analyst: @2think | Updated: 2026-04-04_

## Root Cause Analysis
1. The merged phase-one slice in `src/core/gateway/gateway_core.py` is intentionally narrow, but it still leaves three documented runtime hardening gaps unresolved: budget-denied fail-closed handling before provider execution, deterministic budget failure commit on provider/runtime exceptions, and degraded-telemetry handling when emitters fail.
2. `tests/core/gateway/test_gateway_core_orchestration.py` still proves call order by concatenating two independent stub call lists, which does not preserve real chronology and can validate the wrong interleaving.
3. Source-project artifacts under `docs/project/prj0000124-llm-gateway/` drift from the merged implementation state: the canonical overview still reports `Lane: Discovery` and all milestones as `NOT_STARTED` even though downstream artifacts are `DONE` and PR #287 was opened.
4. Naming guidance is inconsistent across repository guidance sources: `docs/project/naming_standards.md` requires strict `snake_case`, while attached Copilot instructions still mention PascalCase module filenames. The live gateway files (`src/core/gateway/gateway_core.py`, `tests/core/gateway/test_gateway_core.py`) already follow `snake_case`, so this follow-up should treat naming as a governance decision unless a broader rename project is explicitly opened.

## Context Map
### Files Already Showing The Problem
| File | Why it matters | Observed issue |
|---|---|---|
| `src/core/gateway/gateway_core.py` | Runtime orchestration entrypoint | No explicit reserve-result deny handling, no provider-exception fail-closed commit path, no degraded-telemetry protection |
| `tests/core/gateway/test_gateway_core_orchestration.py` | Primary correctness contract | Ordering assertion derives chronology from separate lists instead of one shared event log |
| `docs/project/prj0000124-llm-gateway/llm-gateway.project.md` | Canonical project state source | Milestones and lane still show initialization state instead of merged green state |
| `docs/project/prj0000124-llm-gateway/llm-gateway.design.md` | Design source of truth | Documents degraded-telemetry contract that code does not yet fully honor |
| `docs/architecture/adr/0009-llm-gateway-hybrid-split-plane.md` | Architectural truth source | May need wording alignment if follow-up scope clarifies telemetry or narrow-slice expectations |
| `backend/tracing.py` | Telemetry integration seam | Potential downstream seam if degraded-telemetry behavior requires backend-visible handling |

### Downstream Files Likely In Scope For Design
| File group | Relationship |
|---|---|
| `src/core/gateway/` | Primary runtime hardening surface |
| `tests/core/gateway/` | Deterministic regression proof surface |
| `docs/project/prj0000124-llm-gateway/` | Source-project truth and lifecycle synchronization |
| `docs/project/prj0000125-llm-gateway-lessons-learned-fixes/` | Follow-up project artifacts |
| `docs/architecture/adr/0009-llm-gateway-hybrid-split-plane.md` | Architecture wording only if required by corrected scope |

## Step 1 Research Evidence
| Task Type | Findings | Evidence |
|---|---|---|
| Literature review | The current implementation already emits telemetry and enforces pre/post policy gates, but it does not yet implement the full degraded-telemetry or provider-exception contracts described in the design. | `src/core/gateway/gateway_core.py`, `docs/project/prj0000124-llm-gateway/llm-gateway.design.md`, `docs/architecture/adr/0009-llm-gateway-hybrid-split-plane.md` |
| Alternative enumeration | The follow-up work can credibly be executed as one consolidated remediation, as sequenced waves in one project, or as docs/governance-first normalization before code changes. | `docs/project/prj0000125-llm-gateway-lessons-learned-fixes/llm-gateway-lessons-learned-fixes.project.md`, `docs/project/prj0000125-llm-gateway-lessons-learned-fixes/llm-gateway-lessons-learned-fixes.design.md` |
| Prior-art search | Prior repo cleanup work favors bounded cleanup waves and explicit lifecycle synchronization instead of open-ended polish. Earlier gateway artifacts also show how quickly truth can drift after a narrow slice merges. | `docs/project/prj0000124-llm-gateway/llm-gateway.git.md`, `docs/project/archive/prj0000100-repo-cleanup-docs-code/prj0000100-repo-cleanup-docs-code.plan.md`, `docs/project/archive/prj0000093-projectmanager-ideas-autosync/projectmanager-ideas-autosync.think.md` |
| Constraint mapping | The project boundary allows analysis only now, future remediation code should stay inside `src/core/gateway/`, `tests/core/gateway/`, targeted prj0000124 docs, and `backend/tracing.py` only if telemetry alignment requires it. Naming decisions must comply with `snake_case`. | `docs/project/prj0000125-llm-gateway-lessons-learned-fixes/llm-gateway-lessons-learned-fixes.project.md`, `docs/project/naming_standards.md`, `docs/project/code_of_conduct.md` |
| Stakeholder impact | Runtime/test fixes affect @5test, @6code, @7exec, @8ql, and gateway callers; docs/governance changes affect project traceability; naming changes would affect imports and future contributor guidance. | `src/core/gateway/__init__.py`, `tests/core/gateway/test_gateway_core.py`, `backend/tracing.py`, `docs/project/prj0000124-llm-gateway/llm-gateway.project.md` |
| Risk enumeration | The highest-risk failures are policy/budget bypass under runtime errors, false-positive ordering tests, and document truth drift that misstates what PR #287 actually delivered. | `src/core/gateway/gateway_core.py`, `tests/core/gateway/test_gateway_core_orchestration.py`, `docs/project/prj0000124-llm-gateway/llm-gateway.project.md`, PR #287 metadata |

## Constraints
- Branch gate passed: `git branch --show-current` -> `prj0000125-llm-gateway-lessons-learned-fixes`.
- Analysis only in this step; no runtime implementation is allowed.
- Repository naming policy is not ambiguous for execution: `docs/project/naming_standards.md` requires `snake_case`, and the current gateway files already comply.
- Minimal-risk sequencing matters more than closing every documentation issue in one pass.
- `docs/project/code_of_conduct.md` introduces no blocker for this scope; the work is technical and governance-oriented.

## Options
### Option A - One Consolidated Remediation Slice
**Summary**
Deliver runtime hardening, deterministic test correction, prj0000124 lifecycle/doc cleanup, and naming/convention resolution together as one tightly managed implementation slice.

**Scope boundary**
- Runtime: `src/core/gateway/gateway_core.py`
- Tests: `tests/core/gateway/test_gateway_core_orchestration.py`, `tests/core/gateway/test_gateway_core.py`
- Docs/governance: `docs/project/prj0000124-llm-gateway/*`, `docs/architecture/adr/0009-llm-gateway-hybrid-split-plane.md` if wording must change
- Naming review: documentation decision plus any import/file rename deemed necessary

**Research coverage used**
- Literature review: runtime/design mismatch in `gateway_core.py` vs `llm-gateway.design.md`
- Prior-art search: bounded cleanup waves in `prj0000100-repo-cleanup-docs-code.plan.md`
- Constraint mapping: prj0000125 project boundary and naming standard
- Stakeholder impact: gateway runtime, test suite, project artifacts, possible import consumers
- Risk enumeration: runtime correctness and governance truth can fail independently

**SWOT**
- Strengths: closes all known follow-up items in one project and one downstream design/plan cycle.
- Weaknesses: mixes behavior fixes, test corrections, documentation truth sync, and naming decisions into one larger blast radius.
- Opportunities: one PR can leave the gateway lane in a much cleaner post-merge state.
- Threats: naming or documentation churn can delay urgent fail-closed runtime corrections.

**Security and delivery risks**
| Failure mode | Likelihood | Impact | Mitigation | Testability signal |
|---|---|---|---|---|
| Runtime hardening mixes with docs/naming changes and obscures behavioral regression source | M | H | Keep commit/task boundaries inside the slice and require targeted selectors before docs gates | `python -m pytest -q tests/core/gateway/test_gateway_core_orchestration.py` |
| Naming review expands into file renames and import churn | M | H | Freeze renames unless a proven live mismatch exists beyond guidance conflict | import usage scan plus targeted gateway selectors |
| Docs cleanup grows beyond source-of-truth correction into repo-wide lint work | M | M | Limit docs edits to prj0000124/prj0000125/ADR surfaces directly tied to this lesson set | `python -m pytest -q tests/docs/test_agent_workflow_policy_docs.py` |

**Validation strategy**
1. Gateway runtime selectors first.
2. Any targeted integration selector for telemetry if `backend/tracing.py` changes.
3. Docs workflow policy selector after artifact updates.
4. Narrow pre-commit or lint checks only on touched files.

**Why it is not the best next move**
It is coherent, but it couples urgent runtime/test correctness with the least time-critical part of the work: artifact truth sync and naming adjudication.

### Option B - Sequenced Remediation Waves In One Project (Recommended)
**Summary**
Keep prj0000125 as one project and one branch, but execute three explicit waves: runtime/test correctness first, docs/governance truth sync second, and naming review third as a decision gate that defaults to no rename.

**Scope boundary**
- Wave 1 runtime/test: `src/core/gateway/gateway_core.py`, `tests/core/gateway/test_gateway_core_orchestration.py`, `tests/core/gateway/test_gateway_core.py`, `backend/tracing.py` only if telemetry degradation cannot be contained within gateway orchestration.
- Wave 2 docs/governance: `docs/project/prj0000124-llm-gateway/*`, `docs/project/prj0000125-llm-gateway-lessons-learned-fixes/*`, ADR wording only if runtime/design truth requires it.
- Wave 3 naming: repo-rule decision in docs/design/plan; rename only if @3design proves current filenames violate the actual governing rule set.

**Research coverage used**
- Literature review: current runtime/test/doc mismatches in `gateway_core.py`, orchestration test, and prj0000124 artifacts
- Prior-art search: phased cleanup and synchronization pattern in `prj0000100-repo-cleanup-docs-code.plan.md`; centralized source-of-truth validation in `projectmanager-ideas-autosync.think.md`
- Constraint mapping: minimal-risk sequencing, snake_case naming rule, analysis-only current step
- Stakeholder impact: behavior owners first, then documentation owners, then naming/governance decision makers
- Risk enumeration: each wave has a smaller, more diagnosable failure surface

**SWOT**
- Strengths: fixes the highest-severity behavior risk first while still keeping docs and naming inside the same accountable project.
- Weaknesses: requires more explicit phase discipline and slightly more handoff structure.
- Opportunities: allows @3design to keep naming as a decision rather than accidentally turning it into a rename migration.
- Threats: if wave boundaries are not enforced, the project can still collapse back into Option A sprawl.

**Security and delivery risks**
| Failure mode | Likelihood | Impact | Mitigation | Testability signal |
|---|---|---|---|---|
| Runtime hardening scope expands into fallback/cache/memory redesign | M | H | Cap Wave 1 to budget deny, provider/runtime exception failure commit, degraded telemetry, and deterministic chronology only | targeted gateway selectors plus exact error-path tests |
| Wave 2 docs truth sync is skipped after Wave 1 passes | M | M | Make artifact synchronization a required convergence step before @9git | `python -m pytest -q tests/docs/test_agent_workflow_policy_docs.py` |
| Wave 3 naming review triggers unnecessary renames | L | H | Require proof of live rule violation; default to documentation-only resolution | import usage scan and branch-scope review |

**Validation strategy**
1. Wave 1: targeted gateway selectors proving fail-closed deny, exception commit, degraded telemetry, and deterministic call chronology.
2. Wave 2: docs workflow policy gate plus selective markdown lint cleanup on changed project artifacts.
3. Wave 3: no rename unless import-usage evidence and rule precedence justify it; if deferred, record explicit decision in design/plan docs.

**Why it is the best next move**
It matches the actual severity ordering: behavior correctness first, truth synchronization second, naming governance third. It also preserves one project and one branch, so follow-up accountability stays intact without forcing low-risk docs work to block scoping of runtime fixes.

### Option C - Documentation/Governance First, Runtime Hardening Second
**Summary**
Normalize prj0000124 project state, fix markdown/lifecycle drift, and settle naming guidance before changing runtime or tests.

**Scope boundary**
- First wave docs only: `docs/project/prj0000124-llm-gateway/*`, `docs/project/prj0000125-llm-gateway-lessons-learned-fixes/*`, ADR wording if needed
- Second wave runtime/test: `src/core/gateway/gateway_core.py`, gateway tests, `backend/tracing.py` only if required
- Naming review completed before any runtime changes

**Research coverage used**
- Literature review: obvious drift in `llm-gateway.project.md` and PR body claims vs narrow slice implementation
- Prior-art search: lifecycle synchronization and documentation source-of-truth cleanup patterns
- Constraint mapping: docs are low-risk to edit and immediately testable
- Stakeholder impact: mostly governance owners first, runtime owners second
- Risk enumeration: runtime gaps remain live longer

**SWOT**
- Strengths: clears artifact confusion early and gives @3design a cleaner baseline.
- Weaknesses: postpones the highest-severity runtime correctness fixes.
- Opportunities: can reduce downstream debate about what PR #287 did and did not ship.
- Threats: documentation may need to be edited twice if runtime design decisions materially change the expected behavior wording.

**Security and delivery risks**
| Failure mode | Likelihood | Impact | Mitigation | Testability signal |
|---|---|---|---|---|
| Known fail-closed runtime gaps remain unresolved while docs are updated | H | H | Keep docs-first only if runtime implementation is blocked by missing design inputs | runtime regression selectors remain pending/open |
| Artifact wording is updated before final runtime scope is agreed | M | M | Restrict changes to clearly false lifecycle/status claims only | docs workflow policy selector |
| Naming review consumes time without production benefit | M | M | Default to no rename and record the decision quickly | design or plan review gate |

**Validation strategy**
1. Docs workflow policy selector after each documentation wave.
2. Runtime selectors only after the later code wave starts.
3. Explicit scope review before any rename or import change.

**Why it is not the best next move**
This ordering optimizes clarity, not risk reduction. The outstanding runtime gaps are more important than artifact cleanliness.

## Decision Matrix
| Criterion | Option A Consolidated | Option B Sequenced Waves | Option C Docs First |
|---|---|---|---|
| Fixes highest-risk runtime behavior earliest | M | H | L |
| Keeps docs/governance accountability in this project | H | H | H |
| Limits blast radius of naming debate | L | H | M |
| Testability and fault isolation | M | H | M |
| Delivery simplicity | M | M | M |
| Risk of scope creep | H | M | M |
| Best fit for minimal-risk sequencing | M | H | L |

## Recommendation
**Option B - Sequenced remediation waves in one project**

Why this recommendation is defensible:
1. It addresses the highest-severity gap first: fail-closed runtime correctness under deny and exception paths.
2. It still keeps docs/governance reconciliation inside prj0000125, which avoids creating another follow-up project for truth maintenance.
3. It treats naming as a governance decision point, not an automatic rename exercise.
4. It matches repository prior art that favors bounded cleanup waves and explicit lifecycle synchronization rather than broad mixed-purpose cleanups.

Historical prior-art references:
- `docs/project/prj0000124-llm-gateway/llm-gateway.design.md`
- `docs/project/prj0000124-llm-gateway/llm-gateway.git.md`
- `docs/project/archive/prj0000100-repo-cleanup-docs-code/prj0000100-repo-cleanup-docs-code.plan.md`
- `docs/project/archive/prj0000093-projectmanager-ideas-autosync/projectmanager-ideas-autosync.think.md`

Recommendation risk-to-testability mapping:
- Runtime wave grows beyond hardening into redesign -> constrain Wave 1 to budget deny, provider/runtime exception failure commit, degraded telemetry, and deterministic chronology; prove with targeted gateway selectors.
- Docs wave leaves source project inconsistent -> require docs workflow policy pass after prj0000124/prj0000125 artifact synchronization.
- Naming wave becomes a rename migration -> require proof of live rule violation and import impact before any rename; otherwise resolve in documentation only.

## Decision Points For @3design
1. **Runtime hardening depth**
	- Recommended in scope now: budget-denied fail-closed before provider execution, deterministic `commit_failure` on provider/runtime exceptions, and degraded-telemetry handling consistent with the design contract.
	- Recommended deferred: broader fallback-manager redesign, cache-hit short-circuit behavior, memory integration changes, or typed envelope expansion unrelated to the lessons-learned defects.
2. **Naming changes now vs later**
	- Recommended default: no file rename in prj0000125.
	- Record explicit precedence that repository naming governance is `snake_case`, note that current gateway files already comply, and defer any broader filename normalization to a dedicated rename project if more conflicts are discovered.
3. **Bundled vs isolated doc-lint cleanup**
	- Recommended: bundle only the documentation changes that directly restore truthful state for prj0000124/prj0000125 and any markdown lint issues inside those touched artifacts.
	- Do not expand this project into repo-wide markdown cleanup.

## Open Questions
1. Can degraded-telemetry handling be fully implemented inside `GatewayCore`, or does `backend/tracing.py` need an explicit helper or contract change?
2. Should Wave 2 update only the clearly stale source-project overview, or also normalize plan/test/code/exec/git wording where PR #287 overstated delivered scope?
3. Does @3design want to record the naming-rule precedence in the prj0000125 design artifact only, or also add a short note in the source-project docs to prevent future ambiguity?