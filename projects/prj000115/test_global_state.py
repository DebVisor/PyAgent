"""Tests for global state management."""

import pytest
import threading
import time
from datetime import datetime
from global_state import (
    GlobalState,
    StateChange,
    StateSnapshot,
    StateSubscriber
)


class TestGlobalState:
    """Test global state container."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.state = GlobalState()
    
    def test_initial_state_empty(self):
        """Test that initial state is empty."""
        assert self.state.get() == {}
    
    def test_initial_state_with_data(self):
        """Test initial state with data."""
        initial = {"user": {"name": "Alice"}}
        state = GlobalState(initial)
        
        assert state.get("user.name") == "Alice"
    
    def test_set_and_get_simple(self):
        """Test setting and getting simple values."""
        self.state.set("name", "Alice")
        assert self.state.get("name") == "Alice"
    
    def test_set_and_get_nested(self):
        """Test setting and getting nested values."""
        self.state.set("user.profile.name", "Bob")
        assert self.state.get("user.profile.name") == "Bob"
    
    def test_get_default(self):
        """Test getting non-existent value with default."""
        result = self.state.get("nonexistent", "default")
        assert result == "default"
    
    def test_get_whole_state(self):
        """Test getting whole state."""
        self.state.set("key1", "value1")
        self.state.set("key2", "value2")
        
        whole = self.state.get()
        assert "key1" in whole
        assert "key2" in whole
    
    def test_update_multiple(self):
        """Test updating multiple values."""
        updates = {
            "name": "Charlie",
            "age": 30,
            "city": "NYC"
        }
        self.state.update(updates)
        
        assert self.state.get("name") == "Charlie"
        assert self.state.get("age") == 30
        assert self.state.get("city") == "NYC"
    
    def test_delete_value(self):
        """Test deleting value."""
        self.state.set("temp", "value")
        assert self.state.get("temp") == "value"
        
        assert self.state.delete("temp") is True
        assert self.state.get("temp") is None
    
    def test_delete_nonexistent(self):
        """Test deleting non-existent value."""
        assert self.state.delete("nonexistent") is False
    
    def test_clear_state(self):
        """Test clearing state."""
        self.state.set("key1", "value1")
        self.state.set("key2", "value2")
        
        self.state.clear()
        assert self.state.get() == {}
    
    def test_state_immutability(self):
        """Test that returned state is immutable."""
        self.state.set("user.name", "Dave")
        state1 = self.state.get()
        
        # Modify returned state
        state1["user"]["name"] = "Modified"
        
        # Original should not change
        assert self.state.get("user.name") == "Dave"


class TestStateChange:
    """Test state change events."""
    
    def test_state_change_creation(self):
        """Test creating state change."""
        change = StateChange(
            timestamp=datetime.utcnow().isoformat(),
            path="user.name",
            old_value="Alice",
            new_value="Bob"
        )
        
        assert change.path == "user.name"
        assert change.old_value == "Alice"
        assert change.new_value == "Bob"
    
    def test_state_change_to_dict(self):
        """Test converting state change to dict."""
        change = StateChange(
            timestamp=datetime.utcnow().isoformat(),
            path="key",
            old_value=None,
            new_value="value"
        )
        
        d = change.to_dict()
        assert isinstance(d, dict)
        assert d["path"] == "key"


class TestStateSnapshot:
    """Test state snapshots."""
    
    def test_snapshot_creation(self):
        """Test creating snapshot."""
        snapshot = StateSnapshot(
            timestamp=datetime.utcnow().isoformat(),
            state={"key": "value"},
            change_count=5
        )
        
        assert snapshot.state == {"key": "value"}
        assert snapshot.change_count == 5
    
    def test_take_snapshot(self):
        """Test taking snapshot."""
        state = GlobalState({"user": {"name": "Eve"}})
        snapshot = state.take_snapshot()
        
        assert snapshot.state == {"user": {"name": "Eve"}}
    
    def test_restore_snapshot(self):
        """Test restoring from snapshot."""
        original_state = GlobalState({"key": "original"})
        snapshot = original_state.take_snapshot()
        
        # Modify state
        original_state.set("key", "modified")
        assert original_state.get("key") == "modified"
        
        # Restore
        original_state.restore_snapshot(snapshot)
        assert original_state.get("key") == "original"


class TestObserverPattern:
    """Test observer pattern functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.state = GlobalState()
        self.changes_received = []
    
    def observer(self, change: StateChange) -> None:
        """Observer callback."""
        self.changes_received.append(change)
    
    def test_subscribe_and_notify(self):
        """Test subscribing and receiving notifications."""
        self.state.subscribe(self.observer)
        self.state.set("key", "value")
        
        assert len(self.changes_received) == 1
        assert self.changes_received[0].path == "key"
    
    def test_unsubscribe(self):
        """Test unsubscribing."""
        self.state.subscribe(self.observer)
        self.state.unsubscribe(self.observer)
        
        self.state.set("key", "value")
        assert len(self.changes_received) == 0
    
    def test_multiple_observers(self):
        """Test multiple observers."""
        changes1 = []
        changes2 = []
        
        self.state.subscribe(lambda c: changes1.append(c))
        self.state.subscribe(lambda c: changes2.append(c))
        
        self.state.set("key", "value")
        
        assert len(changes1) == 1
        assert len(changes2) == 1
    
    def test_change_history(self):
        """Test change history."""
        self.state.set("key1", "value1")
        self.state.set("key2", "value2")
        self.state.set("key1", "new_value")
        
        history = self.state.get_change_history()
        assert len(history) == 3


class TestStateSubscriber:
    """Test StateSubscriber helper."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.state = GlobalState()
        self.subscriber = StateSubscriber(self.state)
    
    def test_subscriber_receives_changes(self):
        """Test that subscriber receives changes."""
        self.subscriber.subscribe()
        self.state.set("key", "value")
        
        assert len(self.subscriber.received_changes) == 1
    
    def test_subscriber_filter_by_path(self):
        """Test filtering changes by path."""
        self.subscriber.subscribe()
        
        self.state.set("user.name", "Alice")
        self.state.set("user.age", 30)
        self.state.set("other", "value")
        
        name_changes = self.subscriber.get_changes("user.name")
        assert len(name_changes) == 1
    
    def test_subscriber_clear_changes(self):
        """Test clearing received changes."""
        self.subscriber.subscribe()
        self.state.set("key", "value")
        
        assert len(self.subscriber.received_changes) == 1
        self.subscriber.clear_changes()
        assert len(self.subscriber.received_changes) == 0


class TestThreadSafety:
    """Test thread safety."""
    
    def test_concurrent_writes(self):
        """Test concurrent write operations."""
        state = GlobalState()
        errors = []
        
        def write_worker(thread_id):
            try:
                for i in range(100):
                    state.set(f"thread{thread_id}.counter", i)
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=write_worker, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0
