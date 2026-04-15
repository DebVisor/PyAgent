# PostgreSQL-Backed Unified Memory System

## Overview

A production-ready transaction-backed memory system with multiple virtual path data structures, powering 200K+ idea parallel execution tracking.

**Key Features:**
- ✅ **ACID Transactions** with savepoints and rollback
- ✅ **7 Virtual Path Data Structures** (KV, B-Tree, LinkedList, Graph, Kanban, Lessons, Code Ledger)
- ✅ **PostgreSQL Backend** for reliability and scalability
- ✅ **Execution Tracking** for 200K+ ideas across 10 workers
- ✅ **Code Metrics** aggregation and ledger
- ✅ **Lessons Learned** with recurrence tracking
- ✅ **Atomic Operations** across multiple stores

## Architecture

```
UnifiedMemorySystem (Coordinator)
├── PostgreSQL Core (Database Layer)
├── KVStore (Key-Value, TTL-enabled)
├── BTreeIndex (Sorted Range Queries)
├── LinkedList (Ordered Sequences)
├── Graph (DAG Task Dependencies)
├── KanbanBoard (Workflow Tracking)
├── LessonLearned (Pattern Tracking)
├── CodeImplementationLedger (Metrics)
└── MemoryTransaction (ACID Wrapper)
```

## Virtual Path Data Structures

### 1. **KV Store** - O(1) Fast Lookups
```python
# Set with TTL
memory.kv_set("worker:0:status", {"status": "RUNNING"}, ttl_seconds=3600)

# Get
status = memory.kv_get("worker:0:status")

# Cleanup expired
memory.cleanup_expired()

# List by prefix
keys = memory.kv_keys("worker:*")
```

**Use Cases:**
- Worker status caching
- Configuration with expiration
- Session state
- Quick lookups during execution

---

### 2. **B-Tree Index** - Range Queries & Sorted Iteration
```python
# Insert
memory.btree_insert("idea:000001", {"priority": 5, "status": "BACKLOG"})

# Search
idea = memory.btree_search("idea:000001")

# Range query
ideas_1_to_100 = memory.btree_range("idea:000001", "idea:000100")

# Scan sorted
all_ideas = memory.btree_scan_sorted(limit=1000)
```

**Use Cases:**
- Fast lookups of ideas by ID
- Range queries (e.g., ideas 1000-2000)
- Sorted iteration without sorting overhead
- Performance metrics indexing

---

### 3. **Linked List** - Ordered Sequences
```python
# Append to list
memory.ll_append("execution-timeline", {"stage": "INIT", "time": "2026-04-06T08:18"})

# Insert at position
memory.ll_insert_at("execution-timeline", 0, {"stage": "PRE-INIT", "time": "..."})

# Get item
item = memory.ll_get_at("execution-timeline", 5)

# Traverse
timeline = memory.ll_traverse("execution-timeline")

# Reverse
reverse_timeline = memory.ll_reverse_traverse("execution-timeline")
```

**Use Cases:**
- Execution timeline (INIT → COMPLETE)
- Batch processing queues
- Stage transition history
- Audit trails

---

### 4. **Graph (DAG)** - Task Dependencies
```python
# Add nodes
memory.graph_add_node("idea:1", "IDEA", {"title": "Feature 1", "priority": 5})
memory.graph_add_node("impl:1", "IMPLEMENTATION", {"file": "feature1.py", "loc": 500})
memory.graph_add_node("test:1", "TEST", {"framework": "pytest", "count": 25})

# Add edges (dependencies)
memory.graph_add_edge("idea:1", "impl:1", "IMPLEMENTS")
memory.graph_add_edge("impl:1", "test:1", "TESTED_BY")

# Query relationships
successors = memory.graph_get_successors("idea:1")  # → ["impl:1"]
predecessors = memory.graph_get_predecessors("test:1")  # → ["impl:1"]

# Topological sort for safe parallel execution
order = memory.graph_topological_sort()

# Get dependencies transitively
deps = memory.graph_get_dependencies("test:1")
# {1: ["impl:1"], 2: ["idea:1"]}
```

**Use Cases:**
- Idea → Implementation → Test → Deploy DAG
- Worker → Shard → Idea hierarchy
- Dependency analysis
- Blockage detection
- Topological ordering for parallelism

---

### 5. **Kanban Board** - Workflow Tracking
```python
# Create board
memory.kanban_create_board(
    "mega-execution",
    "200K Ideas Pipeline",
    ["BACKLOG", "ENQUEUED", "IN_PROGRESS", "TESTING", "COMPLETED", "FAILED"]
)

# Create card
memory.kanban_create_card("idea:001", "Feature 1", "BACKLOG", project_id="mega-execution", priority=5)

# Move card through workflow
memory.kanban_move_card("idea:001", "ENQUEUED")
memory.kanban_move_card("idea:001", "IN_PROGRESS")
memory.kanban_move_card("idea:001", "TESTING")
memory.kanban_move_card("idea:001", "COMPLETED")  # Auto-sets completed_at

# Query
cards = memory.kanban_get_cards_by_status("IN_PROGRESS", project_id="mega-execution")
summary = memory.kanban_board_summary("mega-execution")
# {"BACKLOG": 150000, "ENQUEUED": 30000, "IN_PROGRESS": 15000, ...}

# Assign and prioritize
memory.kanban_get_card("idea:001")
```

