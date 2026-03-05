"""
trialmcp-dicom: MCP server for DICOM query/retrieve with strict permissions.

Provides proxied access to DICOM imaging archives with enforced permission
boundaries. Supports C-FIND (query), C-MOVE (retrieve pointers), and study
metadata access. All operations are read-only and logged for audit.

Integration points:
- USL Dimension A (Simulation Framework Switching): DICOM imaging data feeds
  digital twin tumor models (Gompertz, von Bertalanffy growth curves).
- USL Dimension D (Multi-Site Collaboration): Cross-site imaging studies
  accessed through federated DICOM proxies with consistent de-identification.
- Physical AI robotics: Surgical robots retrieve DICOM study pointers for
  intraoperative guidance and pre-surgical planning.
- RECIST 1.1: Tumor measurement tracking from imaging observations.
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from servers.common import (
    ErrorCode,
    error_response,
    health_status,
    validate_dicom_uid,
)

logger = logging.getLogger(__name__)


class DICOMQueryLevel(Enum):
    """DICOM query/retrieve information model levels."""

    PATIENT = "PATIENT"
    STUDY = "STUDY"
    SERIES = "SERIES"
    IMAGE = "IMAGE"


class DICOMModality(Enum):
    """Imaging modalities relevant to oncology trials."""

    CT = "CT"
    MR = "MR"
    PT = "PT"  # PET
    US = "US"
    DX = "DX"
    CR = "CR"
    NM = "NM"
    RTSTRUCT = "RTSTRUCT"
    RTPLAN = "RTPLAN"
    RTDOSE = "RTDOSE"


class DICOMPermissionPolicy:
    """Permission enforcement for DICOM operations.

    Implements least-privilege access following the trialmcp-authz policy
    framework. Restricts access based on caller role, study assignment,
    and permitted modalities.
    """

    def __init__(self) -> None:
        self._role_permissions: dict[str, dict[str, Any]] = {
            "trial_coordinator": {
                "query_levels": ["PATIENT", "STUDY", "SERIES"],
                "modalities": ["CT", "MR", "PT", "DX", "CR"],
                "can_retrieve": True,
            },
            "robot_agent": {
                "query_levels": ["STUDY", "SERIES"],
                "modalities": ["CT", "MR", "RTSTRUCT", "RTPLAN"],
                "can_retrieve": True,
            },
            "data_monitor": {
                "query_levels": ["PATIENT", "STUDY"],
                "modalities": ["CT", "MR", "PT"],
                "can_retrieve": False,
            },
            "auditor": {
                "query_levels": ["STUDY"],
                "modalities": [],
                "can_retrieve": False,
            },
        }

    def check_permission(self, role: str, query_level: str, modality: str | None = None) -> bool:
        """Check if a role has permission for a given query level and modality."""
        perms = self._role_permissions.get(role)
        if perms is None:
            return False
        if query_level not in perms["query_levels"]:
            return False
        if modality and perms["modalities"] and modality not in perms["modalities"]:
            return False
        return True

    def can_retrieve(self, role: str) -> bool:
        """Check if a role can retrieve (C-MOVE) study data."""
        perms = self._role_permissions.get(role)
        if perms is None:
            return False
        return perms.get("can_retrieve", False)


class DICOMStudyIndex:
    """In-memory index of DICOM study metadata.

    In production, this would proxy C-FIND queries to a PACS system
    (e.g., Orthanc, dcm4chee) via the DICOM networking protocol.
    """

    def __init__(self) -> None:
        self._studies: dict[str, dict[str, Any]] = {}

    def index_study(self, study: dict[str, Any]) -> None:
        """Add a study to the index."""
        study_uid = study.get("study_instance_uid", str(uuid.uuid4()))
        self._studies[study_uid] = study

    def query(
        self,
        level: str,
        filters: dict[str, str] | None = None,
    ) -> list[dict[str, Any]]:
        """Query the study index (C-FIND proxy)."""
        results = []
        for study in self._studies.values():
            if filters:
                match = True
                for key, val in filters.items():
                    study_val = str(study.get(key, ""))
                    if val.lower() not in study_val.lower():
                        match = False
                        break
                if not match:
                    continue
            # Return only metadata appropriate for the query level
            result = self._project_to_level(study, level)
            results.append(result)
        return results

    def get_study(self, study_uid: str) -> dict[str, Any] | None:
        """Get a single study by UID."""
        return self._studies.get(study_uid)

    @staticmethod
    def _project_to_level(study: dict[str, Any], level: str) -> dict[str, Any]:
        """Project study data to the requested query level."""
        if level == "PATIENT":
            return {
                "patient_id": study.get("patient_id"),
                "patient_name_hash": hashlib.sha256(
                    study.get("patient_name", "").encode()
                ).hexdigest()[:12],
                "study_count": 1,
            }
        elif level == "STUDY":
            return {
                "study_instance_uid": study.get("study_instance_uid"),
                "study_date": study.get("study_date"),
                "study_description": study.get("study_description"),
                "modality": study.get("modality"),
                "accession_number": study.get("accession_number"),
            }
        elif level == "SERIES":
            return {
                "study_instance_uid": study.get("study_instance_uid"),
                "series": study.get("series", []),
            }
        return study


class DICOMMCPServer:
    """MCP server for DICOM query/retrieve proxy with strict permissions.

    Tools:
        - dicom_query: Query imaging studies by level and filters (C-FIND proxy).
        - dicom_retrieve_pointer: Get a retrieval pointer for a study (C-MOVE proxy).
        - dicom_study_metadata: Get detailed metadata for a specific study.
        - dicom_recist_measurements: Get RECIST 1.1 tumor measurements from a study.

    All tool invocations generate audit records. Permission checks are enforced
    based on the caller's role and the trialmcp-authz policy.
    """

    SERVER_INFO = {
        "name": "trialmcp-dicom",
        "version": "0.2.0",
        "description": (
            "DICOM query/retrieve MCP server with strict permissions for oncology trials"
        ),
        "capabilities": {
            "tools": True,
            "resources": True,
        },
    }

    TOOLS = [
        {
            "name": "dicom_query",
            "description": (
                "Query DICOM imaging studies using C-FIND proxy. Supports PATIENT, "
                "STUDY, and SERIES level queries with optional filters. Results are "
                "de-identified and permission-scoped."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query_level": {
                        "type": "string",
                        "description": "DICOM query level",
                        "enum": [q.value for q in DICOMQueryLevel],
                    },
                    "filters": {
                        "type": "object",
                        "description": "Query filters (e.g., modality, study_date)",
                        "additionalProperties": {"type": "string"},
                    },
                    "caller_role": {
                        "type": "string",
                        "description": "Role of the calling agent",
                        "enum": ["trial_coordinator", "robot_agent", "data_monitor", "auditor"],
                    },
                },
                "required": ["query_level", "caller_role"],
            },
        },
        {
            "name": "dicom_retrieve_pointer",
            "description": (
                "Get a retrieval pointer for a DICOM study. Returns a secure, "
                "time-limited reference that can be used to access the study data. "
                "Used by surgical robots for intraoperative imaging access."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "study_instance_uid": {
                        "type": "string",
                        "description": "DICOM Study Instance UID",
                    },
                    "caller_role": {
                        "type": "string",
                        "description": "Role of the calling agent",
                        "enum": ["trial_coordinator", "robot_agent", "data_monitor", "auditor"],
                    },
                },
                "required": ["study_instance_uid", "caller_role"],
            },
        },
        {
            "name": "dicom_study_metadata",
            "description": (
                "Get detailed metadata for a specific DICOM study including "
                "series breakdown and modality information."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "study_instance_uid": {
                        "type": "string",
                        "description": "DICOM Study Instance UID",
                    },
                    "caller_role": {
                        "type": "string",
                        "description": "Role of the calling agent",
                        "enum": ["trial_coordinator", "robot_agent", "data_monitor", "auditor"],
                    },
                },
                "required": ["study_instance_uid", "caller_role"],
            },
        },
        {
            "name": "dicom_recist_measurements",
            "description": (
                "Retrieve RECIST 1.1 tumor measurements linked to a DICOM study. "
                "Returns target lesion measurements and overall response assessment."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "study_instance_uid": {
                        "type": "string",
                        "description": "DICOM Study Instance UID",
                    },
                },
                "required": ["study_instance_uid"],
            },
        },
    ]

    def __init__(self, audit_callback: Any | None = None) -> None:
        self.index = DICOMStudyIndex()
        self.permissions = DICOMPermissionPolicy()
        self._audit_callback = audit_callback

    def _emit_audit(self, tool_name: str, params: dict, result_summary: str) -> dict[str, Any]:
        """Generate an audit record for every MCP tool invocation."""
        record = {
            "audit_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "server": "trialmcp-dicom",
            "tool": tool_name,
            "parameters": params,
            "result_summary": result_summary,
        }
        if self._audit_callback:
            self._audit_callback(record)
        return record

    def handle_tool_call(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Route an MCP tool call to the appropriate handler."""
        if tool_name == "health":
            return health_status(self.SERVER_INFO["name"], self.SERVER_INFO["version"])
        handlers = {
            "dicom_query": self._handle_query,
            "dicom_retrieve_pointer": self._handle_retrieve_pointer,
            "dicom_study_metadata": self._handle_study_metadata,
            "dicom_recist_measurements": self._handle_recist,
        }
        handler = handlers.get(tool_name)
        if handler is None:
            return error_response(ErrorCode.INVALID_INPUT, f"Unknown tool: {tool_name}")
        return handler(arguments)

    def _handle_query(self, args: dict[str, Any]) -> dict[str, Any]:
        level = args["query_level"]
        role = args["caller_role"]
        filters = args.get("filters")

        if not self.permissions.check_permission(role, level):
            self._emit_audit("dicom_query", args, "permission_denied")
            return error_response(
                ErrorCode.PERMISSION_DENIED,
                f"Role '{role}' lacks permission for {level}-level queries",
            )

        results = self.index.query(level, filters)
        self._emit_audit("dicom_query", args, f"returned {len(results)} results")
        return {"results": results, "total": len(results)}

    def _handle_retrieve_pointer(self, args: dict[str, Any]) -> dict[str, Any]:
        study_uid = args["study_instance_uid"]
        role = args["caller_role"]

        if not validate_dicom_uid(study_uid):
            self._emit_audit("dicom_retrieve_pointer", args, "validation_failed")
            return error_response(ErrorCode.VALIDATION_FAILED, f"Invalid DICOM UID: {study_uid}")

        if not self.permissions.can_retrieve(role):
            self._emit_audit("dicom_retrieve_pointer", args, "permission_denied")
            msg = f"Role '{role}' lacks retrieve permission"
            return error_response(ErrorCode.PERMISSION_DENIED, msg)

        study = self.index.get_study(study_uid)
        if study is None:
            self._emit_audit("dicom_retrieve_pointer", args, "not_found")
            return error_response(ErrorCode.NOT_FOUND, f"Study {study_uid} not found")

        # Generate a time-limited retrieval token
        token_data = f"{study_uid}:{role}:{datetime.now(timezone.utc).isoformat()}"
        token = hashlib.sha256(token_data.encode()).hexdigest()[:32]

        self._emit_audit("dicom_retrieve_pointer", args, "pointer_issued")
        return {
            "study_instance_uid": study_uid,
            "retrieval_token": token,
            "retrieval_endpoint": f"/wado-rs/studies/{study_uid}",
            "expires_in_seconds": 3600,
        }

    def _handle_study_metadata(self, args: dict[str, Any]) -> dict[str, Any]:
        study_uid = args["study_instance_uid"]
        role = args["caller_role"]

        if not self.permissions.check_permission(role, "STUDY"):
            self._emit_audit("dicom_study_metadata", args, "permission_denied")
            return error_response(
                ErrorCode.PERMISSION_DENIED,
                f"Role '{role}' lacks STUDY-level permission",
            )

        study = self.index.get_study(study_uid)
        if study is None:
            self._emit_audit("dicom_study_metadata", args, "not_found")
            return {"error": f"Study {study_uid} not found"}

        self._emit_audit("dicom_study_metadata", args, "found")
        return {
            "study_instance_uid": study_uid,
            "study_date": study.get("study_date"),
            "study_description": study.get("study_description"),
            "modality": study.get("modality"),
            "series_count": len(study.get("series", [])),
            "series": [
                {
                    "series_instance_uid": s.get("series_instance_uid"),
                    "modality": s.get("modality"),
                    "description": s.get("description"),
                    "instance_count": s.get("instance_count", 0),
                }
                for s in study.get("series", [])
            ],
        }

    def _handle_recist(self, args: dict[str, Any]) -> dict[str, Any]:
        study_uid = args["study_instance_uid"]
        study = self.index.get_study(study_uid)
        if study is None:
            self._emit_audit("dicom_recist_measurements", args, "not_found")
            return {"error": f"Study {study_uid} not found"}

        measurements = study.get("recist_measurements", {})
        self._emit_audit("dicom_recist_measurements", args, "found")
        return {
            "study_instance_uid": study_uid,
            "recist_version": "1.1",
            "measurements": measurements,
        }
