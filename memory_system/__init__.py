"""
PostgreSQL-backed Unified Memory System for parallel execution tracking.

Provides multiple virtual path data structures:
- KVStore: Fast O(1) lookups with TTL support
- BTreeIndex: Sorted range queries and iteration
- LinkedList: Ordered sequences and timeline tracking
- Graph: DAG for task dependencies
- KanbanBoard: Workflow tracking (BACKLOG→DONE)
- LessonLearned: Pattern tracking and prevention
- CodeImplementationLedger: Code metrics and tracking
- MemoryTransaction: ACID transactions with savepoints
"""

from .unified_memory import UnifiedMemorySystem
from .base_transaction import BaseTransaction, TransactionState
from .memory_transaction import MemoryTransaction
from .kv_store import KVStore
from .btree_index import BTreeIndex
from .linked_list import LinkedList
from .graph import Graph
from .kanban import KanbanBoard
from .lessons_and_code import LessonLearned, CodeImplementationLedger

__version__ = "1.0.0"
__author__ = "Hermes Agent"
__all__ = [
    "UnifiedMemorySystem",
    "BaseTransaction",
    "TransactionState",
    "MemoryTransaction",
    "KVStore",
    "BTreeIndex",
    "LinkedList",
    "Graph",
    "KanbanBoard",
    "LessonLearned",
    "CodeImplementationLedger",
]
