"""Memory transaction for atomic KV/graph operations on PostgreSQL."""

import logging
from typing import Any, Optional, Dict
from .base_transaction import BaseTransaction, TransactionState

logger = logging.getLogger(__name__)


class MemoryTransaction(BaseTransaction):
    """Atomic transaction for memory operations (KV, graph, kanban, etc)."""
    
    def __init__(self, pg_memory, tx_id: Optional[str] = None, timeout_seconds: int = 300):
        """Initialize memory transaction."""
        super().__init__(tx_id, timeout_seconds)
        self.pg_memory = pg_memory
        self.conn = pg_memory.conn
        
        # Track changes for rollback
        self.kv_changes: Dict[str, Any] = {}
        self.graph_changes: Dict[str, Any] = {}
        self.kanban_changes: Dict[str, Any] = {}
    
    async def kv_set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Set KV with transaction tracking."""
        try:
            # Store old value for rollback
            old_value = self.pg_memory.kv.get(key)
            self.kv_changes[key] = {"old": old_value, "new": value}
            
            # Perform operation
            result = self.pg_memory.kv.set(key, value, ttl_seconds)
            
            if result:
                self.record_operation("kv_set", {"key": key, "old": old_value})
            
            return result
        except Exception as e:
            logger.error(f"Error in kv_set: {e}")
            return False
    
    async def kv_delete(self, key: str) -> bool:
        """Delete KV with transaction tracking."""
        try:
            old_value = self.pg_memory.kv.get(key)
            self.kv_changes[key] = {"old": old_value, "new": None}
            
            result = self.pg_memory.kv.delete(key)
            
            if result:
                self.record_operation("kv_delete", {"key": key, "old": old_value})
            
            return result
        except Exception as e:
            logger.error(f"Error in kv_delete: {e}")
            return False
    
    async def graph_add_node(self, node_id: str, node_type: str, data: Dict) -> bool:
        """Add graph node with transaction tracking."""
        try:
            result = self.pg_memory.graph.add_node(node_id, node_type, data)
            
            if result:
                self.record_operation("graph_add_node", {"node_id": node_id, "type": node_type})
                self.graph_changes[node_id] = {"action": "add"}
            
            return result
        except Exception as e:
            logger.error(f"Error adding graph node: {e}")
            return False
    
    async def graph_add_edge(self, from_node: str, to_node: str, edge_type: str, weight: float = 1.0) -> bool:
        """Add graph edge with transaction tracking."""
        try:
            result = self.pg_memory.graph.add_edge(from_node, to_node, edge_type, weight)
            
            if result:
                self.record_operation("graph_add_edge", {
                    "from": from_node,
                    "to": to_node,
                    "type": edge_type
                })
                edge_key = f"{from_node}→{to_node}:{edge_type}"
                self.graph_changes[edge_key] = {"action": "add"}
            
            return result
        except Exception as e:
            logger.error(f"Error adding graph edge: {e}")
            return False
    
    async def kanban_create_card(self, card_id: str, title: str, status: str = "BACKLOG", 
                                 project_id: Optional[str] = None) -> bool:
        """Create kanban card with transaction tracking."""
        try:
            result = self.pg_memory.kanban.create_card(card_id, title, status, project_id)
            
            if result:
                self.record_operation("kanban_create_card", {"card_id": card_id, "status": status})
                self.kanban_changes[card_id] = {"action": "create", "status": status}
            
            return result
        except Exception as e:
            logger.error(f"Error creating kanban card: {e}")
            return False
    
    async def kanban_move_card(self, card_id: str, new_status: str) -> bool:
        """Move kanban card with transaction tracking."""
        try:
            old_status = self.pg_memory.kanban.get_card_status(card_id)
            result = self.pg_memory.kanban.move_card(card_id, new_status)
            
            if result:
                self.record_operation("kanban_move_card", {
                    "card_id": card_id,
                    "from": old_status,
                    "to": new_status
                })
                self.kanban_changes[card_id] = {"action": "move", "from": old_status, "to": new_status}
            
            return result
        except Exception as e:
            logger.error(f"Error moving kanban card: {e}")
            return False
    
    async def lesson_record(self, pattern: str, root_cause: str, prevention: str = None) -> bool:
        """Record a lesson learned with transaction tracking."""
        try:
            lesson_id = self.pg_memory.lessons.add_lesson(pattern, root_cause, prevention)
            
            if lesson_id:
                self.record_operation("lesson_record", {
                    "lesson_id": lesson_id,
                    "pattern": pattern
                })
            
            return lesson_id is not None
        except Exception as e:
            logger.error(f"Error recording lesson: {e}")
            return False
    
    async def code_log_implementation(self, project_id: str, file_path: str, lines_of_code: int,
                                     coverage_percent: float, quality_score: float) -> bool:
        """Log code implementation with transaction tracking."""
        try:
            impl_id = self.pg_memory.code_ledger.log_implementation(
                project_id, file_path, lines_of_code, coverage_percent, quality_score
            )
            
            if impl_id:
                self.record_operation("code_log", {
                    "impl_id": impl_id,
                    "project_id": project_id,
                    "loc": lines_of_code
                })
            
            return impl_id is not None
        except Exception as e:
            logger.error(f"Error logging implementation: {e}")
            return False
    
    async def commit(self) -> bool:
        """Commit all memory changes."""
        try:
            # Database transaction is already committed at operation time
            # This just marks transaction as complete
            await super().commit()
            logger.info(f"MemoryTransaction {self.tx_id} committed: "
                       f"KV={len(self.kv_changes)}, Graph={len(self.graph_changes)}, "
                       f"Kanban={len(self.kanban_changes)}")
            return True
        except Exception as e:
            logger.error(f"Error committing MemoryTransaction: {e}")
            return False
    
    async def rollback(self) -> bool:
        """Rollback all memory changes."""
        try:
            # Rollback KV changes
            for key, changes in self.kv_changes.items():
                if changes["new"] is None and changes["old"] is not None:
                    # Was deleted, restore it
                    self.pg_memory.kv.set(key, changes["old"])
                elif changes["old"] is None and changes["new"] is not None:
                    # Was created, delete it
                    self.pg_memory.kv.delete(key)
                else:
                    # Was modified, restore old value
                    self.pg_memory.kv.set(key, changes["old"])
            
            # Rollback graph changes
            for change_key, change_info in self.graph_changes.items():
                if change_info["action"] == "add":
                    if "→" in change_key:
                        # It's an edge
                        from_node, to_info = change_key.split("→")
                        to_node, edge_type = to_info.rsplit(":", 1)
                        self.pg_memory.graph.delete_edge(from_node, to_node, edge_type)
                    else:
                        # It's a node
                        self.pg_memory.graph.delete_node(change_key)
            
            # Rollback kanban changes
            for card_id, change_info in self.kanban_changes.items():
                if change_info["action"] == "create":
                    self.pg_memory.kanban.delete_card(card_id)
                elif change_info["action"] == "move":
                    self.pg_memory.kanban.move_card(card_id, change_info["from"])
            
            await super().rollback()
            logger.info(f"MemoryTransaction {self.tx_id} rolled back")
            return True
        except Exception as e:
            logger.error(f"Error rolling back MemoryTransaction: {e}")
            return False
