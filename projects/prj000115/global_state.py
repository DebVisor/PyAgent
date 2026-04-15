"""Global State Management

This module provides thread-safe global state management with observer pattern.
"""

import threading
import json
from typing import Any, Dict, Callable, List, Optional, Set
from datetime import datetime
from dataclasses import dataclass, field, asdict
from copy import deepcopy


@dataclass
class StateChange:
    """Represents a state change event."""
    timestamp: str
    path: str  # Dot-notation path to changed value
    old_value: Any
    new_value: Any
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class StateSnapshot:
    """Represents a snapshot of state at a point in time."""
    timestamp: str
    state: Dict[str, Any]
    change_count: int = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "state": self.state,
            "change_count": self.change_count
        }


class GlobalState:
    """Thread-safe global state container."""
    
    def __init__(self, initial_state: Dict = None):
        self._state = initial_state or {}
        self._lock = threading.RLock()
        self._observers: List[Callable[[StateChange], None]] = []
        self._change_history: List[StateChange] = []
        self._max_history_size = 1000
    
    def get(self, path: str = None, default: Any = None) -> Any:
        """Get value from state by dot-notation path."""
        with self._lock:
            if path is None:
                return deepcopy(self._state)
            
            keys = path.split(".")
            current = self._state
            
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return default
            
            return deepcopy(current)
    
    def set(self, path: str, value: Any) -> None:
        """Set value in state by dot-notation path."""
        with self._lock:
            keys = path.split(".")
            
            # Get old value
            old_value = self.get(path)
            
            # Navigate to parent
            current = self._state
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            # Set value
            current[keys[-1]] = deepcopy(value)
            
            # Notify observers
            change = StateChange(
                timestamp=datetime.utcnow().isoformat(),
                path=path,
                old_value=old_value,
                new_value=deepcopy(value)
            )
            self._record_change(change)
            self._notify_observers(change)
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple values at once."""
        with self._lock:
            for path, value in updates.items():
                self.set(path, value)
    
    def delete(self, path: str) -> bool:
        """Delete value from state."""
        with self._lock:
            keys = path.split(".")
            current = self._state
            
            # Navigate to parent
            for key in keys[:-1]:
                if key not in current:
                    return False
                current = current[key]
            
            # Delete
            if keys[-1] in current:
                old_value = current[keys[-1]]
                del current[keys[-1]]
                
                change = StateChange(
                    timestamp=datetime.utcnow().isoformat(),
                    path=path,
                    old_value=old_value,
                    new_value=None
                )
                self._record_change(change)
                self._notify_observers(change)
                return True
            
            return False
    
    def clear(self) -> None:
        """Clear all state."""
        with self._lock:
            self._state.clear()
            self._change_history.clear()
    
    def subscribe(self, observer: Callable[[StateChange], None]) -> None:
        """Subscribe to state changes."""
        with self._lock:
            if observer not in self._observers:
                self._observers.append(observer)
    
    def unsubscribe(self, observer: Callable[[StateChange], None]) -> None:
        """Unsubscribe from state changes."""
        with self._lock:
            if observer in self._observers:
                self._observers.remove(observer)
    
    def _notify_observers(self, change: StateChange) -> None:
        """Notify all observers of state change."""
        for observer in self._observers:
            try:
                observer(change)
            except Exception:
                pass  # Ignore observer errors
    
    def _record_change(self, change: StateChange) -> None:
        """Record change in history."""
        self._change_history.append(change)
        
        # Limit history size
        if len(self._change_history) > self._max_history_size:
            self._change_history = self._change_history[-self._max_history_size:]
    
    def get_change_history(
        self,
        path: str = None,
        limit: int = None
    ) -> List[StateChange]:
        """Get change history, optionally filtered by path."""
        with self._lock:
            if path is None:
                history = self._change_history
            else:
                history = [c for c in self._change_history if c.path == path]
            
            if limit:
                history = history[-limit:]
            
            return deepcopy(history)
    
    def take_snapshot(self) -> StateSnapshot:
        """Take a snapshot of current state."""
        with self._lock:
            return StateSnapshot(
                timestamp=datetime.utcnow().isoformat(),
                state=deepcopy(self._state),
                change_count=len(self._change_history)
            )
    
    def restore_snapshot(self, snapshot: StateSnapshot) -> None:
        """Restore state from snapshot."""
        with self._lock:
            self._state = deepcopy(snapshot.state)
            # Don't restore history, only the state


class StateSubscriber:
    """Helper for managing state subscriptions."""
    
    def __init__(self, global_state: GlobalState):
        self.global_state = global_state
        self.received_changes: List[StateChange] = []
    
    def on_change(self, change: StateChange) -> None:
        """Called when state changes."""
        self.received_changes.append(change)
    
    def subscribe(self) -> None:
        """Subscribe to state changes."""
        self.global_state.subscribe(self.on_change)
    
    def unsubscribe(self) -> None:
        """Unsubscribe from state changes."""
        self.global_state.unsubscribe(self.on_change)
    
    def get_changes(self, path: str = None) -> List[StateChange]:
        """Get received changes, optionally filtered by path."""
        if path is None:
            return list(self.received_changes)
        return [c for c in self.received_changes if c.path == path]
    
    def clear_changes(self) -> None:
        """Clear received changes."""
        self.received_changes.clear()
