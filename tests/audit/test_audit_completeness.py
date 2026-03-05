"""Audit completeness tests: every MCP call produces a signed audit record."""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from servers.trialmcp_fhir.src.fhir_server import FHIRMCPServer
from servers.trialmcp_dicom.src.dicom_server import DICOMMCPServer
from servers.trialmcp_ledger.src.ledger_server import LedgerMCPServer
from servers.trialmcp_provenance.src.provenance_server import ProvenanceMCPServer


class TestFHIRAuditCompleteness:
    """Every FHIR MCP tool call must produce an audit record."""

    def setup_method(self) -> None:
        self.audit_records: list[dict] = []
        self.server = FHIRMCPServer(audit_callback=self.audit_records.append)

    def test_fhir_read_produces_audit(self) -> None:
        self.server.handle_tool_call(
            "fhir_read", {"resource_type": "Patient", "resource_id": "patient-001"}
        )
        assert len(self.audit_records) == 1
        record = self.audit_records[0]
        assert record["server"] == "trialmcp-fhir"
        assert record["tool"] == "fhir_read"
        assert "audit_id" in record
        assert "timestamp" in record

    def test_fhir_search_produces_audit(self) -> None:
        self.server.handle_tool_call(
            "fhir_search", {"resource_type": "Observation"}
        )
        assert len(self.audit_records) == 1
        assert self.audit_records[0]["tool"] == "fhir_search"

    def test_fhir_patient_lookup_produces_audit(self) -> None:
        self.server.handle_tool_call(
            "fhir_patient_lookup", {"patient_id": "patient-001"}
        )
        assert len(self.audit_records) == 1
        assert self.audit_records[0]["tool"] == "fhir_patient_lookup"

    def test_fhir_study_status_produces_audit(self) -> None:
        self.server.handle_tool_call(
            "fhir_study_status", {"study_id": "ONCO-TRIAL-2026-001"}
        )
        assert len(self.audit_records) == 1
        assert self.audit_records[0]["tool"] == "fhir_study_status"


class TestDICOMAuditCompleteness:
    """Every DICOM MCP tool call must produce an audit record."""

    def setup_method(self) -> None:
        self.audit_records: list[dict] = []
        self.server = DICOMMCPServer(audit_callback=self.audit_records.append)

    def test_dicom_query_produces_audit(self) -> None:
        self.server.handle_tool_call(
            "dicom_query", {"query_level": "STUDY", "caller_role": "trial_coordinator"}
        )
        assert len(self.audit_records) == 1
        assert self.audit_records[0]["server"] == "trialmcp-dicom"
        assert self.audit_records[0]["tool"] == "dicom_query"

    def test_dicom_permission_denied_produces_audit(self) -> None:
        """Even denied requests must produce audit records."""
        self.server.handle_tool_call(
            "dicom_query", {"query_level": "SERIES", "caller_role": "auditor"}
        )
        assert len(self.audit_records) == 1
        assert "permission_denied" in self.audit_records[0]["result_summary"]


class TestLedgerChainIntegrity:
    """Test the hash-chain integrity of the audit ledger."""

    def test_chain_integrity_after_multiple_appends(self) -> None:
        server = LedgerMCPServer()
        for i in range(10):
            server.handle_tool_call(
                "ledger_append",
                {
                    "server": "test",
                    "tool": f"tool_{i}",
                    "caller_id": "test-agent",
                    "result_summary": f"record {i}",
                },
            )
        result = server.handle_tool_call("ledger_verify", {})
        assert result["valid"] is True
        assert result["chain_length"] == 10

    def test_chain_genesis_hash(self) -> None:
        """First record should link to the genesis hash."""
        server = LedgerMCPServer()
        server.handle_tool_call(
            "ledger_append",
            {
                "server": "test",
                "tool": "first_tool",
                "caller_id": "test",
                "result_summary": "genesis test",
            },
        )
        records = server.handle_tool_call("ledger_query", {"limit": 1})
        assert records["records"][0]["previous_hash"] == "0" * 64

    def test_replay_trace_ordering(self) -> None:
        """Replay trace should maintain chronological order."""
        server = LedgerMCPServer()
        for i in range(5):
            server.handle_tool_call(
                "ledger_append",
                {
                    "server": "test",
                    "tool": f"tool_{i}",
                    "caller_id": "test",
                    "result_summary": f"event {i}",
                },
            )
        result = server.handle_tool_call("ledger_replay", {})
        trace = result["trace"]
        assert len(trace) == 5
        for i, event in enumerate(trace):
            assert event["sequence"] == i


class TestProvenanceAuditCompleteness:
    """Every provenance MCP tool call must produce an audit record."""

    def setup_method(self) -> None:
        self.audit_records: list[dict] = []
        self.server = ProvenanceMCPServer(audit_callback=self.audit_records.append)

    def test_register_source_produces_audit(self) -> None:
        self.server.handle_tool_call(
            "provenance_register_source",
            {
                "source_type": "fhir_bundle",
                "origin_server": "trialmcp-fhir",
                "description": "Test FHIR bundle",
            },
        )
        assert len(self.audit_records) == 1
        assert self.audit_records[0]["tool"] == "provenance_register_source"

    def test_record_access_produces_audit(self) -> None:
        self.server.handle_tool_call(
            "provenance_record_access",
            {
                "source_id": "test-source",
                "action": "read",
                "actor_id": "test-agent",
                "actor_role": "robot_agent",
                "tool_call": "fhir_read:patient-001",
                "input_data": "test input",
            },
        )
        assert len(self.audit_records) == 1
        assert self.audit_records[0]["tool"] == "provenance_record_access"

    def test_verify_integrity_produces_audit(self) -> None:
        self.server.handle_tool_call(
            "provenance_verify_integrity",
            {
                "data": "test data",
                "expected_hash": "invalid-hash",
            },
        )
        assert len(self.audit_records) == 1
        assert self.audit_records[0]["tool"] == "provenance_verify_integrity"
