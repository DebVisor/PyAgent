"""Base transaction class for atomic operations."""

import asyncio
import logging
from typing import Any, Callable, Optional, Dict
from datetime import datetime
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class TransactionState(Enum):
    """Transaction lifecycle states."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMMITTED = "COMMITTED"
    ROLLED_BACK = "ROLLED_BACK"
    FAILED = "FAILED"


class BaseTransaction:
    """Base class for all transaction types (Storage, Memory, Process, Context)."""
    
    def __init__(self, tx_id: Optional[str] = None, timeout_seconds: int = 300):
        """Initialize transaction."""
        self.tx_id = tx_id or str(uuid.uuid4())
        self.state = TransactionState.PENDING
        self.timeout_seconds = timeout_seconds
        self.start_time = None
        self.end_time = None
        self.operations: list = []
        self.savepoints: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.begin()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
    
    def __enter__(self):
        """Sync context manager entry."""
        self.begin_sync()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Sync context manager exit."""
        if exc_type:
            self.rollback_sync()
        else:
            self.commit_sync()
    
    async def begin(self) -> bool:
        """Start transaction."""
        self.state = TransactionState.IN_PROGRESS
        self.start_time = datetime.now()
        logger.info(f"Transaction {self.tx_id} started")
        return True
    
    def begin_sync(self) -> bool:
        """Start transaction (sync version)."""
        self.state = TransactionState.IN_PROGRESS
        self.start_time = datetime.now()
        logger.info(f"Transaction {self.tx_id} started")
        return True
    
    async def commit(self) -> bool:
        """Commit transaction."""
        self.state = TransactionState.COMMITTED
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        logger.info(f"Transaction {self.tx_id} committed ({duration:.2f}s, {len(self.operations)} ops)")
        return True
    
    def commit_sync(self) -> bool:
        """Commit transaction (sync version)."""
        self.state = TransactionState.COMMITTED
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        logger.info(f"Transaction {self.tx_id} committed ({duration:.2f}s, {len(self.operations)} ops)")
        return True
    
    async def rollback(self) -> bool:
        """Rollback transaction."""
        self.state = TransactionState.ROLLED_BACK
        self.end_time = datetime.now()
        logger.warning(f"Transaction {self.tx_id} rolled back ({len(self.operations)} ops undone)")
        
        # Rollback operations in reverse order
        for op in reversed(self.operations):
            await self._undo_operation(op)
        
        self.operations.clear()
        return True
    
    def rollback_sync(self) -> bool:
        """Rollback transaction (sync version)."""
        self.state = TransactionState.ROLLED_BACK
        self.end_time = datetime.now()
        logger.warning(f"Transaction {self.tx_id} rolled back ({len(self.operations)} ops undone)")
        
        # Rollback operations in reverse order
        for op in reversed(self.operations):
            self._undo_operation_sync(op)
        
        self.operations.clear()
        return True
    
    def savepoint(self, name: str) -> bool:
        """Create a savepoint within the transaction."""
        self.savepoints[name] = {
            "operations_count": len(self.operations),
            "timestamp": datetime.now()
        }
        logger.info(f"Savepoint '{name}' created in transaction {self.tx_id}")
        return True
    
    def rollback_to_savepoint(self, name: str) -> bool:
        """Rollback to a named savepoint."""
        if name not in self.savepoints:
            logger.error(f"Savepoint '{name}' not found")
            return False
        
        sp = self.savepoints[name]
        ops_to_undo = len(self.operations) - sp["operations_count"]
        
        for _ in range(ops_to_undo):
            if self.operations:
                op = self.operations.pop()
                self._undo_operation_sync(op)
        
        logger.info(f"Rolled back to savepoint '{name}' ({ops_to_undo} ops undone)")
        return True
    
    async def _undo_operation(self, op: Dict) -> None:
        """Undo an operation (async). Override in subclasses."""
        pass
    
    def _undo_operation_sync(self, op: Dict) -> None:
        """Undo an operation (sync). Override in subclasses."""
        pass
    
    def record_operation(self, op_type: str, data: Any, undo_fn: Optional[Callable] = None) -> None:
        """Record an operation for potential rollback."""
        op = {
            "type": op_type,
            "data": data,
            "undo_fn": undo_fn,
            "timestamp": datetime.now()
        }
        self.operations.append(op)
    
    def get_status(self) -> Dict[str, Any]:
        """Get transaction status."""
        return {
            "tx_id": self.tx_id,
            "state": self.state.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "operations_count": len(self.operations),
            "savepoints": list(self.savepoints.keys())
        }
