# 3design Memory

This file records finalized design decisions, 
architecture diagrams, and key interface contracts.

## Auto-handoff (Design → Plan)

Once a design is finalized, the next agent in the workflow is **@4plan**.  
The designer agent should invoke **@4plan** via `agent/runSubagent` 
so the planning work is started automatically 
and the work is correctly attributed.

When calling `agent/runSubagent`, include a clear task description 
and any relevant context/links to the design decisions 
so the planning agent can continue without having to re-derive 
the design intent.

---

## prj030 - agent-doc-frequency

| Field | Value |
|---|---|
| **task_id** | prj030-agent-doc-frequency |
| **owner_agent** | @3design |
| **source** | @2think |
| **created_at** | 2026-03-18 |
| **updated_at** | 2026-03-18 |
| **status** | DONE |
| **summary** | Designed checkpoint rule (Step-Gated Full Overwrite) for all 9 agent artifact files. Templates inline per agent. @1project pre-creates all 9 stubs. Checkpoint rule applies to all artifact types. Documents updated before next runSubagent call. |
| **handoff_target** | @4plan |
| **artifact_paths** | docs/project/prj030-agent-doc-frequency/agent-doc-frequency.design.md |
---

## prj0000045 - transaction-managers-full

| Field | Value |
|---|---|
| **task_id** | prj0000045-transaction-managers-full |
| **owner_agent** | @3design |
| **source** | @2think |
| **created_at** | 2026-03-22 |
| **updated_at** | 2026-03-22 |
| **status** | HANDED_OFF |
| **branch_gate** | WARN — designed on `main`; expected `prj0000045-transaction-managers-full` |
| **selected_option** | Option B — `src/transactions/` package with BaseTransaction ABC |
| **key_decisions** | Dual-API coexistence (single class, two constructor modes); Fernet encryption (cryptography pkg, HKDF per-user key, user_id=None skips); httpx remote sync with dry_run=True for tests; ContextTransaction UUID lineage auto-wired from contextvar stack; ContextWindow LLM handoff deferred to follow-on project |
| **interface_contracts** | See design.md §Interfaces & Contracts; 5 open questions documented for @4plan |
| **shim_strategy** | 3 new src/core/ shims + 1 replacement src/MemoryTransactionManager.py shim |
| **handoff_target** | @4plan |
| **artifact_paths** | docs/project/prj0000045/transaction-managers-full.design.md |

---

## prj0000047 - conky-real-metrics

| Field | Value |
|---|---|
| **task_id** | prj0000047-conky-real-metrics |
| **owner_agent** | @3design |
| **source** | @2think |
| **created_at** | 2026-03-23 |
| **updated_at** | 2026-03-23 |
| **status** | DONE |
| **branch_gate** | PASS — `prj0000047-conky-real-metrics` |
| **selected_option** | Option A — REST Polling `GET /api/metrics/system` (psutil, module-level delta state) |
| **key_decisions** | 2s poll interval; `useSystemMetrics(2000)` custom hook; stay-on-last-values error strategy + OFFLINE badge; no Vite dev plugin needed (existing /api proxy sufficient); memory surfaces used_mb/total_mb/percent; disk I/O row added to UI; interface filter by name prefix (lo, docker, veth, br-, virbr, tun, tap, loopback, isatap, teredo) |
| **interface_contracts** | `SystemMetrics` TS interface; `SystemMetricsResponse` Pydantic model; `useSystemMetrics` hook; `_is_physical_iface()` helper; module-level `_prev_net` + `_prev_disk` delta state |
| **vite_config_change** | None required |
| **handoff_target** | @4plan |
| **artifact_paths** | docs/project/prj0000047/conky-real-metrics.design.md |