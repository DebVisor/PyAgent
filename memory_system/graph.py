"""Graph implementation for DAG task dependencies."""

import logging
import json
from typing import Any, Optional, List, Dict, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class Graph:
    """Directed Acyclic Graph for task dependencies and workflows."""
    
    def __init__(self, conn):
        """Initialize graph."""
        self.conn = conn
    
    def add_node(self, node_id: str, node_type: str, data: Dict[str, Any]) -> bool:
        """Add a node to the graph."""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO graph_nodes (node_id, node_type, data)
                VALUES (%s, %s, %s)
                ON CONFLICT (node_id) DO UPDATE SET
                    data = EXCLUDED.data,
                    updated_at = NOW()
            """, (node_id, node_type, json.dumps(data)))
            
            self.conn.commit()
            logger.debug(f"Graph add_node: {node_id} ({node_type})")
            return True
        
        except Exception as e:
            logger.error(f"Error adding node: {e}")
            self.conn.rollback()
            return False
        finally:
            if cur:
                cur.close()
    
    def delete_node(self, node_id: str) -> bool:
        """Delete a node and its edges."""
        try:
            cur = self.conn.cursor()
            cur.execute("DELETE FROM graph_nodes WHERE node_id = %s", (node_id,))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting node: {e}")
            self.conn.rollback()
            return False
        finally:
            if cur:
                cur.close()
    
    def add_edge(self, from_node: str, to_node: str, edge_type: str, weight: float = 1.0) -> bool:
        """Add an edge between nodes."""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO graph_edges (from_node_id, to_node_id, edge_type, weight)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (from_node_id, to_node_id, edge_type) DO UPDATE SET
                    weight = EXCLUDED.weight
            """, (from_node, to_node, edge_type, weight))
            
            self.conn.commit()
            logger.debug(f"Graph add_edge: {from_node} → {to_node} ({edge_type})")
            return True
        
        except Exception as e:
            logger.error(f"Error adding edge: {e}")
            self.conn.rollback()
            return False
        finally:
            if cur:
                cur.close()
    
    def delete_edge(self, from_node: str, to_node: str, edge_type: str) -> bool:
        """Delete an edge."""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                DELETE FROM graph_edges
                WHERE from_node_id = %s AND to_node_id = %s AND edge_type = %s
            """, (from_node, to_node, edge_type))
            
            self.conn.commit()
            return cur.rowcount > 0
        
        except Exception as e:
            logger.error(f"Error deleting edge: {e}")
            self.conn.rollback()
            return False
        finally:
            if cur:
                cur.close()
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get node data."""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT node_id, node_type, data, created_at, updated_at
                FROM graph_nodes
                WHERE node_id = %s
            """, (node_id,))
            
            result = cur.fetchone()
            if result:
                return {
                    "node_id": result[0],
                    "node_type": result[1],
                    "data": json.loads(result[2]) if isinstance(result[2], str) else result[2],
                    "created_at": result[3],
                    "updated_at": result[4]
                }
            
            return None
        
        except Exception as e:
            logger.error(f"Error getting node: {e}")
            return None
        finally:
            if cur:
                cur.close()
    
    def get_outgoing_edges(self, node_id: str) -> List[Dict[str, Any]]:
        """Get all outgoing edges from a node."""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT from_node_id, to_node_id, edge_type, weight
                FROM graph_edges
                WHERE from_node_id = %s
            """, (node_id,))
            
            return [
                {
                    "from": row[0],
                    "to": row[1],
                    "type": row[2],
                    "weight": row[3]
                }
                for row in cur.fetchall()
            ]
        
        except Exception as e:
            logger.error(f"Error getting outgoing edges: {e}")
            return []
        finally:
            if cur:
                cur.close()
    
    def get_incoming_edges(self, node_id: str) -> List[Dict[str, Any]]:
        """Get all incoming edges to a node."""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT from_node_id, to_node_id, edge_type, weight
                FROM graph_edges
                WHERE to_node_id = %s
            """, (node_id,))
            
            return [
                {
                    "from": row[0],
                    "to": row[1],
                    "type": row[2],
                    "weight": row[3]
                }
                for row in cur.fetchall()
            ]
        
        except Exception as e:
            logger.error(f"Error getting incoming edges: {e}")
            return []
        finally:
            if cur:
                cur.close()
    
    def get_successors(self, node_id: str) -> List[str]:
        """Get all successor nodes."""
        edges = self.get_outgoing_edges(node_id)
        return [edge["to"] for edge in edges]
    
    def get_predecessors(self, node_id: str) -> List[str]:
        """Get all predecessor nodes."""
        edges = self.get_incoming_edges(node_id)
        return [edge["from"] for edge in edges]
    
    def topological_sort(self) -> List[str]:
        """Return nodes in topological order (for DAG)."""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                WITH RECURSIVE topo AS (
                    -- Base: nodes with no incoming edges
                    SELECT node_id FROM graph_nodes
                    WHERE NOT EXISTS (
                        SELECT 1 FROM graph_edges WHERE to_node_id = graph_nodes.node_id
                    )
                    
                    UNION ALL
                    
                    -- Recursive: nodes whose predecessors are all in topo
                    SELECT DISTINCT gn.node_id FROM graph_nodes gn
                    WHERE NOT EXISTS (
                        SELECT 1 FROM graph_edges ge
                        WHERE ge.to_node_id = gn.node_id
                        AND ge.from_node_id NOT IN (SELECT node_id FROM topo)
                    )
                    AND gn.node_id NOT IN (SELECT node_id FROM topo)
                )
                SELECT node_id FROM topo
            """)
            
            return [row[0] for row in cur.fetchall()]
        
        except Exception as e:
            logger.error(f"Error in topological sort: {e}")
            return []
        finally:
            if cur:
                cur.close()
    
    def get_dependencies(self, node_id: str) -> Dict[str, Any]:
        """Get all dependencies (predecessors transitively)."""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                WITH RECURSIVE deps AS (
                    SELECT from_node_id, to_node_id, 1 as depth
                    FROM graph_edges
                    WHERE to_node_id = %s
                    
                    UNION ALL
                    
                    SELECT ge.from_node_id, ge.to_node_id, d.depth + 1
                    FROM graph_edges ge
                    JOIN deps d ON ge.to_node_id = d.from_node_id
                    WHERE d.depth < 10  -- prevent infinite recursion
                )
                SELECT DISTINCT from_node_id, depth FROM deps
                ORDER BY depth
            """, (node_id,))
            
            result = {}
            for row in cur.fetchall():
                dep_id, depth = row
                if depth not in result:
                    result[depth] = []
                result[depth].append(dep_id)
            
            return result
        
        except Exception as e:
            logger.error(f"Error getting dependencies: {e}")
            return {}
        finally:
            if cur:
                cur.close()
