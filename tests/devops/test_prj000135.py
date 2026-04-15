"""Tests for prj000135: Disaster Recovery Testing."""
import pytest, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from devops.disaster_recovery import DisasterRecoveryTester, RecoveryType, RecoveryStatus, DRConfig

class TestDisasterRecoveryTester:
    def test_tester_init(self):
        tester = DisasterRecoveryTester()
        assert tester is not None

    def test_create_plan(self):
        tester = DisasterRecoveryTester()
        plan = tester.create_recovery_plan("plan1", "Main Plan", 60, 120)
        assert plan.plan_id == "plan1"
        assert plan.rpo_minutes == 60

    def test_validate_plan(self):
        tester = DisasterRecoveryTester()
        plan = tester.create_recovery_plan("plan1", "Main Plan", 60, 120)
        assert tester.validate_plan("plan1") is True

    def test_execute_test(self):
        tester = DisasterRecoveryTester()
        plan = tester.create_recovery_plan("plan1", "Main Plan", 60, 120)
        test = tester.execute_test("plan1", RecoveryType.BACKUP_RESTORE)
        assert test.status == RecoveryStatus.COMPLETED

    def test_config_creation(self):
        config = DRConfig(backup_interval_hours=12)
        assert config.backup_interval_hours == 12

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
