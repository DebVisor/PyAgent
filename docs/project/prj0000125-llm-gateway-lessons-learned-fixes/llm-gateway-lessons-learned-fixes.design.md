# llm-gateway-lessons-learned-fixes - Design

_Status: NOT_STARTED_
_Designer: @3design | Updated: 2026-04-04_

## Selected Option
No remediation design has been selected yet. This project starts from the assumption that follow-up fixes should preserve the merged phase-one gateway architecture rather than replace it.

## Architecture
The likely design shape is a targeted hardening pass over the existing gateway core and its immediate test/documentation seams. Expected design work will focus on deterministic fail-closed control flow, deterministic test evidence, and governance-document alignment with the merged implementation.

## Interfaces & Contracts
- `GatewayCore` must continue to fail closed before provider execution when budget or policy denies the request.
- Provider/runtime exception paths must commit budget failure deterministically.
- Telemetry failure behavior must remain consistent with the documented degraded-telemetry contract.
- Orchestration tests must use deterministic sequencing evidence rather than unordered side-effect comparisons.

## Non-Functional Requirements
- Performance: remediation must preserve the phase-one gateway performance profile and avoid unnecessary architecture expansion.
- Security: budget, policy, and provider-failure paths must remain deny-by-default and auditable.

## Open Questions
1. Does the naming review require file renames, alias shims, or only a documented repository-rule decision?
2. Which prj0000124 artifacts are authoritative for the green implementation state that PR #287 actually merged?