**Use Cases:**
- BACKLOG → TODO → IN_PROGRESS → REVIEW → DONE
- Per-idea progress visibility
- Bottleneck identification
- Priority-based queue management
- Worker assignment tracking

---

### 6. **Lessons Learned** - Pattern Tracking & Prevention
```python
# Record a lesson
lesson_id = memory.lesson_record(
    pattern="Database connection timeout",
    root_cause="Connection pool exhausted under parallelism",
    prevention="Implement pool scaling + circuit breaker"
)

# Record occurrences
memory.lesson_record_occurrence(lesson_id, context="worker-3, shard-42")
memory.lesson_record_occurrence(lesson_id, context="worker-7, shard-128")
memory.lesson_record_occurrence(lesson_id, context="worker-9, shard-251")

# Search lessons
lessons = memory.lesson_search("timeout")

# Get top recurring (to prioritize prevention)
top = memory.lesson_top_recurring(limit=10)
# [
#   {"lesson_id": 1, "pattern": "timeout", "recurrence_count": 4, ...},
#   {"lesson_id": 2, "pattern": "memory_leak", "recurrence_count": 3, ...},
#   ...
# ]

# Promote lesson to standard practice
memory.lesson_promote_to_prevention(1)
```

**Use Cases:**
- Track failures and patterns
- Detect recurring issues
- Implement preventive measures
- Convert lessons to standard practices
- Reduce repeat mistakes

---

### 7. **Code Implementation Ledger** - Metrics & Tracking
```python
# Log implementation
impl_id = memory.code_log(
    project_id="mega-execution-v1",
    file_path="core/executor.py",
    lines_of_code=2500,
    coverage_percent=92.5,
    quality_score=8.7,
    module_name="executor",
    idea_id="idea:001"
)

# Get implementation details
impl = memory.code_get(impl_id)
# {
#   "impl_id": 1,
#   "project_id": "mega-execution-v1",
#   "file_path": "core/executor.py",
#   "lines_of_code": 2500,
#   "coverage_percent": 92.5,
#   "quality_score": 8.7,
#   "test_count": 45,
#   "passed_tests": 45,
#   ...
# }

# Project statistics
stats = memory.code_project_stats("mega-execution-v1")
# {
#   "file_count": 450,
#   "total_loc": 185000,
#   "avg_coverage": 87.5,
#   "avg_quality": 8.6,
#   "total_tests": 450,
#   "total_passed": 445
# }

# List implementations
implementations = memory.code_list("mega-execution-v1", limit=100)

# Update test results
memory.code_ledger.update_test_results(impl_id, test_count=50, passed_tests=50)
```

**Use Cases:**
- Track every code implementation
- Monitor coverage trends
- Quality metrics aggregation
- LOC tracking per project
- Idea-to-implementation mapping
- Test result tracking

## Transactions

All operations can be wrapped in ACID transactions for atomicity:

```python
# Sync transaction
with memory.transaction() as tx:
    # Create idea
    memory.graph_add_node("idea:999", "IDEA", {"title": "New Feature"})
    
    # Log implementation
    impl_id = memory.code_log(
        "mega-execution-v1",
        "new_feature.py",
        2000,
        88.0,
        8.5,
        "new_feature"
    )
    
    # Update kanban
    memory.kanban_create_card("idea:999-card", "Implement Feature", "IN_PROGRESS")
    
    # All operations committed atomically
    # If any fails, entire transaction rolls back

# Savepoints for nested rollback
with memory.transaction() as tx:
    memory.kv_set("key1", "value1")
    tx.savepoint("checkpoint1")
    
    try:
        memory.kv_set("key2", "value2")  # Might fail
    except:
        tx.rollback_to_savepoint("checkpoint1")  # key2 rolled back, key1 kept
```

## Database Schema

