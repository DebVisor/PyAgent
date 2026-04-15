"""KV Store virtual path implementation."""

import json
import pickle
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class KVStore:
    """Key-Value store backed by PostgreSQL."""
    
    def __init__(self, conn):
        """Initialize with database connection."""
        self.conn = conn
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None, metadata: Optional[Dict] = None) -> bool:
        """Set a key-value pair with optional TTL."""
        try:
            cur = self.conn.cursor()
            
            # Serialize value to bytea
            serialized_value = pickle.dumps(value)
            
            # Calculate TTL expiration
            ttl_expires_at = None
            if ttl_seconds:
                ttl_expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
            
            # Upsert
            cur.execute("""
                INSERT INTO kv_store (key, value, metadata, ttl_expires_at, updated_at)
                VALUES (%s, %s, %s, %s, NOW())
                ON CONFLICT (key) DO UPDATE SET
                    value = EXCLUDED.value,
                    metadata = EXCLUDED.metadata,
                    ttl_expires_at = EXCLUDED.ttl_expires_at,
                    updated_at = NOW()
            """, (key, serialized_value, json.dumps(metadata or {}), ttl_expires_at))
            
            self.conn.commit()
            logger.debug(f"Set KV: {key}")
            return True
        
        except Exception as e:
            logger.error(f"Error setting KV {key}: {e}")
            self.conn.rollback()
            return False
        finally:
            if cur:
                cur.close()
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value by key, checking TTL."""
        try:
            cur = self.conn.cursor()
            
            # Check TTL first
            cur.execute("""
                SELECT value FROM kv_store
                WHERE key = %s AND (ttl_expires_at IS NULL OR ttl_expires_at > NOW())
            """, (key,))
            
            result = cur.fetchone()
            
            if result:
                try:
                    return pickle.loads(result[0])
                except:
                    return result[0]
            
            return None
        
        except Exception as e:
            logger.error(f"Error getting KV {key}: {e}")
            return None
        finally:
            if cur:
                cur.close()
    
    def delete(self, key: str) -> bool:
        """Delete a key."""
        try:
            cur = self.conn.cursor()
            cur.execute("DELETE FROM kv_store WHERE key = %s", (key,))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting KV {key}: {e}")
            self.conn.rollback()
            return False
        finally:
            if cur:
                cur.close()
    
    def exists(self, key: str) -> bool:
        """Check if key exists and hasn't expired."""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT 1 FROM kv_store
                WHERE key = %s AND (ttl_expires_at IS NULL OR ttl_expires_at > NOW())
            """, (key,))
            return cur.fetchone() is not None
        except Exception as e:
            logger.error(f"Error checking KV {key}: {e}")
            return False
        finally:
            if cur:
                cur.close()
    
    def keys(self, prefix: str = "") -> list:
        """Get all keys matching prefix."""
        try:
            cur = self.conn.cursor()
            
            if prefix:
                cur.execute("""
                    SELECT key FROM kv_store
                    WHERE key LIKE %s AND (ttl_expires_at IS NULL OR ttl_expires_at > NOW())
                    ORDER BY key
                """, (f"{prefix}%",))
            else:
                cur.execute("""
                    SELECT key FROM kv_store
                    WHERE ttl_expires_at IS NULL OR ttl_expires_at > NOW()
                    ORDER BY key
                """)
            
            return [row[0] for row in cur.fetchall()]
        
        except Exception as e:
            logger.error(f"Error listing keys: {e}")
            return []
        finally:
            if cur:
                cur.close()
    
    def cleanup_expired(self) -> int:
        """Remove expired entries. Returns count deleted."""
        try:
            cur = self.conn.cursor()
            cur.execute("DELETE FROM kv_store WHERE ttl_expires_at IS NOT NULL AND ttl_expires_at < NOW()")
            self.conn.commit()
            return cur.rowcount
        except Exception as e:
            logger.error(f"Error cleaning up expired: {e}")
            self.conn.rollback()
            return 0
        finally:
            if cur:
                cur.close()
    
    def mget(self, keys: list) -> Dict[str, Any]:
        """Get multiple values at once."""
        result = {}
        for key in keys:
            value = self.get(key)
            if value is not None:
                result[key] = value
        return result
    
    def mset(self, items: Dict[str, Any]) -> bool:
        """Set multiple values at once."""
        try:
            for key, value in items.items():
                if not self.set(key, value):
                    return False
            return True
        except Exception as e:
            logger.error(f"Error in mset: {e}")
            return False
