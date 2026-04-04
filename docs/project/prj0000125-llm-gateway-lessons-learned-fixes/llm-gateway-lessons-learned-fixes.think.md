# llm-gateway-lessons-learned-fixes - Options

_Status: NOT_STARTED_
_Analyst: @2think | Updated: 2026-04-04_

## Root Cause Analysis
1. PR #287 merged a valid phase-one gateway slice, but follow-up review identified behavior and governance gaps that were intentionally left for a separate branch.
2. The remaining gaps span four categories: fail-closed runtime behavior, deterministic test evidence, documentation/governance drift, and naming-rule reconciliation.
3. The new project boundary must decide whether to address these items as one remediation slice or as a phased set of tightly scoped fixes under a single branch.

## Options
### Option A - Single remediation slice
Address runtime hardening, deterministic test fixes, and document/governance cleanup in one coordinated follow-up branch.

### Option B - Runtime/test fixes first, docs cleanup second
Prioritize runtime and test correctness, then defer document/governance cleanup to a later project if the scope expands beyond a small remediation set.

### Option C - Documentation-first reconciliation before runtime changes
Normalize artifact status and naming guidance before code fixes so the implementation scope is clearer for downstream agents.

## Decision Matrix
| Criterion | Opt A | Opt B |
|---|---|---|
| Captures all PR #287 follow-ups in one branch | High | Medium |
| Minimizes delay before runtime hardening | High | High |
| Reduces governance drift quickly | High | Medium |

## Recommendation
Initial default: favor a single remediation slice unless @2think finds that the documentation/governance fixes introduce an independent risk profile that justifies splitting the work.

## Open Questions
1. Does degraded-telemetry alignment require only gateway telemetry code, or also backend tracing contracts?
2. Should documentation consistency updates be limited to prj0000124 artifacts, or include ADR text tied to the merged design/plan state?
3. Is any PascalCase filename still present in the merged gateway slice, or is the task limited to documenting the repo-standard decision for new files?