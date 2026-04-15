"""Distributed queue with file locks for shard coordination."""

import json
import fcntl
import os
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class DistributedQueue:
    """File-lock based distributed queue for shard coordination."""
    
    def __init__(self, queue_dir: str = "/tmp/shard_queue"):
        self.queue_dir = Path(queue_dir)
        self.queue_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.queue_dir / "queue_state.json"
        self.locks_dir = self.queue_dir / "locks"
        self.locks_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_lock_file(self, shard_id: int) -> Path:
        """Get lock file path for a shard."""
        return self.locks_dir / f"shard_{shard_id:04d}.lock"
    
    def lock_shard(self, shard_id: int, worker_id: int, timeout: int = 30) -> bool:
        """Acquire lock for a shard. Returns True if acquired."""
        lock_path = self._get_lock_file(shard_id)
        try:
            # Open in append mode to create if doesn't exist
            with open(lock_path, 'a+') as f:
                # Try non-blocking exclusive lock
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    f.truncate(0)
                    f.write(json.dumps({
                        "worker_id": worker_id,
                        "shard_id": shard_id,
                        "locked_at": str(Path.cwd() / ".")
                    }))
                    f.flush()
                    logger.info(f"Worker {worker_id} locked shard {shard_id}")
                    return True
                except IOError:
                    logger.warning(f"Worker {worker_id} failed to lock shard {shard_id} (in use)")
                    return False
        except Exception as e:
            logger.error(f"Error locking shard {shard_id}: {e}")
            return False
    
    def unlock_shard(self, shard_id: int) -> bool:
        """Release lock for a shard."""
        lock_path = self._get_lock_file(shard_id)
        try:
            if lock_path.exists():
                lock_path.unlink()
                logger.info(f"Unlocked shard {shard_id}")
                return True
            return True
        except Exception as e:
            logger.error(f"Error unlocking shard {shard_id}: {e}")
            return False
    
    def enqueue_shard(self, shard_id: int, worker_id: int) -> bool:
        """Enqueue a shard for processing by a worker."""
        state = self._load_state()
        if "queue" not in state:
            state["queue"] = {}
        
        state["queue"][str(shard_id)] = {
            "status": "PENDING",
            "worker_id": worker_id,
            "attempts": 0,
            "last_error": None
        }
        
        return self._save_state(state)
    
    def mark_shard_processing(self, shard_id: int, worker_id: int) -> bool:
        """Mark shard as currently being processed."""
        state = self._load_state()
        if str(shard_id) in state.get("queue", {}):
            state["queue"][str(shard_id)]["status"] = "PROCESSING"
            state["queue"][str(shard_id)]["attempts"] += 1
        return self._save_state(state)
    
    def mark_shard_complete(self, shard_id: int, result_path: str) -> bool:
        """Mark shard as completed."""
        state = self._load_state()
        if str(shard_id) in state.get("queue", {}):
            state["queue"][str(shard_id)]["status"] = "COMPLETE"
            state["queue"][str(shard_id)]["result_path"] = result_path
        return self._save_state(state)
    
    def mark_shard_failed(self, shard_id: int, error: str, attempt: int = 0) -> bool:
        """Mark shard as failed."""
        state = self._load_state()
        if str(shard_id) in state.get("queue", {}):
            entry = state["queue"][str(shard_id)]
            if attempt < 3:  # Max 3 retries
                entry["status"] = "PENDING"
            else:
                entry["status"] = "FAILED"
            entry["last_error"] = error
        return self._save_state(state)
    
    def get_shard_status(self, shard_id: int) -> Optional[Dict[str, Any]]:
        """Get status of a shard."""
        state = self._load_state()
        return state.get("queue", {}).get(str(shard_id))
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get overall queue statistics."""
        state = self._load_state()
        queue = state.get("queue", {})
        
        stats = {
            "total": len(queue),
            "pending": 0,
            "processing": 0,
            "complete": 0,
            "failed": 0
        }
        
        for entry in queue.values():
            status = entry.get("status", "UNKNOWN")
            if status in stats:
                stats[status.lower()] += 1
        
        return stats
    
    def _load_state(self) -> Dict[str, Any]:
        """Load queue state from file."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except:
                return {"queue": {}}
        return {"queue": {}}
    
    def _save_state(self, state: Dict[str, Any]) -> bool:
        """Save queue state to file atomically."""
        try:
            temp_file = self.state_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(state, f, indent=2)
            temp_file.replace(self.state_file)
            return True
        except Exception as e:
            logger.error(f"Error saving state: {e}")
            return False
