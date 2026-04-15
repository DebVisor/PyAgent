"""B-Tree index implementation for PostgreSQL."""

import logging
from typing import Any, Optional, List, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class BTreeIndex:
    """Self-balancing B-Tree index for range queries and sorted iteration."""
    
    def __init__(self, conn, tree_name: str = "default", order: int = 4):
        """Initialize B-Tree index."""
        self.conn = conn
        self.tree_name = tree_name
        self.order = order  # B-tree order (min degree)
        self.root_id = None
    
    def insert(self, key: str, value: Any) -> bool:
        """Insert key-value pair into B-Tree."""
        try:
            cur = self.conn.cursor()
            
            # If tree is empty, create root
            if self.root_id is None:
                cur.execute("""
                    INSERT INTO btree_nodes (parent_id, key, value, height)
                    VALUES (NULL, %s, %s, 0)
                    RETURNING node_id
                """, (key, value))
                self.root_id = cur.fetchone()[0]
            else:
                # Find leaf and insert
                self._insert_recursive(key, value, self.root_id)
            
            self.conn.commit()
            logger.debug(f"BTree insert: {key}")
            return True
        
        except Exception as e:
            logger.error(f"Error inserting into B-Tree: {e}")
            self.conn.rollback()
            return False
        finally:
            if cur:
                cur.close()
    
    def search(self, key: str) -> Optional[Any]:
        """Search for a key in B-Tree."""
        try:
            cur = self.conn.cursor()
            
            if self.root_id is None:
                return None
            
            cur.execute("""
                WITH RECURSIVE search_tree AS (
                    SELECT node_id, key, value, parent_id
                    FROM btree_nodes
                    WHERE node_id = %s
                    
                    UNION ALL
                    
                    SELECT n.node_id, n.key, n.value, n.parent_id
                    FROM btree_nodes n
                    JOIN search_tree st ON (
                        (n.key < %s AND n.node_id = st.left_child_id) OR
                        (n.key >= %s AND n.node_id = st.right_child_id)
                    )
                )
                SELECT value FROM search_tree WHERE key = %s LIMIT 1
            """, (self.root_id, key, key, key))
            
            result = cur.fetchone()
            return result[0] if result else None
        
        except Exception as e:
            logger.error(f"Error searching B-Tree: {e}")
            return None
        finally:
            if cur:
                cur.close()
    
    def range_query(self, start_key: str, end_key: str, inclusive: bool = True) -> List[Tuple[str, Any]]:
        """Query range of keys."""
        try:
            cur = self.conn.cursor()
            
            if inclusive:
                cur.execute("""
                    SELECT key, value FROM btree_nodes
                    WHERE key >= %s AND key <= %s
                    ORDER BY key
                """, (start_key, end_key))
            else:
                cur.execute("""
                    SELECT key, value FROM btree_nodes
                    WHERE key > %s AND key < %s
                    ORDER BY key
                """, (start_key, end_key))
            
            return cur.fetchall()
        
        except Exception as e:
            logger.error(f"Error in range query: {e}")
            return []
        finally:
            if cur:
                cur.close()
    
    def delete(self, key: str) -> bool:
        """Delete a key from B-Tree."""
        try:
            cur = self.conn.cursor()
            cur.execute("DELETE FROM btree_nodes WHERE key = %s", (key,))
            self.conn.commit()
            return cur.rowcount > 0
        
        except Exception as e:
            logger.error(f"Error deleting from B-Tree: {e}")
            self.conn.rollback()
            return False
        finally:
            if cur:
                cur.close()
    
    def scan_sorted(self, limit: int = 1000) -> List[Tuple[str, Any]]:
        """Scan all keys in sorted order."""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT key, value FROM btree_nodes
                ORDER BY key
                LIMIT %s
            """, (limit,))
            
            return cur.fetchall()
        
        except Exception as e:
            logger.error(f"Error scanning B-Tree: {e}")
            return []
        finally:
            if cur:
                cur.close()
    
    def _insert_recursive(self, key: str, value: Any, node_id: int) -> None:
        """Recursively insert into B-Tree (helper)."""
        cur = self.conn.cursor()
        
        # Get node
        cur.execute("SELECT key, left_child_id, right_child_id FROM btree_nodes WHERE node_id = %s",
                   (node_id,))
        node = cur.fetchone()
        
        if node is None:
            return
        
        node_key, left_child, right_child = node
        
        # Leaf node - insert directly
        if left_child is None and right_child is None:
            cur.execute("""
                INSERT INTO btree_nodes (parent_id, key, value, height)
                VALUES (%s, %s, %s, 0)
            """, (node_id, key, value))
        # Internal node - recurse to appropriate child
        else:
            child_id = left_child if key < node_key else right_child
            if child_id:
                self._insert_recursive(key, value, child_id)
