# Async Runtime Update
> **2026-03-10:** Project migrated to Node.js-like asynchronous runtime; synchronous loops are prohibited by automated tests.

# Swarm Architecture Design

The `src/swarm` package will encapsulate logic for managing collections of
agents working together.  Although the current tree is empty, `src-old`
contained numerous specialized swarm managers and agents, including
`CloudSwarmManager`, `DynamicDecomposerAgent`, and many others under
`classes/specialized` referencing "swarm" in their docstrings.

## Legacy Glimpse

- **CloudSwarmManager**: cross‑cloud orchestration across AWS, Azure, GCP.
  Handles provisioning, deployment, resource listing, and termination.
- **Specialized agents** such as `ArchitectAgent`, `ConsensusConflictAgent`,
  `AttentionBufferAgent` hint at roles within a swarm (architecture, conflict
  resolution, shared consciousness).
- `DynamicDecomposerAgent` split tasks and balanced swarm load.

## Core Principles

1. **Distributed coordination** – swarms should operate across nodes and
   clouds transparently.
2. **Role-based agents** – design agents with specific responsibilities (e.g.,
   health monitoring, load balancing, conflict resolution).
3. **Resource abstraction** – decouple agent logic from the underlying
   compute resources via a provider-agnostic API.
4. **Scalability & elasticity** – swarms can grow/shrink automatically based on
   workload.

## Brainstorm Topics

- Swarm membership protocols and discovery (gossip, mDNS).
- Healthcheck/heartbeat framework for agents in a swarm.
- Task decomposition and scheduling algorithms (token passing, auction).
- Cross-cloud consistency and data synchronization strategies.
- Economic model for swarm (agent cost, budget, auction core).

*Documentation content references old `CloudSwarmManager` and specialized
agent docstrings.*