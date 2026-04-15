# Code

This file summarizes where the main code components live.

## Key code areas
- `src/logic/agents/`: agent orchestration and workflows
- `src/core/base/`: core mixins, state managers, and transaction engines
- `src/inference/`: LLM connectors and tool-call orchestrators
- `rust_core/`: performance-critical Rust kernels exposed via PyO3

## When to update
- When the code layout changes in a way that affects how agents locate or interact with core components.
