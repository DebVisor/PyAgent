# Async Runtime Update
> **2026-03-10:** Project migrated to Node.js-like asynchronous runtime; synchronous loops are prohibited by automated tests.

# Memory Subsystem Design

The `memory` package in `src/memory` provides long‑term storage for agent
knowledge, facts, and conversation context.  The legacy implementation used a
wrapper around ChromaDB, enabling vector search and persistent collections.

> **Legacy Overview**
>
> Manages persistent conversational and factual memory for agents.
>
> Uses ChromaDB with an HNSW index sharded over the filesystem to support
> trillions of parameters.  In absence of ChromaDB, the subsystem quietly
> disables itself.

## Architectural Highlights

- **Pluggable backends**: abstract interface so the store could switch to
  SQLite, Pinecone, or custom vector DBs.
- **Metadata tagging**: each entry carries a timestamp, tags, and optional
  JSON metadata for filtering.
- **Lazy initialization**: the database client is created on first access to
  avoid startup penalties when memory is disabled.
- **Query interface**: simple `store(content, metadata, tags)` and
  `query(query_text, n_results, filter_tags)` methods.

## Design Considerations

1. **Scalability** – design for sharding and horizontal scaling across fleet
   nodes.
2. **Consistency** – eventual consistency acceptable; conflict resolution
   strategy for concurrent writes.
3. **Privacy** – ability to purge or encrypt sensitive entries.
4. **Indexing strategies** – tune HNSW parameters or alternative indices
   depending on workload.

## Potential Brainstorm Areas

- Pluggable indexing abstraction with swap‑in/out algorithms.
- Offline/archived memory tier for very old entries.
- Memory summarization and pruning policies (synaptic pruning idea).

*Content reused from `src-old/classes/agent/LongTermMemory.py`.*