# Async Runtime Update
> **2026-03-10:** Project migrated to Node.js-like asynchronous runtime; synchronous loops are prohibited by automated tests.

# Agents Subsystem Design

This document summarizes the architecture and design considerations for the
`agents` package, which lives in `src/agents`.

> **Overview (extracted from legacy code)**
>
> OrchestratorAgent for PyAgent Swarm Management.
>
> This agent acts as the primary coordinator for sub-swarms, managing task
delegation, resource allocation, and final response synthesis. It implements
advanced self-healing and multi-agent synergy protocols.
>
> The current implementation delegates most domain logic to specialized
> managers (metrics, file, git, command, core). The core remains a thin
> orchestration layer, making future Rust porting feasible.

## Key Concepts

- **OrchestratorAgent**: central class responsible for spawning and supervising
  sub‑agents, handling lifecycle events, and aggregating results.
- **Plugin architecture**: allow third‑party extensions via `AgentPluginBase`.
- **Metric tracking**: every agent emits telemetry through a `metrics_manager`.
- **Git integration**: `git_handler` encapsulates repository operations.
- **Command runners**: separate thread/process execution via
  `AgentCommandHandler`.

## Design Goals

1. **Modularity** – keep agents small, focused and replaceable.
2. **Extensibility** – support new agent types, protocols, or communication
   channels via plugins.
3. **Resilience** – implement self‑healing, retries, and health checks.
4. **Language‑agnostic core** – maintain a thin Python wrapper around a
   performance‑critical core (Rust or native).

## Outstanding Brainstorm Topics

- Swarm coordination strategies (round‑robin, priority queue, token bucket).
- Agent lifecycle and state machine design.
- Agent authentication/identity across fleets.
- Versioning and rollback of agent behavior.

*Reuse and refactor content from `src-old/classes/agent/Agent.py` above.*