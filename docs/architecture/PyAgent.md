# PyAgent Architecture (Reference)

PyAgent is a **transactional, Rust‑accelerated multi‑agent system** built for safe, autonomous code improvement.

## Key Concepts (for agents)
- **Core vs Agent separation**: Agents orchestrate; `*Core` classes contain domain logic.
- **Mixins** provide shared behavior (persistence, memory, identity, auditing) without deep inheritance.
- **Transactional safety**: all FS changes are wrapped in `StorageTransaction` / `MemoryTransaction` / `ProcessTransaction` and can rollback on failure.
- **Rust acceleration**: `rust_core/` holds performance kernels (diff/patch, metrics, parsing) exposed via PyO3.
- **Async runtime**: Agents run in a Tokio-based scheduler (Rust) with Python coroutines; blocking loops are prohibited by audit tests.

## Primary paths
- `src/core/base/` — transaction managers, mixins, state models
- `src/logic/agents/` — agent orchestration
- `src/logic/` — reasoning cores and coordination
- `src/inference/` — LLM connectors, tool loops, streaming
- `rust_core/` — Rust performance libraries
- `docs/project/` — project plans and design docs (source of truth)

## Quick setup (local)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd rust_core
maturin develop --release
```

## Where to look next
- Design/architecture overviews: `docs/architecture/`
- Project plans: `docs/project/prjXXX-*`
