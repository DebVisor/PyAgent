#!/usr/bin/env python3
"""Integration tests for secret scanning pipeline."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from src.security.secret_scan_service import SecretScanService


class TestSecretScanningIntegration:
    """Test pre-commit and CI/CD integration points."""

    def setup_method(self) -> None:
        """Initialize test fixtures."""
        self.service = SecretScanService()

    def test_scan_service_finds_no_secrets_in_clean_code(self) -> None:
        """Test that SecretScanService returns PASS when no secrets detected."""
        report = self.service.scan_tree(findings=[])
        assert report.status == "PASS"
        assert len(report.findings) == 0

    def test_scan_service_finds_secrets_in_compromised_code(self) -> None:
        """Test that SecretScanService returns FAIL when secrets detected."""
        findings = [
            {
                "fingerprint": "secret123",
                "secret_type": "Private Key",
                "line": 42,
            },
        ]
        report = self.service.scan_tree(findings=findings)
        assert report.status == "FAIL"
        assert len(report.findings) == 1

    def test_scan_profiles_normalize_findings(self) -> None:
        """Test that findings are normalized across all profiles."""
        findings = [
            {"fingerprint": "z-secret", "secret_type": "AWS"},
            {"fingerprint": "a-secret", "secret_type": "GitHub"},
        ]

        tree_report = self.service.scan_tree(findings=findings)
        assert tree_report.findings[0]["fingerprint"] == "a-secret"
        assert tree_report.findings[1]["fingerprint"] == "z-secret"

    def test_scan_service_error_handling(self) -> None:
        """Test that SecretScanService handles errors gracefully."""
        with patch.object(
            self.service,
            "_execute_profile",
            side_effect=RuntimeError("Scan failed"),
        ):
            report = self.service.scan_history()
            assert report.status == "ERROR"
            assert report.blocking is True
            assert "Scan failed" in report.error_message

    def test_ci_cd_integration_failure_on_findings(self) -> None:
        """Test CI/CD behavior: should fail if secrets are found."""
        findings = [{"fingerprint": "detected-key", "secret_type": "API Key"}]
        report = self.service.scan_refs(findings=findings)

        # CI/CD workflow should fail
        assert report.status == "FAIL"
        assert not report.blocking  # Non-blocking unless critical

    def test_pre_commit_hook_report_format(self) -> None:
        """Test that report format is suitable for pre-commit output."""
        findings = [
            {
                "fingerprint": "secret1",
                "secret_type": "Private Key",
                "line": 10,
                "file": "src/config.py",
            },
        ]
        report = self.service.scan_tree(findings=findings)

        # Report should be serializable for logging
        report_dict = {
            "status": report.status,
            "findings_count": len(report.findings),
            "run_id": report.run_id,
        }
        assert json.dumps(report_dict) is not None

    def test_multiple_scan_profiles(self) -> None:
        """Test all three scan profiles (tree, refs, history)."""
        findings = [{"fingerprint": "test-secret", "secret_type": "Token"}]

        tree = self.service.scan_tree(findings=findings)
        refs = self.service.scan_refs(findings=findings)
        history = self.service.scan_history(findings=findings)

        assert tree.status == "FAIL"
        assert refs.status == "FAIL"
        assert history.status == "FAIL"

    def test_empty_findings_pass(self) -> None:
        """Test that all profiles pass with no findings."""
        tree = self.service.scan_tree(findings=[])
        refs = self.service.scan_refs(findings=[])
        history = self.service.scan_history(findings=[])

        assert tree.status == "PASS"
        assert refs.status == "PASS"
        assert history.status == "PASS"


class TestSecretScanningReferenceIntegration:
    """Test that integration correctly references existing code."""

    def test_service_uses_existing_scan_report_model(self) -> None:
        """Verify integration uses existing ScanReport model."""
        from src.security.models.scan_report import ScanReport

        service = SecretScanService()
        report = service.scan_tree()
        assert isinstance(report, ScanReport)

    def test_scan_tree_profile_returns_valid_report(self) -> None:
        """Test tree profile returns valid ScanReport."""
        service = SecretScanService()
        report = service.scan_tree()
        assert hasattr(report, "status")
        assert hasattr(report, "findings")
        assert hasattr(report, "run_id")

    def test_scan_refs_profile_returns_valid_report(self) -> None:
        """Test refs profile returns valid ScanReport."""
        service = SecretScanService()
        report = service.scan_refs()
        assert hasattr(report, "status")
        assert hasattr(report, "findings")
        assert hasattr(report, "run_id")

    def test_scan_history_profile_returns_valid_report(self) -> None:
        """Test history profile returns valid ScanReport."""
        service = SecretScanService()
        report = service.scan_history()
        assert hasattr(report, "status")
        assert hasattr(report, "findings")
        assert hasattr(report, "run_id")

    def test_normalize_finding_keys_determinism(self) -> None:
        """Test that finding normalization is deterministic."""
        service = SecretScanService()
        findings1 = [
            {"fingerprint": "z"},
            {"fingerprint": "a"},
            {"fingerprint": "m"},
        ]
        findings2 = [
            {"fingerprint": "m"},
            {"fingerprint": "z"},
            {"fingerprint": "a"},
        ]

        normalized1 = service.normalize_finding_keys(findings1)
        normalized2 = service.normalize_finding_keys(findings2)

        assert normalized1 == normalized2
        assert [f["fingerprint"] for f in normalized1] == ["a", "m", "z"]
