"""
prj000173 - Agent Versioning System

Implementation for Phase 1 Batch 002, Idea 073
"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class ComponentStatus(Enum):
    """Status of agent component"""
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"
    STOPPED = "stopped"


@dataclass
class ComponentConfig:
    """Configuration for Agent Versioning System"""
    name: str = "prj000173"
    timeout: float = 30.0
    max_retries: int = 3
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComponentResult:
    """Result from component execution"""
    success: bool
    data: Any
    error: Optional[str] = None
    duration_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class IComponent(ABC):
    """Interface for Agent Versioning System"""
    
    @abstractmethod
    def initialize(self, config: ComponentConfig) -> bool:
        """Initialize component"""
        pass
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> ComponentResult:
        """Execute component logic"""
        pass
    
    @abstractmethod
    def shutdown(self) -> bool:
        """Shutdown component"""
        pass
    
    @abstractmethod
    def get_status(self) -> ComponentStatus:
        """Get current status"""
        pass


class AgentVersioningSystem(IComponent):
    """Implementation of Agent Versioning System"""
    
    def __init__(self):
        self.config: Optional[ComponentConfig] = None
        self.status = ComponentStatus.IDLE
        self.execution_count = 0
        self.error_count = 0
        self._handlers: Dict[str, List[Callable]] = {}
    
    def initialize(self, config: ComponentConfig) -> bool:
        """Initialize the component"""
        try:
            self.config = config
            logger.info(f"Initializing {self.config.name}")
            self.status = ComponentStatus.IDLE
            return True
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            self.status = ComponentStatus.ERROR
            return False
    
    def execute(self, *args, **kwargs) -> ComponentResult:
        """Execute the component logic"""
        if not self.config:
            return ComponentResult(
                success=False,
                data=None,
                error="Component not initialized"
            )
        
        start = datetime.utcnow()
        try:
            self.status = ComponentStatus.RUNNING
            self.execution_count += 1
            
            results = []
            for handler in self._handlers.get('execute', []):
                results.append(handler(*args, **kwargs))
            
            duration = (datetime.utcnow() - start).total_seconds() * 1000
            
            return ComponentResult(
                success=True,
                data={"results": results},
                duration_ms=duration
            )
        
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            self.error_count += 1
            self.status = ComponentStatus.ERROR
            
            return ComponentResult(
                success=False,
                data=None,
                error=str(e),
                duration_ms=(datetime.utcnow() - start).total_seconds() * 1000
            )
        
        finally:
            self.status = ComponentStatus.IDLE
    
    def shutdown(self) -> bool:
        """Shutdown the component"""
        try:
            self.status = ComponentStatus.STOPPED
            logger.info(f"Shutting down {self.config.name if self.config else 'component'}")
            return True
        except Exception as e:
            logger.error(f"Shutdown failed: {e}")
            return False
    
    def get_status(self) -> ComponentStatus:
        """Get component status"""
        return self.status
    
    def register_handler(self, event: str, handler: Callable) -> None:
        """Register event handler"""
        if event not in self._handlers:
            self._handlers[event] = []
        self._handlers[event].append(handler)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get component metrics"""
        return {
            "name": self.config.name if self.config else "unknown",
            "status": self.status.value,
            "execution_count": self.execution_count,
            "error_count": self.error_count,
            "success_rate": (
                (self.execution_count - self.error_count) / self.execution_count
                if self.execution_count > 0 else 0.0
            )
        }
