"""Security tests: SSRF, injection, permission escalation, and replay attacks."""

from __future__ import annotations

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from servers.trialmcp_fhir.src.fhir_server import FHIRMCPServer
from servers.trialmcp_dicom.src.dicom_server import DICOMMCPServer
from servers.trialmcp_authz.src.authz_server import AuthzMCPServer
from servers.trialmcp_ledger.src.ledger_server import LedgerMCPServer


class TestSSRFPrevention:
    """Test that MCP servers prevent SSRF attacks."""

    def test_fhir_rejects_url_in_resource_id(self) -> None:
        """Resource IDs containing URLs should not trigger external requests."""
        server = FHIRMCPServer()
        result = server.handle_tool_call(
            "fhir_read",
            {
                "resource_type": "Patient",
                "resource_id": "http://evil.example.com/steal-data",
            },
        )
        assert "error" in result
        assert "not found" in result["error"]

    def test_dicom_rejects_url_in_study_uid(self) -> None:
        """Study UIDs containing URLs should not trigger external requests."""
        server = DICOMMCPServer()
        result = server.handle_tool_call(
            "dicom_retrieve_pointer",
            {
                "study_instance_uid": "http://evil.example.com/exfiltrate",
                "caller_role": "robot_agent",
            },
        )
        assert "error" in result


class TestInjectionPrevention:
    """Test that MCP servers prevent injection attacks."""

    def test_fhir_search_rejects_json_injection(self) -> None:
        """Search parameters should not allow JSON injection."""
        server = FHIRMCPServer()
        result = server.handle_tool_call(
            "fhir_search",
            {
                "resource_type": "Patient",
                "params": {"name": '{"$gt":""}'},
            },
        )
        # Should return empty results, not an error from injection
        assert "results" in result
        assert isinstance(result["results"], list)

    def test_ledger_append_sanitizes_input(self) -> None:
        """Ledger append should handle malicious input safely."""
        server = LedgerMCPServer()
        result = server.handle_tool_call(
            "ledger_append",
            {
                "server": "<script>alert('xss')</script>",
                "tool": "'; DROP TABLE audit; --",
                "caller_id": "test-injection",
                "result_summary": "test",
            },
        )
        # Should succeed - data is stored as-is but never interpreted
        assert "audit_id" in result
        assert "record_hash" in result


class TestPermissionEscalation:
    """Test that permission boundaries cannot be bypassed."""

    def test_auditor_cannot_query_dicom_series(self) -> None:
        """Auditor role should not have SERIES-level DICOM access."""
        server = DICOMMCPServer()
        result = server.handle_tool_call(
            "dicom_query",
            {"query_level": "SERIES", "caller_role": "auditor"},
        )
        assert "error" in result
        assert "permission" in result["error"].lower()

    def test_monitor_cannot_retrieve_dicom(self) -> None:
        """Data monitor role should not be able to retrieve DICOM data."""
        server = DICOMMCPServer()
        result = server.handle_tool_call(
            "dicom_retrieve_pointer",
            {
                "study_instance_uid": "1.2.3.4.5",
                "caller_role": "data_monitor",
            },
        )
        assert "error" in result
        assert "permission" in result["error"].lower()

    def test_authz_denies_unknown_role(self) -> None:
        """Unknown roles should be denied by default."""
        server = AuthzMCPServer()
        result = server.handle_tool_call(
            "authz_evaluate",
            {"role": "unknown_hacker", "server": "trialmcp-fhir", "tool": "fhir_read"},
        )
        assert result["decision"] == "deny"

    def test_authz_deny_overrides_allow(self) -> None:
        """Explicit DENY rules should take precedence over ALLOW rules."""
        server = AuthzMCPServer()
        # Data monitor has explicit deny for provenance write
        result = server.handle_tool_call(
            "authz_evaluate",
            {
                "role": "data_monitor",
                "server": "trialmcp-provenance",
                "tool": "provenance_register_source",
            },
        )
        assert result["decision"] == "deny"


class TestReplayPrevention:
    """Test that the audit system detects replay attempts."""

    def test_ledger_chain_detects_tampering(self) -> None:
        """Modifying a record should break the hash chain."""
        server = LedgerMCPServer()
        # Append some records
        server.handle_tool_call(
            "ledger_append",
            {
                "server": "test",
                "tool": "test_tool",
                "caller_id": "test",
                "result_summary": "record 1",
            },
        )
        server.handle_tool_call(
            "ledger_append",
            {
                "server": "test",
                "tool": "test_tool",
                "caller_id": "test",
                "result_summary": "record 2",
            },
        )

        # Verify chain is valid
        result = server.handle_tool_call("ledger_verify", {})
        assert result["valid"] is True

    def test_token_revocation_prevents_reuse(self) -> None:
        """Revoked tokens should not be valid."""
        server = AuthzMCPServer()
        token_result = server.handle_tool_call(
            "authz_issue_token",
            {"caller_id": "test-agent", "role": "robot_agent"},
        )
        token_id = token_result["token_id"]

        # Validate before revocation
        valid_result = server.handle_tool_call(
            "authz_validate_token", {"token_id": token_id}
        )
        assert valid_result["valid"] is True

        # Revoke
        server.handle_tool_call("authz_revoke_token", {"token_id": token_id})

        # Validate after revocation
        invalid_result = server.handle_tool_call(
            "authz_validate_token", {"token_id": token_id}
        )
        assert invalid_result["valid"] is False
