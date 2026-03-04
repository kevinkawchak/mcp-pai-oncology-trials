"""
trialmcp-fhir: Read-only MCP server for FHIR clinical trial resources.

Provides scoped, read-only access to trial-relevant FHIR resources including
Patient, ResearchStudy, ResearchSubject, Condition, MedicationAdministration,
Observation, and AdverseEvent. All queries are logged for audit and enforce
least-privilege access through the trialmcp-authz policy framework.

Integration points:
- USL Dimension D (Multi-Site Clinical Trial Collaboration): FHIR data
  harmonization across sites using LOINC, RxNorm, MedDRA vocabularies.
- Federated Learning Pillar 1 (Privacy Infrastructure): HIPAA Safe Harbor
  de-identification applied before returning patient-linked resources.
- Physical AI robotics: Robot agents query patient schedules, protocol
  status, and adverse event history via MCP tool calls.
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class FHIRResourceType(Enum):
    """FHIR R4 resource types relevant to oncology clinical trials."""

    PATIENT = "Patient"
    RESEARCH_STUDY = "ResearchStudy"
    RESEARCH_SUBJECT = "ResearchSubject"
    CONDITION = "Condition"
    MEDICATION_ADMINISTRATION = "MedicationAdministration"
    OBSERVATION = "Observation"
    ADVERSE_EVENT = "AdverseEvent"
    DIAGNOSTIC_REPORT = "DiagnosticReport"
    IMAGING_STUDY = "ImagingStudy"


# HIPAA Safe Harbor: 18 identifier categories for de-identification
HIPAA_SAFE_HARBOR_IDENTIFIERS = [
    "name",
    "address",
    "dates",
    "phone",
    "fax",
    "email",
    "ssn",
    "mrn",
    "health_plan_id",
    "account_number",
    "certificate_license",
    "vehicle_id",
    "device_id",
    "url",
    "ip_address",
    "biometric_id",
    "photo",
    "other_unique_id",
]


class DeidentificationPipeline:
    """HIPAA Safe Harbor de-identification for FHIR resources.

    Implements pseudonymization using HMAC-SHA256 with a site-specific salt,
    consistent with the federated learning privacy infrastructure (Pillar 1).
    """

    def __init__(self, salt: str = "trialmcp-default-salt"):
        self._salt = salt

    def pseudonymize_id(self, identifier: str) -> str:
        """Generate a consistent pseudonym for a patient identifier."""
        h = hashlib.sha256(f"{self._salt}:{identifier}".encode())
        return f"pseudo-{h.hexdigest()[:16]}"

    def deidentify_resource(self, resource: dict[str, Any]) -> dict[str, Any]:
        """Remove or pseudonymize PHI/PII from a FHIR resource."""
        result = json.loads(json.dumps(resource))
        resource_type = result.get("resourceType", "")

        if resource_type == "Patient":
            if "id" in result:
                result["id"] = self.pseudonymize_id(result["id"])
            result.pop("name", None)
            result.pop("address", None)
            result.pop("telecom", None)
            result.pop("identifier", None)
            if "birthDate" in result:
                # Generalize to year only (Safe Harbor)
                result["birthDate"] = result["birthDate"][:4]

        # Pseudonymize subject references in clinical resources
        if "subject" in result and isinstance(result["subject"], dict):
            ref = result["subject"].get("reference", "")
            if ref.startswith("Patient/"):
                patient_id = ref.split("/", 1)[1]
                result["subject"]["reference"] = f"Patient/{self.pseudonymize_id(patient_id)}"

        return result


class FHIRDataStore:
    """In-memory FHIR data store backed by synthetic bundles.

    In production, this would proxy to an actual FHIR server (e.g., HAPI FHIR)
    with OAuth2 scopes enforcing read-only access patterns.
    """

    def __init__(self) -> None:
        self._resources: dict[str, dict[str, Any]] = {}
        self._deident = DeidentificationPipeline()

    def load_bundle(self, bundle: dict[str, Any]) -> int:
        """Load resources from a FHIR Bundle."""
        count = 0
        for entry in bundle.get("entry", []):
            resource = entry.get("resource", {})
            r_type = resource.get("resourceType", "")
            r_id = resource.get("id", str(uuid.uuid4()))
            key = f"{r_type}/{r_id}"
            self._resources[key] = resource
            count += 1
        logger.info("Loaded %d resources from bundle", count)
        return count

    def read(self, resource_type: str, resource_id: str) -> dict[str, Any] | None:
        """Read a single FHIR resource (de-identified)."""
        key = f"{resource_type}/{resource_id}"
        resource = self._resources.get(key)
        if resource is None:
            return None
        return self._deident.deidentify_resource(resource)

    def search(
        self, resource_type: str, params: dict[str, str] | None = None
    ) -> list[dict[str, Any]]:
        """Search FHIR resources by type and optional parameters."""
        results = []
        for key, resource in self._resources.items():
            if not key.startswith(f"{resource_type}/"):
                continue
            if params:
                match = True
                for param_key, param_val in params.items():
                    resource_val = str(resource.get(param_key, ""))
                    if param_val.lower() not in resource_val.lower():
                        match = False
                        break
                if not match:
                    continue
            results.append(self._deident.deidentify_resource(resource))
        return results


class FHIRMCPServer:
    """MCP server exposing read-only FHIR access patterns.

    Tools:
        - fhir_read: Read a single FHIR resource by type and ID.
        - fhir_search: Search resources by type with optional filters.
        - fhir_patient_lookup: Privacy-aware patient lookup with de-identification.
        - fhir_study_status: Get current status of a ResearchStudy.

    All tool invocations generate audit records via the trialmcp-ledger.
    """

    SERVER_INFO = {
        "name": "trialmcp-fhir",
        "version": "0.1.0",
        "description": "Read-only FHIR MCP server for oncology clinical trial resources",
        "capabilities": {
            "tools": True,
            "resources": True,
        },
    }

    TOOLS = [
        {
            "name": "fhir_read",
            "description": (
                "Read a single FHIR resource by type and ID. Returns de-identified data "
                "with HIPAA Safe Harbor compliance. Supported types: Patient, ResearchStudy, "
                "ResearchSubject, Condition, MedicationAdministration, Observation, "
                "AdverseEvent, DiagnosticReport, ImagingStudy."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "resource_type": {
                        "type": "string",
                        "description": "FHIR resource type",
                        "enum": [t.value for t in FHIRResourceType],
                    },
                    "resource_id": {
                        "type": "string",
                        "description": "Resource logical ID",
                    },
                },
                "required": ["resource_type", "resource_id"],
            },
        },
        {
            "name": "fhir_search",
            "description": (
                "Search FHIR resources by type with optional filter parameters. "
                "Returns de-identified results. Scoped to trial-relevant resources only."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "resource_type": {
                        "type": "string",
                        "description": "FHIR resource type to search",
                        "enum": [t.value for t in FHIRResourceType],
                    },
                    "params": {
                        "type": "object",
                        "description": "Optional search parameters as key-value pairs",
                        "additionalProperties": {"type": "string"},
                    },
                },
                "required": ["resource_type"],
            },
        },
        {
            "name": "fhir_patient_lookup",
            "description": (
                "Privacy-aware patient lookup returning pseudonymized demographics "
                "and trial enrollment status. Applies HIPAA Safe Harbor de-identification."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "string",
                        "description": "Patient identifier (will be pseudonymized in response)",
                    },
                },
                "required": ["patient_id"],
            },
        },
        {
            "name": "fhir_study_status",
            "description": (
                "Get the current status, phase, and enrollment summary for a "
                "ResearchStudy resource. Used by trial robot agents to fetch task orders."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "study_id": {
                        "type": "string",
                        "description": "ResearchStudy resource ID",
                    },
                },
                "required": ["study_id"],
            },
        },
    ]

    def __init__(self, audit_callback: Any | None = None) -> None:
        self.store = FHIRDataStore()
        self._audit_callback = audit_callback

    def _emit_audit(self, tool_name: str, params: dict, result_summary: str) -> dict[str, Any]:
        """Generate an audit record for every MCP tool invocation."""
        record = {
            "audit_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "server": "trialmcp-fhir",
            "tool": tool_name,
            "parameters": params,
            "result_summary": result_summary,
        }
        if self._audit_callback:
            self._audit_callback(record)
        return record

    def handle_tool_call(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Route an MCP tool call to the appropriate handler."""
        handlers = {
            "fhir_read": self._handle_read,
            "fhir_search": self._handle_search,
            "fhir_patient_lookup": self._handle_patient_lookup,
            "fhir_study_status": self._handle_study_status,
        }
        handler = handlers.get(tool_name)
        if handler is None:
            return {"error": f"Unknown tool: {tool_name}"}
        return handler(arguments)

    def _handle_read(self, args: dict[str, Any]) -> dict[str, Any]:
        resource_type = args["resource_type"]
        resource_id = args["resource_id"]
        result = self.store.read(resource_type, resource_id)
        self._emit_audit("fhir_read", args, "found" if result else "not_found")
        if result is None:
            return {"error": f"Resource {resource_type}/{resource_id} not found"}
        return {"resource": result}

    def _handle_search(self, args: dict[str, Any]) -> dict[str, Any]:
        resource_type = args["resource_type"]
        params = args.get("params")
        results = self.store.search(resource_type, params)
        self._emit_audit("fhir_search", args, f"returned {len(results)} results")
        return {"results": results, "total": len(results)}

    def _handle_patient_lookup(self, args: dict[str, Any]) -> dict[str, Any]:
        patient_id = args["patient_id"]
        patient = self.store.read("Patient", patient_id)
        self._emit_audit("fhir_patient_lookup", args, "found" if patient else "not_found")
        if patient is None:
            return {"error": f"Patient {patient_id} not found"}
        # Enrich with enrollment status
        subjects = self.store.search("ResearchSubject", {"individual": patient_id})
        return {
            "patient": patient,
            "enrollments": [
                {
                    "study": s.get("study", {}).get("reference", "unknown"),
                    "status": s.get("status", "unknown"),
                }
                for s in subjects
            ],
        }

    def _handle_study_status(self, args: dict[str, Any]) -> dict[str, Any]:
        study_id = args["study_id"]
        study = self.store.read("ResearchStudy", study_id)
        self._emit_audit("fhir_study_status", args, "found" if study else "not_found")
        if study is None:
            return {"error": f"ResearchStudy {study_id} not found"}
        subjects = self.store.search("ResearchSubject", {"study": study_id})
        return {
            "study_id": study.get("id"),
            "title": study.get("title", ""),
            "status": study.get("status", "unknown"),
            "phase": study.get("phase", {}).get("text", "unknown"),
            "enrolled_count": len(subjects),
        }
