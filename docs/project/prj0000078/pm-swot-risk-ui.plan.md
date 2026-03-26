# pm-swot-risk-ui — Implementation Plan

_Status: NOT_STARTED_
_Planner: @4plan | Updated: 2026-03-26_

## Overview
<!-- summary -->

## Task List
- [ ] T1 — Extend `Editor` props: `initialContent?: string`, `scrollToSection?: string` | Files: `web/apps/Editor.tsx` | Acceptance: Editor renders provided content; scrolls to target heading
- [ ] T2 — Thread `openEditor` callback from `App.tsx` into `ProjectManager` → `FilterBar` | Files: `web/App.tsx`, `web/apps/ProjectManager.tsx` | Acceptance: `FilterBar` can trigger Editor open
- [ ] T3 — Add "SWOT Analysis" and "Risk Register" buttons to `FilterBar` | Files: `web/apps/ProjectManager.tsx` | Acceptance: Two new buttons visible; click opens Editor at correct section
- [ ] T4 — Fetch `kanban.md` content (via API or static import) for Editor pre-load | Files: TBD by @4plan | Acceptance: kanban.md text is available client-side when button clicked

## Milestones
| # | Milestone | Tasks | Status |
|---|---|---|---|
| M1 | Editor extensible | T1 | |
| M2 | Callback wired | T2 | |
| M3 | Buttons live | T3, T4 | |

## Validation Commands
```powershell
pytest tests/structure/ -x -q
```
