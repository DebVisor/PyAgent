# Exec

This document captures the runtime execution model.

## Key points
- PyAgent runs on a **Rust/Tokio async runtime** that schedules Python coroutines via FFI.
- The system prohibits blocking loops; tests enforce this.

## Where to find more
- See `docs/architecture/archive/` for deep dives on async runtime and task scheduling.

## When to update
- When the runtime model changes (scheduler design, async semantics, threading model).
