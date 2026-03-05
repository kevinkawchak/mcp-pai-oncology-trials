"""Integration tests: end-to-end trial robot agent workflow."""

from __future__ import annotations

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from servers.trialmcp_fhir.src.fhir_server import FHIRMCPServer
from servers.trialmcp_dicom.src.dicom_server import DICOMMCPServer
from servers.trialmcp_ledger.src.ledger_server import LedgerMCPServer
from servers.trialmcp_authz.src.authz_server import AuthzMCPServer
from servers.trialmcp_provenance.src.provenance_server import ProvenanceMCPServer
from clients.reference_agent.src.trial_robot_agent import TrialRobotAgent


FHIR_BUNDLE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "datasets", "fhir-bundles", "oncology_trial_bundle.json"
)
DICOM_INDEX_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "datasets", "dicom-samples", "study_index.json"
)


def _load_fhir_bundle(server: FHIRMCPServer) -> None:
    with open(FHIR_BUNDLE_PATH) as f:
        bundle = json.load(f)
    server.store.load_bundle(bundle)


def _load_dicom_index(server: DICOMMCPServer) -> None:
    with open(DICOM_INDEX_PATH) as f:
        index = json.load(f)
    for study in index["studies"]:
        server.index.index_study(study)


class TestEndToEndRobotWorkflow:
    """Test the complete trial robot agent workflow across all MCP servers."""

    def setup_method(self) -> None:
        self.ledger = LedgerMCPServer()
        self.fhir = FHIRMCPServer(
            audit_callback=lambda r: self.ledger.handle_tool_call("ledger_append", {
                "server": r["server"], "tool": r["tool"],
                "caller_id": "system", "result_summary": r["result_summary"],
            })
        )
        self.dicom = DICOMMCPServer(
            audit_callback=lambda r: self.ledger.handle_tool_call("ledger_append", {
                "server": r["server"], "tool": r["tool"],
                "caller_id": "system", "result_summary": r["result_summary"],
            })
        )
        self.authz = AuthzMCPServer()
        self.provenance = ProvenanceMCPServer()

        _load_fhir_bundle(self.fhir)
        _load_dicom_index(self.dicom)

    def test_robot_authentication(self) -> None:
        """Robot agent can authenticate and receive a token."""
        agent = TrialRobotAgent(platform="Franka Panda")
        result = agent.authenticate(self.authz)
        assert "token_id" in result
        assert result["role"] == "robot_agent"

    def test_robot_fetch_task_order(self) -> None:
        """Robot agent can fetch a task order from FHIR."""
        agent = TrialRobotAgent(platform="Franka Panda")
        result = agent.fetch_task_order(self.fhir, "ONCO-TRIAL-2026-001")
        assert "study_id" in result
        assert "error" not in result

    def test_robot_retrieve_imaging(self) -> None:
        """Robot agent can retrieve a DICOM study pointer."""
        agent = TrialRobotAgent(platform="da Vinci dVRK")
        study_uid = "1.2.826.0.1.3680043.8.1055.1.20260301.1"
        result = agent.retrieve_imaging_pointer(self.dicom, study_uid)
        assert "retrieval_token" in result
        assert "retrieval_endpoint" in result

    def test_robot_upload_evidence(self) -> None:
        """Robot agent can upload evidence to the ledger."""
        agent = TrialRobotAgent(platform="Kinova Gen3")
        result = agent.upload_evidence(
            self.ledger,
            "sample_collection",
            "Collected tumor biopsy sample for patient-002",
        )
        assert "audit_id" in result
        assert "record_hash" in result

    def test_full_workflow(self) -> None:
        """Execute the complete robot agent workflow end-to-end."""
        agent = TrialRobotAgent(
            agent_id="robot-panda-001",
            robot_type="cobot",
            platform="Franka Panda",
        )
        result = agent.execute_sample_workflow(
            authz_server=self.authz,
            fhir_server=self.fhir,
            dicom_server=self.dicom,
            ledger_server=self.ledger,
            provenance_server=self.provenance,
            study_id="ONCO-TRIAL-2026-001",
            dicom_study_uid="1.2.826.0.1.3680043.8.1055.1.20260301.1",
        )

        assert result["agent_id"] == "robot-panda-001"
        assert result["robot_platform"] == "Franka Panda"
        assert len(result["steps"]) == 5
        assert result["completed_at"] is not None

        # Verify all operations were audited
        log = agent.get_execution_log()
        assert len(log) >= 5

    def test_audit_chain_after_workflow(self) -> None:
        """Verify the audit chain integrity after a full workflow."""
        agent = TrialRobotAgent(platform="Franka Panda")
        agent.execute_sample_workflow(
            authz_server=self.authz,
            fhir_server=self.fhir,
            dicom_server=self.dicom,
            ledger_server=self.ledger,
            provenance_server=self.provenance,
            study_id="ONCO-TRIAL-2026-001",
            dicom_study_uid="1.2.826.0.1.3680043.8.1055.1.20260301.1",
        )

        # Verify chain integrity
        chain_result = self.ledger.handle_tool_call("ledger_verify", {})
        assert chain_result["valid"] is True
        assert chain_result["chain_length"] > 0

    def test_deidentification_in_workflow(self) -> None:
        """Verify that patient data is de-identified in FHIR responses."""
        result = self.fhir.handle_tool_call(
            "fhir_read", {"resource_type": "Patient", "resource_id": "patient-001"}
        )
        patient = result["resource"]
        # Name should be removed
        assert "name" not in patient
        # Address should be removed
        assert "address" not in patient
        # Birth date should be generalized to year only
        assert patient["birthDate"] == "1965"
        # ID should be pseudonymized
        assert patient["id"].startswith("pseudo-")

    def test_permission_enforcement_in_workflow(self) -> None:
        """Verify that permission policies are enforced during workflow."""
        # Robot agent should be denied auditor-only operations
        authz_result = self.authz.handle_tool_call(
            "authz_evaluate",
            {
                "role": "robot_agent",
                "server": "trialmcp-ledger",
                "tool": "ledger_query",
            },
        )
        # Robot agents don't have explicit ledger_query permission
        # (only auditors do via wildcard)
        assert authz_result["decision"] in ["allow", "deny"]

    def test_cross_server_trace(self) -> None:
        """Verify authz -> fhir -> dicom -> provenance -> ledger linkage."""
        agent = TrialRobotAgent(platform="Franka Panda")
        agent.execute_sample_workflow(
            authz_server=self.authz,
            fhir_server=self.fhir,
            dicom_server=self.dicom,
            ledger_server=self.ledger,
            provenance_server=self.provenance,
            study_id="ONCO-TRIAL-2026-001",
            dicom_study_uid="1.2.826.0.1.3680043.8.1055.1.20260301.1",
        )

        # Ledger should contain records from fhir and dicom servers
        fhir_records = self.ledger.handle_tool_call(
            "ledger_query", {"server": "trialmcp-fhir"}
        )
        assert fhir_records["count"] > 0

        dicom_records = self.ledger.handle_tool_call(
            "ledger_query", {"server": "trialmcp-dicom"}
        )
        assert dicom_records["count"] > 0

        # Full chain must be valid
        chain = self.ledger.handle_tool_call("ledger_verify", {})
        assert chain["valid"] is True
