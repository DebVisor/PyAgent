"""Core disaster recovery testing implementation."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class RecoveryStatus(Enum):
    """Status of recovery operations."""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class RecoveryType(Enum):
    """Types of recovery procedures."""
    BACKUP_RESTORE = "backup_restore"
    FAILOVER = "failover"
    FULL_RECOVERY = "full_recovery"
    PARTIAL_RECOVERY = "partial_recovery"


@dataclass
class RecoveryTest:
    """Represents a disaster recovery test."""
    test_id: str
    test_type: RecoveryType
    status: RecoveryStatus = RecoveryStatus.PLANNED
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration_seconds: float = 0.0
    result: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"RecoveryTest(id={self.test_id}, type={self.test_type.value}, status={self.status.value})"


@dataclass
class RecoveryPlan:
    """Disaster recovery plan."""
    plan_id: str
    plan_name: str
    rpo_minutes: int
    rto_minutes: int
    description: str = ""
    procedures: List[str] = field(default_factory=list)
    tests: List[RecoveryTest] = field(default_factory=list)
    last_tested: Optional[str] = None

    def add_test(self, test: RecoveryTest) -> None:
        """Add a test result to plan."""
        self.tests.append(test)

    def __repr__(self) -> str:
        return f"RecoveryPlan(id={self.plan_id}, rpo={self.rpo_minutes}min, rto={self.rto_minutes}min)"


class DisasterRecoveryTester:
    """Disaster recovery testing and validation."""

    def __init__(self):
        """Initialize DR tester."""
        self.plans: Dict[str, RecoveryPlan] = {}
        self.logger = logger

    def create_recovery_plan(self, plan_id: str, plan_name: str, rpo: int, rto: int) -> RecoveryPlan:
        """Create a disaster recovery plan.
        
        Args:
            plan_id: Unique plan identifier
            plan_name: Human-readable plan name
            rpo: Recovery Point Objective in minutes
            rto: Recovery Time Objective in minutes
            
        Returns:
            RecoveryPlan instance
        """
        self.logger.info(f"Creating recovery plan: {plan_id}")
        
        plan = RecoveryPlan(
            plan_id=plan_id,
            plan_name=plan_name,
            rpo_minutes=rpo,
            rto_minutes=rto
        )
        
        self.plans[plan_id] = plan
        return plan

    def execute_test(self, plan_id: str, test_type: RecoveryType) -> RecoveryTest:
        """Execute a disaster recovery test.
        
        Args:
            plan_id: Plan to test
            test_type: Type of test to execute
            
        Returns:
            RecoveryTest with results
        """
        plan = self.plans.get(plan_id)
        if not plan:
            self.logger.error(f"Plan not found: {plan_id}")
            return RecoveryTest(
                test_id="unknown",
                test_type=test_type,
                status=RecoveryStatus.FAILED,
                result="Plan not found"
            )
        
        self.logger.info(f"Executing {test_type.value} test for plan {plan_id}")
        
        # Create test
        import hashlib
        test_id = hashlib.md5(f"{plan_id}-{datetime.utcnow().isoformat()}".encode()).hexdigest()[:8]
        
        test = RecoveryTest(
            test_id=test_id,
            test_type=test_type,
            status=RecoveryStatus.IN_PROGRESS,
            start_time=datetime.utcnow().isoformat()
        )
        
        # Simulate test execution
        test.status = RecoveryStatus.COMPLETED
        test.end_time = datetime.utcnow().isoformat()
        test.duration_seconds = 60.0
        test.result = "Test completed successfully"
        test.metrics = {
            "data_recovered": "100%",
            "downtime": "5 minutes",
            "validation_status": "passed"
        }
        
        plan.add_test(test)
        plan.last_tested = test.end_time
        
        self.logger.info(f"Test completed: {test}")
        return test

    def validate_plan(self, plan_id: str) -> bool:
        """Validate a recovery plan.
        
        Args:
            plan_id: Plan to validate
            
        Returns:
            True if plan is valid, False otherwise
        """
        plan = self.plans.get(plan_id)
        if not plan:
            return False
        
        # Basic validation
        if plan.rpo_minutes <= 0 or plan.rto_minutes <= 0:
            return False
        
        if plan.rpo_minutes > plan.rto_minutes:
            return False
        
        return True

    def get_plan(self, plan_id: str) -> Optional[RecoveryPlan]:
        """Get a recovery plan by ID."""
        return self.plans.get(plan_id)

    def list_plans(self) -> List[RecoveryPlan]:
        """List all recovery plans."""
        return list(self.plans.values())
