"""Linked list implementation for PostgreSQL."""

import logging
from typing import Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class LinkedList:
    """Ordered linked list with insertion/deletion operations."""
    
    def __init__(self, conn, list_id: str = "default"):
        """Initialize linked list."""
        self.conn = conn
        self.list_id = list_id
        self.head_id = None
        self.tail_id = None
        self.length = 0
    
    def append(self, data: Any) -> bool:
        """Append item to end of list."""
        try:
            cur = self.conn.cursor()
            
            # Insert new node
            cur.execute("""
                INSERT INTO linked_list_nodes (list_id, data, prev_node_id, next_node_id, position)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING node_id
            """, (self.list_id, data, self.tail_id, None, self.length))
            
            new_node_id = cur.fetchone()[0]
            
            # Update previous tail's next pointer
            if self.tail_id is not None:
                cur.execute("""
                    UPDATE linked_list_nodes SET next_node_id = %s
                    WHERE node_id = %s
                """, (new_node_id, self.tail_id))
            
            # Update head if first element
            if self.head_id is None:
                self.head_id = new_node_id
            
            self.tail_id = new_node_id
            self.length += 1
            
            self.conn.commit()
            logger.debug(f"LinkedList append: {self.list_id}[{self.length-1}]")
            return True
        
        except Exception as e:
            logger.error(f"Error appending to linked list: {e}")
            self.conn.rollback()
            return False
        finally:
            if cur:
                cur.close()
    
    def insert_at(self, position: int, data: Any) -> bool:
        """Insert item at specific position."""
        try:
            cur = self.conn.cursor()
            
            if position < 0 or position > self.length:
                logger.error(f"Position {position} out of range [0, {self.length}]")
                return False
            
            # Find node at position
            cur.execute("""
                SELECT node_id, prev_node_id, next_node_id FROM linked_list_nodes
                WHERE list_id = %s AND position = %s
            """, (self.list_id, position))
            
            result = cur.fetchone()
            next_node_id = result[0] if result else None
            prev_node_id = result[1] if result else self.tail_id
            
            # Insert new node
            cur.execute("""
                INSERT INTO linked_list_nodes (list_id, data, prev_node_id, next_node_id, position)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING node_id
            """, (self.list_id, data, prev_node_id, next_node_id, position))
            
            new_node_id = cur.fetchone()[0]
            
            # Update prev node's next
            if prev_node_id:
                cur.execute("""
                    UPDATE linked_list_nodes SET next_node_id = %s
                    WHERE node_id = %s
                """, (new_node_id, prev_node_id))
            
            # Update next node's prev
            if next_node_id:
                cur.execute("""
                    UPDATE linked_list_nodes SET prev_node_id = %s
                    WHERE node_id = %s
                """, (new_node_id, next_node_id))
            
            # Increment positions after insertion
            cur.execute("""
                UPDATE linked_list_nodes SET position = position + 1
                WHERE list_id = %s AND position >= %s AND node_id != %s
            """, (self.list_id, position, new_node_id))
            
            self.length += 1
            self.conn.commit()
            logger.debug(f"LinkedList insert_at {position}: {self.list_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error inserting at position: {e}")
            self.conn.rollback()
            return False
        finally:
            if cur:
                cur.close()
    
    def remove_at(self, position: int) -> bool:
        """Remove item at position."""
        try:
            cur = self.conn.cursor()
            
            if position < 0 or position >= self.length:
                return False
            
            # Find node
            cur.execute("""
                SELECT node_id, prev_node_id, next_node_id FROM linked_list_nodes
                WHERE list_id = %s AND position = %s
            """, (self.list_id, position))
            
            result = cur.fetchone()
            if not result:
                return False
            
            node_id, prev_node_id, next_node_id = result
            
            # Update prev node
            if prev_node_id:
                cur.execute("""
                    UPDATE linked_list_nodes SET next_node_id = %s
                    WHERE node_id = %s
                """, (next_node_id, prev_node_id))
            else:
                self.head_id = next_node_id
            
            # Update next node
            if next_node_id:
                cur.execute("""
                    UPDATE linked_list_nodes SET prev_node_id = %s
                    WHERE node_id = %s
                """, (prev_node_id, next_node_id))
            else:
                self.tail_id = prev_node_id
            
            # Delete node
            cur.execute("DELETE FROM linked_list_nodes WHERE node_id = %s", (node_id,))
            
            # Decrement positions after deletion
            cur.execute("""
                UPDATE linked_list_nodes SET position = position - 1
                WHERE list_id = %s AND position > %s
            """, (self.list_id, position))
            
            self.length -= 1
            self.conn.commit()
            logger.debug(f"LinkedList remove_at {position}: {self.list_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error removing from list: {e}")
            self.conn.rollback()
            return False
        finally:
            if cur:
                cur.close()
    
    def get_at(self, position: int) -> Optional[Any]:
        """Get item at position."""
        try:
            cur = self.conn.cursor()
            
            if position < 0 or position >= self.length:
                return None
            
            cur.execute("""
                SELECT data FROM linked_list_nodes
                WHERE list_id = %s AND position = %s
            """, (self.list_id, position))
            
            result = cur.fetchone()
            return result[0] if result else None
        
        except Exception as e:
            logger.error(f"Error getting item: {e}")
            return None
        finally:
            if cur:
                cur.close()
    
    def traverse(self) -> List[Any]:
        """Traverse entire list in order."""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT data FROM linked_list_nodes
                WHERE list_id = %s
                ORDER BY position
            """, (self.list_id,))
            
            return [row[0] for row in cur.fetchall()]
        
        except Exception as e:
            logger.error(f"Error traversing list: {e}")
            return []
        finally:
            if cur:
                cur.close()
    
    def reverse_traverse(self) -> List[Any]:
        """Traverse list in reverse order."""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT data FROM linked_list_nodes
                WHERE list_id = %s
                ORDER BY position DESC
            """, (self.list_id,))
            
            return [row[0] for row in cur.fetchall()]
        
        except Exception as e:
            logger.error(f"Error reverse traversing: {e}")
            return []
        finally:
            if cur:
                cur.close()
