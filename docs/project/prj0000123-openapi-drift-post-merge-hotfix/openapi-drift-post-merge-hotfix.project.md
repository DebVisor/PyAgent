# openapi-drift-post-merge-hotfix - Project Overview

_Status: IN_PROGRESS_
_Owner: @1project | Updated: 2026-04-04_

## Project Identity
**Project ID:** prj0000123
**Short name:** openapi-drift-post-merge-hotfix
**Project folder:** docs/project/prj0000123-openapi-drift-post-merge-hotfix/

## Project Overview
Post-merge hotfix boundary to address CI / Lightweight failure where tests/docs/test_backend_openapi_drift.py reports backend_openapi.json drift after PR #284 merge.

## Goal & Scope
**Goal:** Re-establish CI stability by removing OpenAPI drift regressions introduced after PR #284 and provide a governed project boundary for downstream analysis and implementation.
**In scope:** project boundary initialization, discovery/design/plan artifact scaffolding, lane registration, branch-plan enforcement, and validation gates.
**Out of scope:** direct code fixes to backend OpenAPI generation in this initialization step.

## Branch Plan
**Expected branch:** prj0000123-openapi-drift-post-merge-hotfix
**Scope boundary:** docs/project/prj0000123-openapi-drift-post-merge-hotfix/ plus registry files docs/project/kanban.json, data/projects.json, and data/nextproject.md.
**Handoff rule:** @9git must refuse staging, commit, push, or PR work unless the active branch matches this project and changed files stay inside the scope boundary.
**Failure rule:** If project ID or branch plan is missing, conflicting, or ambiguous, return task to @0master before downstream handoff.

## Milestones
| # | Milestone | Agent | Status |
|---|---|---|---|
| M1 | Options explored | @2think | NOT_STARTED |
| M2 | Design confirmed | @3design | NOT_STARTED |
| M3 | Plan finalized | @4plan | NOT_STARTED |
| M4 | Tests written | @5test | NOT_STARTED |
| M5 | Code implemented | @6code | NOT_STARTED |
| M6 | Integration validated | @7exec | NOT_STARTED |
| M7 | Security clean | @8ql | NOT_STARTED |
| M8 | Committed | @9git | NOT_STARTED |

## Status
_Last updated: 2026-04-04_
Initialization complete for project boundary and governance artifacts. Ready for @2think handoff.
