# Async Runtime Update
> **2026-03-10:** Project migrated to Node.js-like asynchronous runtime; synchronous loops are prohibited by automated tests.

# Core Subsystem Design

The `src/core` tree houses foundational components shared by all agents and
services.  It is where low‑level abstractions, state managers, and common
utilities live.  The repo’s architectural guidelines (see `gemini.md`) define
the core philosophy:

> - **Mixin-Based Agents** – agents should be composed from small mixins rather
>   than monolithic classes (`src/core/base/mixins/`).
> - **Core/Agent separation** – domain logic lives in `*Core` classes; agent
>   wrappers handle orchestration, prompting, and state only
>   (e.g. `BaseAgent` + `BaseAgentCore`).
> - **Rust acceleration** – high‑throughput logic (metrics, bulk operations,
>   complexity analysis) should be moved into `rust_core/` with a thin Python
>   bridge.

## Architectural Principles

1. **Modularity** – the core tree is organised by concern (`base`,
   `metrics`, `verification`, `configuration`, etc.).  Each module exposes a
   Python API and, where appropriate, a matching Core class.
2. **Transactions & Safety** – use `AgentStateManager`, `MemoryTransaction`,
   and similar patterns to ensure atomicity and recoverability.
3. **Language Agnosticism** – keep core logic independent of any particular
   LLM or agent implementation.  Cores should be easy to port to Rust or
   another language.
4. **Testability** – Core classes have corresponding unit tests; see existing
   `*_test.py` files in `src-old/core/base` for examples.

## Legacy Content Highlights

- `src-old/core/base/base_agent.py` and `metrics_engine.py` were previously
  monolithic; todo list items mention decomposing them into `BaseAgent`/
  `BaseAgentCore` and `MetricsCore` respectively.  Refactoring should continue
  along this “core/shell” pattern.
- `verification_core.py` illustrates how independent core modules encapsulate a
  distinct domain (multi‑agent consensus).

## Potential Brainstorm Topics

- Definition of core package boundaries and dependency graph (e.g., which
  cores may import others).
- Core plugin mechanism (how additional cores register themselves).
- Versioning strategy for core APIs vs agent-facing wrappers.
- Performance testing harness for Rust-interfaced cores.

*Reuse guidelines text from `gemini.md` and examples from `src-old/core/base`.*