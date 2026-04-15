"""Kanban board for task management and status tracking."""

import logging
import json
from typing import Any, Optional, List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class KanbanBoard:
    """Kanban board with columns and cards for workflow tracking."""
    
    def __init__(self, conn):
        """Initialize kanban board."""
        self.conn = conn
        self.default_columns = ["BACKLOG", "TODO", "IN_PROGRESS", "REVIEW", "DONE"]
    
    def create_board(self, board_id: str, name: str, columns: Optional[List[str]] = None) -> bool:
        """Create a kanban board."""
        try:
            cols = columns or self.default_columns
            cur = self.conn.cursor()
            
            cur.execute("""
                INSERT INTO kanban_board (board_id, name, columns)
                VALUES (%s, %s, %s)
                ON CONFLICT (board_id) DO UPDATE SET
                    columns = EXCLUDED.columns,
                    updated_at = NOW()
            """, (board_id, name, json.dumps(cols)))
            
            self.conn.commit()
            logger.info(f"Created kanban board: {board_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error creating board: {e}")
            self.conn.rollback()
            return False
        finally:
            if cur:
                cur.close()
    
    def create_card(self, card_id: str, title: str, status: str = "BACKLOG",
                   project_id: Optional[str] = None, priority: int = 0) -> bool:
        """Create a kanban card."""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO kanban_cards (card_id, title, status, project_id, priority)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (card_id) DO UPDATE SET
                    title = EXCLUDED.title,
                    status = EXCLUDED.status,
                    updated_at = NOW()
            """, (card_id, title, status, project_id, priority))
            
            self.conn.commit()
            logger.debug(f"Created kanban card: {card_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error creating card: {e}")
            self.conn.rollback()
            return False
        finally:
            if cur:
                cur.close()
    
    def move_card(self, card_id: str, new_status: str) -> bool:
        """Move card to different status/column."""
        try:
            cur = self.conn.cursor()
            
            # Mark as completed if moved to DONE
            completed_at = datetime.now() if new_status == "DONE" else None
            
            cur.execute("""
                UPDATE kanban_cards
                SET status = %s, updated_at = NOW(), completed_at = %s
                WHERE card_id = %s
            """, (new_status, completed_at, card_id))
            
            self.conn.commit()
            logger.debug(f"Moved card {card_id} → {new_status}")
            return cur.rowcount > 0
        
        except Exception as e:
            logger.error(f"Error moving card: {e}")
            self.conn.rollback()
            return False
        finally:
            if cur:
                cur.close()
    
    def get_card(self, card_id: str) -> Optional[Dict[str, Any]]:
        """Get card details."""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT card_id, title, description, status, priority, assignee,
                       project_id, created_at, updated_at, completed_at
                FROM kanban_cards
                WHERE card_id = %s
            """, (card_id,))
            
            result = cur.fetchone()
            if result:
                return {
                    "card_id": result[0],
                    "title": result[1],
                    "description": result[2],
                    "status": result[3],
                    "priority": result[4],
                    "assignee": result[5],
                    "project_id": result[6],
                    "created_at": result[7],
                    "updated_at": result[8],
                    "completed_at": result[9]
                }
            
            return None
        
        except Exception as e:
            logger.error(f"Error getting card: {e}")
            return None
        finally:
            if cur:
                cur.close()
    
    def get_card_status(self, card_id: str) -> Optional[str]:
        """Get card's current status."""
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT status FROM kanban_cards WHERE card_id = %s", (card_id,))
            result = cur.fetchone()
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error getting card status: {e}")
            return None
        finally:
            if cur:
                cur.close()
    
    def delete_card(self, card_id: str) -> bool:
        """Delete a card."""
        try:
            cur = self.conn.cursor()
            cur.execute("DELETE FROM kanban_cards WHERE card_id = %s", (card_id,))
            self.conn.commit()
            return cur.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting card: {e}")
            self.conn.rollback()
            return False
        finally:
            if cur:
                cur.close()
    
    def get_cards_by_status(self, status: str, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all cards with specific status."""
        try:
            cur = self.conn.cursor()
            
            if project_id:
                cur.execute("""
                    SELECT card_id, title, priority, assignee, created_at
                    FROM kanban_cards
                    WHERE status = %s AND project_id = %s
                    ORDER BY priority DESC, created_at
                """, (status, project_id))
            else:
                cur.execute("""
                    SELECT card_id, title, priority, assignee, created_at
                    FROM kanban_cards
                    WHERE status = %s
                    ORDER BY priority DESC, created_at
                """, (status,))
            
            return [
                {
                    "card_id": row[0],
                    "title": row[1],
                    "priority": row[2],
                    "assignee": row[3],
                    "created_at": row[4]
                }
                for row in cur.fetchall()
            ]
        
        except Exception as e:
            logger.error(f"Error getting cards by status: {e}")
            return []
        finally:
            if cur:
                cur.close()
    
    def get_board_summary(self, project_id: Optional[str] = None) -> Dict[str, int]:
        """Get summary of cards by status."""
        try:
            cur = self.conn.cursor()
            
            if project_id:
                cur.execute("""
                    SELECT status, COUNT(*) as count
                    FROM kanban_cards
                    WHERE project_id = %s
                    GROUP BY status
                """, (project_id,))
            else:
                cur.execute("""
                    SELECT status, COUNT(*) as count
                    FROM kanban_cards
                    GROUP BY status
                """)
            
            return {row[0]: row[1] for row in cur.fetchall()}
        
        except Exception as e:
            logger.error(f"Error getting board summary: {e}")
            return {}
        finally:
            if cur:
                cur.close()
    
    def assign_card(self, card_id: str, assignee: str) -> bool:
        """Assign card to a person."""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                UPDATE kanban_cards
                SET assignee = %s, updated_at = NOW()
                WHERE card_id = %s
            """, (assignee, card_id))
            
            self.conn.commit()
            return cur.rowcount > 0
        
        except Exception as e:
            logger.error(f"Error assigning card: {e}")
            self.conn.rollback()
            return False
        finally:
            if cur:
                cur.close()
    
    def set_priority(self, card_id: str, priority: int) -> bool:
        """Set card priority."""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                UPDATE kanban_cards
                SET priority = %s, updated_at = NOW()
                WHERE card_id = %s
            """, (priority, card_id))
            
            self.conn.commit()
            return cur.rowcount > 0
        
        except Exception as e:
            logger.error(f"Error setting priority: {e}")
            self.conn.rollback()
            return False
        finally:
            if cur:
                cur.close()
