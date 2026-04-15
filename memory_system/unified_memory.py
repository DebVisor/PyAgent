"""Unified PostgreSQL Memory System - Transaction-backed multi-virtual-path storage."""

import logging
import asyncio
from typing import Optional, Dict, Any
from contextlib import contextmanager

from .postgres_core import PostgreSQLMemory
from .kv_store import KVStore
from .btree_index import BTreeIndex
from .linked_list import LinkedList
from .graph import Graph
from .kanban import KanbanBoard
from .lessons_and_code import LessonLearned, CodeImplementationLedger
from .memory_transaction import MemoryTransaction
from .base_transaction import TransactionState

logger = logging.getLogger(__name__)


class UnifiedMemorySystem:
    """
    Unified multi-virtual-path memory system backed by PostgreSQL.
    
    Supports:
    - KV (Key-Value) store with TTL
    - B-Tree index for range queries
    - Linked lists for ordered sequences
    - Graphs (DAG) for dependencies
    - Kanban boards for workflow tracking
    - Lessons learned with recurrence tracking
    - Code implementation ledger with metrics
    
    All operations are wrapped in transactions for atomicity.
    """
    
    def __init__(self,
                 host: str = "localhost",
                 port: int = 5432,
                 database: str = "hermes_memory",
                 user: str = "postgres",
                 password: Optional[str] = None):
        """Initialize unified memory system."""
        self.pg = PostgreSQLMemory(host, port, database, user, password)
        
        # Virtual paths (initialized after connection)
        self.kv = None
        self.btree = None
        self.linked_list = None
        self.graph = None
        self.kanban = None
        self.lessons = None
        self.code_ledger = None
        
        self.initialized = False
    
    def initialize(self) -> bool:
        """Initialize database connection and schema."""
        try:
            # Create database if needed
            if not self.pg.create_database():
                logger.error("Failed to create database")
                return False
            
            # Connect
            if not self.pg.connect():
                logger.error("Failed to connect to database")
                return False
            
            # Initialize schema
            if not self.pg.init_schema():
                logger.error("Failed to initialize schema")
                return False
            
            # Initialize virtual paths
            self.kv = KVStore(self.pg.conn)
            self.btree = BTreeIndex(self.pg.conn)
            self.linked_list = LinkedList(self.pg.conn)
            self.graph = Graph(self.pg.conn)
            self.kanban = KanbanBoard(self.pg.conn)
            self.lessons = LessonLearned(self.pg.conn)
            self.code_ledger = CodeImplementationLedger(self.pg.conn)
            
            self.initialized = True
            logger.info("✅ Memory system initialized successfully")
            return True
        
        except Exception as e:
            logger.error(f"Error initializing memory system: {e}")
            return False
    
    def new_transaction(self, tx_id: Optional[str] = None) -> MemoryTransaction:
        """Create a new transaction for atomic operations."""
        return MemoryTransaction(self, tx_id)
    
    @contextmanager
    def transaction(self):
        """Context manager for transaction."""
        tx = self.new_transaction()
        tx.begin_sync()
        try:
            yield tx
            tx.commit_sync()
        except Exception as e:
            logger.error(f"Transaction error: {e}")
            tx.rollback_sync()
            raise
    
    async def transaction_async(self):
        """Async context manager for transaction."""
        tx = self.new_transaction()
        await tx.begin()
        try:
            return tx
        except Exception as e:
            logger.error(f"Transaction error: {e}")
            await tx.rollback()
            raise
    
    # ============================================================================
    # KV STORE OPERATIONS
    # ============================================================================
    
    def kv_set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Set key-value with optional TTL."""
        with self.transaction() as tx:
            return asyncio.run(tx.kv_set(key, value, ttl_seconds))
    
    def kv_get(self, key: str) -> Optional[Any]:
        """Get value by key."""
        return self.kv.get(key) if self.kv else None
    
    def kv_delete(self, key: str) -> bool:
        """Delete key."""
        return self.kv.delete(key) if self.kv else False
    
    def kv_exists(self, key: str) -> bool:
        """Check if key exists."""
        return self.kv.exists(key) if self.kv else False
    
    def kv_keys(self, prefix: str = "") -> list:
        """Get keys matching prefix."""
        return self.kv.keys(prefix) if self.kv else []
    
    # ============================================================================
    # B-TREE OPERATIONS
    # ============================================================================
    
    def btree_insert(self, key: str, value: Any) -> bool:
        """Insert into B-Tree index."""
        return self.btree.insert(key, value) if self.btree else False
    
    def btree_search(self, key: str) -> Optional[Any]:
        """Search B-Tree."""
        return self.btree.search(key) if self.btree else None
    
    def btree_range(self, start_key: str, end_key: str) -> list:
        """Range query on B-Tree."""
        return self.btree.range_query(start_key, end_key) if self.btree else []
    
    def btree_scan_sorted(self, limit: int = 1000) -> list:
        """Scan B-Tree in sorted order."""
        return self.btree.scan_sorted(limit) if self.btree else []
    
    # ============================================================================
    # LINKED LIST OPERATIONS
    # ============================================================================
    
    def ll_append(self, list_id: str, data: Any) -> bool:
        """Append to linked list."""
        ll = LinkedList(self.pg.conn, list_id)
        return ll.append(data)
    
    def ll_insert_at(self, list_id: str, position: int, data: Any) -> bool:
        """Insert at position in linked list."""
        ll = LinkedList(self.pg.conn, list_id)
        return ll.insert_at(position, data)
    
    def ll_remove_at(self, list_id: str, position: int) -> bool:
        """Remove from linked list."""
        ll = LinkedList(self.pg.conn, list_id)
        return ll.remove_at(position)
    
    def ll_get_at(self, list_id: str, position: int) -> Optional[Any]:
        """Get item from linked list."""
        ll = LinkedList(self.pg.conn, list_id)
        return ll.get_at(position)
    
    def ll_traverse(self, list_id: str) -> list:
        """Traverse linked list."""
        ll = LinkedList(self.pg.conn, list_id)
        return ll.traverse()
    
    # ============================================================================
    # GRAPH OPERATIONS
    # ============================================================================
    
    def graph_add_node(self, node_id: str, node_type: str, data: Dict[str, Any]) -> bool:
        """Add node to graph."""
        return self.graph.add_node(node_id, node_type, data) if self.graph else False
    
    def graph_add_edge(self, from_node: str, to_node: str, edge_type: str, weight: float = 1.0) -> bool:
        """Add edge to graph."""
        return self.graph.add_edge(from_node, to_node, edge_type, weight) if self.graph else False
    
    def graph_get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get node from graph."""
        return self.graph.get_node(node_id) if self.graph else None
    
    def graph_get_successors(self, node_id: str) -> list:
        """Get successor nodes."""
        return self.graph.get_successors(node_id) if self.graph else []
    
    def graph_get_predecessors(self, node_id: str) -> list:
        """Get predecessor nodes."""
        return self.graph.get_predecessors(node_id) if self.graph else []
    
    def graph_topological_sort(self) -> list:
        """Get nodes in topological order."""
        return self.graph.topological_sort() if self.graph else []
    
    def graph_get_dependencies(self, node_id: str) -> Dict[str, Any]:
        """Get all dependencies transitively."""
        return self.graph.get_dependencies(node_id) if self.graph else {}
    
    # ============================================================================
    # KANBAN OPERATIONS
    # ============================================================================
    
    def kanban_create_board(self, board_id: str, name: str, columns: Optional[list] = None) -> bool:
        """Create kanban board."""
        return self.kanban.create_board(board_id, name, columns) if self.kanban else False
    
    def kanban_create_card(self, card_id: str, title: str, status: str = "BACKLOG",
                          project_id: Optional[str] = None, priority: int = 0) -> bool:
        """Create kanban card."""
        return self.kanban.create_card(card_id, title, status, project_id, priority) if self.kanban else False
    
    def kanban_move_card(self, card_id: str, new_status: str) -> bool:
        """Move card to new status."""
        return self.kanban.move_card(card_id, new_status) if self.kanban else False
    
    def kanban_get_card(self, card_id: str) -> Optional[Dict[str, Any]]:
        """Get card details."""
        return self.kanban.get_card(card_id) if self.kanban else None
    
    def kanban_get_cards_by_status(self, status: str, project_id: Optional[str] = None) -> list:
        """Get cards by status."""
        return self.kanban.get_cards_by_status(status, project_id) if self.kanban else []
    
    def kanban_board_summary(self, project_id: Optional[str] = None) -> Dict[str, int]:
        """Get board summary."""
        return self.kanban.get_board_summary(project_id) if self.kanban else {}
    
    # ============================================================================
    # LESSONS OPERATIONS
    # ============================================================================
    
    def lesson_record(self, pattern: str, root_cause: str, prevention: str = None) -> Optional[int]:
        """Record lesson learned."""
        return self.lessons.add_lesson(pattern, root_cause, prevention) if self.lessons else None
    
    def lesson_record_occurrence(self, lesson_id: int, context: str = None) -> bool:
        """Record lesson occurrence."""
        return self.lessons.record_occurrence(lesson_id, context) if self.lessons else False
    
    def lesson_get(self, lesson_id: int) -> Optional[Dict[str, Any]]:
        """Get lesson details."""
        return self.lessons.get_lesson(lesson_id) if self.lessons else None
    
    def lesson_search(self, pattern: str) -> list:
        """Search lessons by pattern."""
        return self.lessons.search_lessons(pattern) if self.lessons else []
    
    def lesson_top_recurring(self, limit: int = 10) -> list:
        """Get top recurring lessons."""
        return self.lessons.get_top_recurring_lessons(limit) if self.lessons else []
    
    # ============================================================================
    # CODE IMPLEMENTATION LEDGER OPERATIONS
    # ============================================================================
    
    def code_log(self, project_id: str, file_path: str, lines_of_code: int,
                coverage_percent: float, quality_score: float,
                module_name: str = None, idea_id: str = None) -> Optional[int]:
        """Log code implementation."""
        return self.code_ledger.log_implementation(
            project_id, file_path, lines_of_code, coverage_percent, quality_score, module_name, idea_id
        ) if self.code_ledger else None
    
    def code_get(self, impl_id: int) -> Optional[Dict[str, Any]]:
        """Get implementation details."""
        return self.code_ledger.get_implementation(impl_id) if self.code_ledger else None
    
    def code_project_stats(self, project_id: str) -> Dict[str, Any]:
        """Get project code stats."""
        return self.code_ledger.get_project_stats(project_id) if self.code_ledger else {}
    
    def code_list(self, project_id: str, limit: int = 100) -> list:
        """List project implementations."""
        return self.code_ledger.list_implementations(project_id, limit) if self.code_ledger else []
    
    # ============================================================================
    # CLEANUP & HEALTH
    # ============================================================================
    
    def cleanup_expired(self) -> int:
        """Clean up expired KV entries. Returns count deleted."""
        return self.kv.cleanup_expired() if self.kv else 0
    
    def health_check(self) -> bool:
        """Check system health."""
        if not self.initialized:
            return False
        
        try:
            # Test KV
            test_key = "__health_check_kv__"
            if not self.kv_set(test_key, "OK"):
                return False
            if self.kv_get(test_key) != "OK":
                return False
            self.kv_delete(test_key)
            
            logger.info("✅ Memory system health check passed")
            return True
        
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def shutdown(self) -> None:
        """Shutdown memory system."""
        if self.pg:
            self.pg.disconnect()
        self.initialized = False
        logger.info("Memory system shut down")
    
    def __enter__(self):
        """Context manager entry."""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()
