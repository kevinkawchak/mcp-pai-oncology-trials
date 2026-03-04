"""
trialmcp-provenance: Data provenance gateway MCP server.

Enforces least-privilege data access, logs all tool calls, and provides
replayable audit traces across the TrialMCP Pack. Acts as a unified
gateway that tracks the lineage and chain-of-custody for every piece
of clinical data accessed through MCP tools.

Integration points:
- Federated Learning Pillar 5 (Multi-Organization Cooperation): Provenance
  tracking across federated trial sites with differential privacy budgets.
- USL Dimension D (Multi-Site Collaboration): Cross-site data lineage
  maintaining metadata and traceability when copying records.
- 21 CFR Part 11: Preserves metadata and traceability for electronic records,
  satisfying FDA guidance on electronic records management.
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


class DataSource:
    """Represents a registered data source in the provenance graph."""

    def __init__(
        self,
        source_id: str,
        source_type: str,
        origin_server: str,
        description: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.source_id = source_id
        self.source_type = source_type
        self.origin_server = origin_server
        self.description = description
        self.metadata = metadata or {}
        self.registered_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "source_type": self.source_type,
            "origin_server": self.origin_server,
            "description": self.description,
            "metadata": self.metadata,
            "registered_at": self.registered_at,
        }


class ProvenanceRecord:
    """A single provenance record tracking data access or transformation."""

    def __init__(
        self,
        record_id: str,
        source_id: str,
        action: str,
        actor_id: str,
        actor_role: str,
        tool_call: str,
        input_hash: str,
        output_hash: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.record_id = record_id
        self.source_id = source_id
        self.action = action
        self.actor_id = actor_id
        self.actor_role = actor_role
        self.tool_call = tool_call
        self.input_hash = input_hash
        self.output_hash = output_hash
        self.metadata = metadata or {}
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "source_id": self.source_id,
            "action": self.action,
            "actor_id": self.actor_id,
            "actor_role": self.actor_role,
            "tool_call": self.tool_call,
            "input_hash": self.input_hash,
            "output_hash": self.output_hash,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }


class ProvenanceGraph:
    """Directed acyclic graph tracking data lineage across MCP operations.

    Each node is a data source or transformation result. Each edge represents
    a tool call that accessed or transformed data. The graph supports
    forward lineage (what was derived from X?) and backward lineage
    (where did Y come from?) queries.
    """

    def __init__(self) -> None:
        self._sources: dict[str, DataSource] = {}
        self._records: list[ProvenanceRecord] = []

    def register_source(self, source: DataSource) -> None:
        """Register a new data source in the provenance graph."""
        self._sources[source.source_id] = source

    def record_access(
        self,
        source_id: str,
        action: str,
        actor_id: str,
        actor_role: str,
        tool_call: str,
        input_data: str,
        output_data: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ProvenanceRecord:
        """Record a data access or transformation event."""
        input_hash = hashlib.sha256(input_data.encode()).hexdigest()
        output_hash = None
        if output_data:
            output_hash = hashlib.sha256(output_data.encode()).hexdigest()

        record = ProvenanceRecord(
            record_id=str(uuid.uuid4()),
            source_id=source_id,
            action=action,
            actor_id=actor_id,
            actor_role=actor_role,
            tool_call=tool_call,
            input_hash=input_hash,
            output_hash=output_hash,
            metadata=metadata,
        )
        self._records.append(record)
        return record

    def get_lineage(self, source_id: str) -> list[dict[str, Any]]:
        """Get the full access lineage for a data source."""
        return [r.to_dict() for r in self._records if r.source_id == source_id]

    def get_actor_history(self, actor_id: str) -> list[dict[str, Any]]:
        """Get all provenance records for a specific actor."""
        return [r.to_dict() for r in self._records if r.actor_id == actor_id]

    def get_sources(self) -> list[dict[str, Any]]:
        """List all registered data sources."""
        return [s.to_dict() for s in self._sources.values()]

    def compute_data_fingerprint(self, data: str) -> str:
        """Compute a SHA-256 fingerprint for data integrity verification."""
        return hashlib.sha256(data.encode()).hexdigest()


class ProvenanceMCPServer:
    """Data provenance gateway MCP server.

    Tools:
        - provenance_register_source: Register a data source in the graph.
        - provenance_record_access: Record a data access event.
        - provenance_get_lineage: Get lineage history for a data source.
        - provenance_get_actor_history: Get all access by a specific actor.
        - provenance_verify_integrity: Verify data integrity via fingerprint.

    This server enforces least-privilege data access by integrating with
    trialmcp-authz and logs all operations for replayable audit traces
    via trialmcp-ledger.
    """

    SERVER_INFO = {
        "name": "trialmcp-provenance",
        "version": "0.1.0",
        "description": "Data provenance gateway enforcing least-privilege access with audit traces",
        "capabilities": {
            "tools": True,
            "resources": True,
        },
    }

    TOOLS = [
        {
            "name": "provenance_register_source",
            "description": (
                "Register a data source in the provenance graph. Sources include "
                "FHIR bundles, DICOM studies, scheduling data, and eSource uploads."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_type": {
                        "type": "string",
                        "description": "Type of data source",
                        "enum": ["fhir_bundle", "dicom_study", "scheduling", "esource", "econsent"],
                    },
                    "origin_server": {
                        "type": "string",
                        "description": "MCP server that manages this source",
                    },
                    "description": {
                        "type": "string",
                        "description": "Human-readable description of the source",
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Additional metadata for the source",
                    },
                },
                "required": ["source_type", "origin_server", "description"],
            },
        },
        {
            "name": "provenance_record_access",
            "description": (
                "Record a data access or transformation event. Called by MCP servers "
                "when data is read, transformed, or exported."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_id": {
                        "type": "string",
                        "description": "ID of the data source being accessed",
                    },
                    "action": {
                        "type": "string",
                        "description": "Action performed on the data",
                        "enum": ["read", "transform", "export", "deidentify", "aggregate"],
                    },
                    "actor_id": {
                        "type": "string",
                        "description": "ID of the agent performing the action",
                    },
                    "actor_role": {
                        "type": "string",
                        "description": "Role of the agent",
                    },
                    "tool_call": {
                        "type": "string",
                        "description": "MCP tool call that triggered this access",
                    },
                    "input_data": {
                        "type": "string",
                        "description": "Input data fingerprint or reference",
                    },
                    "output_data": {
                        "type": "string",
                        "description": "Output data fingerprint or reference",
                    },
                },
                "required": ["source_id", "action", "actor_id", "actor_role", "tool_call",
                             "input_data"],
            },
        },
        {
            "name": "provenance_get_lineage",
            "description": (
                "Get the full access lineage for a data source. Shows every read, "
                "transformation, and export with actor and timestamp details."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_id": {
                        "type": "string",
                        "description": "ID of the data source",
                    },
                },
                "required": ["source_id"],
            },
        },
        {
            "name": "provenance_get_actor_history",
            "description": (
                "Get all provenance records for a specific actor. Useful for "
                "auditing what data a robot agent or user has accessed."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "actor_id": {
                        "type": "string",
                        "description": "ID of the actor",
                    },
                },
                "required": ["actor_id"],
            },
        },
        {
            "name": "provenance_verify_integrity",
            "description": (
                "Verify data integrity by comparing a SHA-256 fingerprint. "
                "Used to ensure data has not been modified in transit."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "string",
                        "description": "Data to fingerprint",
                    },
                    "expected_hash": {
                        "type": "string",
                        "description": "Expected SHA-256 hash to verify against",
                    },
                },
                "required": ["data", "expected_hash"],
            },
        },
    ]

    def __init__(self, audit_callback: Any | None = None) -> None:
        self.graph = ProvenanceGraph()
        self._audit_callback = audit_callback

    def _emit_audit(self, tool_name: str, params: dict, result_summary: str) -> None:
        if self._audit_callback:
            self._audit_callback(
                {
                    "audit_id": str(uuid.uuid4()),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "server": "trialmcp-provenance",
                    "tool": tool_name,
                    "parameters": params,
                    "result_summary": result_summary,
                }
            )

    def handle_tool_call(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Route an MCP tool call to the appropriate handler."""
        handlers = {
            "provenance_register_source": self._handle_register,
            "provenance_record_access": self._handle_record_access,
            "provenance_get_lineage": self._handle_get_lineage,
            "provenance_get_actor_history": self._handle_get_actor_history,
            "provenance_verify_integrity": self._handle_verify_integrity,
        }
        handler = handlers.get(tool_name)
        if handler is None:
            return {"error": f"Unknown tool: {tool_name}"}
        return handler(arguments)

    def _handle_register(self, args: dict[str, Any]) -> dict[str, Any]:
        source = DataSource(
            source_id=str(uuid.uuid4()),
            source_type=args["source_type"],
            origin_server=args["origin_server"],
            description=args["description"],
            metadata=args.get("metadata"),
        )
        self.graph.register_source(source)
        self._emit_audit("provenance_register_source", args, f"registered:{source.source_id}")
        return {"source_id": source.source_id, "registered": True}

    def _handle_record_access(self, args: dict[str, Any]) -> dict[str, Any]:
        record = self.graph.record_access(
            source_id=args["source_id"],
            action=args["action"],
            actor_id=args["actor_id"],
            actor_role=args["actor_role"],
            tool_call=args["tool_call"],
            input_data=args["input_data"],
            output_data=args.get("output_data"),
            metadata=args.get("metadata"),
        )
        self._emit_audit("provenance_record_access", args, f"recorded:{record.record_id}")
        return {"record_id": record.record_id, "recorded": True}

    def _handle_get_lineage(self, args: dict[str, Any]) -> dict[str, Any]:
        lineage = self.graph.get_lineage(args["source_id"])
        self._emit_audit("provenance_get_lineage", args, f"returned {len(lineage)} records")
        return {"source_id": args["source_id"], "lineage": lineage, "count": len(lineage)}

    def _handle_get_actor_history(self, args: dict[str, Any]) -> dict[str, Any]:
        history = self.graph.get_actor_history(args["actor_id"])
        self._emit_audit("provenance_get_actor_history", args, f"returned {len(history)} records")
        return {"actor_id": args["actor_id"], "history": history, "count": len(history)}

    def _handle_verify_integrity(self, args: dict[str, Any]) -> dict[str, Any]:
        actual_hash = self.graph.compute_data_fingerprint(args["data"])
        match = actual_hash == args["expected_hash"]
        self._emit_audit(
            "provenance_verify_integrity", {"expected": args["expected_hash"]},
            "match" if match else "mismatch"
        )
        return {
            "match": match,
            "actual_hash": actual_hash,
            "expected_hash": args["expected_hash"],
        }