```
kv_store
├── key (TEXT PRIMARY KEY)
├── value (BYTEA)
├── metadata (JSONB)
├── ttl_expires_at (TIMESTAMP)
└── Index: ttl expiration

btree_nodes
├── node_id (BIGSERIAL)
├── parent_id (BIGINT FK)
├── key (TEXT)
├── value (JSONB)
├── left_child_id, right_child_id (BIGINT FK)
└── height, balance_factor

linked_list_nodes
├── node_id (BIGSERIAL)
├── list_id (TEXT)
├── data (JSONB)
├── prev_node_id, next_node_id (BIGINT FK)
└── position (INT UNIQUE per list)

graph_nodes
├── node_id (TEXT PRIMARY KEY)
├── node_type (TEXT)
├── data (JSONB)
└── metadata (JSONB)

graph_edges
├── edge_id (BIGSERIAL)
├── from_node_id (TEXT FK)
├── to_node_id (TEXT FK)
├── edge_type (TEXT)
├── weight (FLOAT)
└── Constraint: UNIQUE(from, to, type)

kanban_cards
├── card_id (TEXT PRIMARY KEY)
├── title (TEXT)
├── status (TEXT)
├── priority (INT)
├── assignee (TEXT)
├── project_id (TEXT)
├── completed_at (TIMESTAMP)
└── Indexes: status, project, priority

lessons
├── lesson_id (BIGSERIAL)
├── pattern (TEXT)
├── root_cause (TEXT)
├── prevention (TEXT)
├── recurrence_count (INT)
├── promotion_status (TEXT)
└── Indexes: status, pattern

code_implementations
├── impl_id (BIGSERIAL)
├── project_id (TEXT)
├── file_path (TEXT)
├── module_name (TEXT)
├── lines_of_code (INT)
├── coverage_percent (FLOAT)
├── quality_score (FLOAT)
├── test_count, passed_tests (INT)
└── Indexes: project, idea, module
```

## Quick Start

```python
from memory_system.unified_memory import UnifiedMemorySystem

# Initialize
memory = UnifiedMemorySystem()
memory.initialize()

# Use any virtual path
memory.kv_set("status", "RUNNING", ttl_seconds=3600)
memory.graph_add_node("task:1", "TASK", {"name": "Test"})
memory.kanban_create_card("idea:1", "Feature 1", "BACKLOG")
memory.code_log("project1", "file.py", 500, 90.0, 8.5)

# Shutdown
memory.shutdown()

# Or use context manager
with UnifiedMemorySystem() as memory:
    memory.kv_set("key", "value")
    # Auto-shutdown on exit
```

## Execution Plan Integration

The system tracks the 200K+ idea execution with:

1. **KV Store**: Worker status, shard completion tracking
2. **B-Tree**: Fast idea lookups and range queries
3. **Linked List**: Execution timeline (INIT → COMPLETE)
4. **Graph**: Idea→Impl→Test→Deploy DAG
5. **Kanban**: BACKLOG→ENQUEUED→IN_PROGRESS→TESTING→COMPLETED
6. **Lessons**: Track failures, prevent recurrence
7. **Code Ledger**: Track implementations, metrics, quality

**Execution Flow:**
```
Worker 0: Process Shards 0-41
  ├── Shard 0: Process Ideas 0-475
  │   ├── Create idea node (Graph)
  │   ├── Create kanban card (Kanban)
  │   ├── Log implementation (Code Ledger)
  │   └── Update execution timeline (Linked List)
  ├── Shard 1: Process Ideas 476-951
  └── ...

Worker 1: Process Shards 42-83 (parallel)
  └── ...
```

## Performance Characteristics

| Operation | Time Complexity | Use Case |
|-----------|-----------------|----------|
| KV Get/Set | O(1) | Worker status, config caching |
| B-Tree Search | O(log n) | Idea lookup |
| B-Tree Range | O(log n + k) | Idea ranges |
| Linked List Append | O(1) | Timeline updates |
| Linked List Insert | O(n) | Timeline insertion |
| Graph Add Node | O(1) | Idea creation |
| Graph Add Edge | O(1) | Dependency creation |
| Kanban Move | O(1) | Status update |
| Lessons Search | O(n) | Pattern matching |

## Testing

```bash
python -m pytest memory_system/tests/ -v
```

## Files

```
memory_system/
├── postgres_core.py          # PostgreSQL connection & schema
├── kv_store.py               # Key-value store
├── btree_index.py            # B-Tree sorted index
├── linked_list.py            # Ordered linked list
├── graph.py                  # Directed acyclic graph
├── kanban.py                 # Kanban board
├── lessons_and_code.py       # Lessons + code ledger
├── base_transaction.py       # Base transaction class
├── memory_transaction.py     # Memory-specific transactions
├── unified_memory.py         # Unified coordinator
├── examples.py               # Usage examples
└── README.md                 # This file
```

## Scaling to 200K+ Ideas

For 200K+ ideas:
- **Workers**: 10 parallel workers, each handling 42 shards
- **Shards**: 420 total shards, 476 ideas per shard
- **Velocity**: 480 shards/day = 228,480 ideas/day
- **Completion**: ~24 hours for 200K ideas

Memory usage:
- KV Store: ~50 MB (worker status, config)
- B-Tree: ~100 MB (200K ideas with metadata)
- Kanban: ~200 MB (200K cards with status)
- Graph: ~150 MB (nodes + edges)
- Code Ledger: ~300 MB (450 implementations with metrics)
- **Total**: ~800 MB (easily fits in memory with PostgreSQL caching)

## Production Deployment

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
createdb hermes_memory

# Run initialization
python -c "
from memory_system.unified_memory import UnifiedMemorySystem
with UnifiedMemorySystem() as memory:
    memory.health_check()
"

# Start application using memory system
python run_mega_execution.py
```

## License

MIT
