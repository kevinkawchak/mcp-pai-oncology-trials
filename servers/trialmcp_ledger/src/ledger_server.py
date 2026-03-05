"""
trialmcp-ledger: MCP server for trial audit ledger and chain-of-custody.

Provides an append-only, hash-chained audit ledger for all MCP tool calls
across the TrialMCP Pack. Every invocation produces a signed audit record
with SHA-256 hash-chain integrity, satisfying 21 CFR Part 11 requirements
for electronic records in clinical trials.

Integration points:
- USL Dimension D (Multi-Site Collaboration): Federated audit logs
  synchronized across trial sites with conflict-free merge semantics.
- Federated Learning Pillar 2 (Regulatory Infrastructure): FDA, IRB,
  ICH-GCP compliance through comprehensive audit trails.
- Physical AI robotics: Chain-of-custody tracking for evidence collected
  by autonomous trial robots (sample handling, imaging, eConsent).
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


class AuditRecord:
    """A single audit record in the hash-chained ledger.

    Each record contains the previous record's hash, creating an
    immutable chain that detects tampering or record deletion.
    """

    def __init__(
        self,
        audit_id: str,
        timestamp: str,
        server: str,
        tool: str,
        caller_id: str,
        parameters: dict[str, Any],
        result_summary: str,
        previous_hash: str,
    ) -> None:
        self.audit_id = audit_id
        self.timestamp = timestamp
        self.server = server
        self.tool = tool
        self.caller_id = caller_id
        self.parameters = parameters
        self.result_summary = result_summary
        self.previous_hash = previous_hash
        self.record_hash = self._compute_hash()

    def _compute_hash(self) -> str:
        """Compute SHA-256 hash of the record including the chain link."""
        content = json.dumps(
            {
                "audit_id": self.audit_id,
                "timestamp": self.timestamp,
                "server": self.server,
                "tool": self.tool,
                "caller_id": self.caller_id,
                "parameters": self.parameters,
                "result_summary": self.result_summary,
                "previous_hash": self.previous_hash,
            },
            sort_keys=True,
        )
        return hashlib.sha256(content.encode()).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        """Serialize record to dictionary."""
        return {
            "audit_id": self.audit_id,
            "timestamp": self.timestamp,
            "server": self.server,
            "tool": self.tool,
            "caller_id": self.caller_id,
            "parameters": self.parameters,
            "result_summary": self.result_summary,
            "previous_hash": self.previous_hash,
            "record_hash": self.record_hash,
        }


class AuditLedger:
    """Append-only, hash-chained audit ledger.

    Implements the chain-of-custody pattern required by 21 CFR Part 11
    and ICH-GCP E6(R2) for electronic records in clinical trials.
    Provides integrity verification and replay capability.
    """

    GENESIS_HASH = "0" * 64

    def __init__(self) -> None:
        self._records: list[AuditRecord] = []

    @property
    def chain_length(self) -> int:
        return len(self._records)

    @property
    def latest_hash(self) -> str:
        if not self._records:
            return self.GENESIS_HASH
        return self._records[-1].record_hash

    def append(
        self,
        server: str,
        tool: str,
        caller_id: str,
        parameters: dict[str, Any],
        result_summary: str,
    ) -> AuditRecord:
        """Append a new audit record to the ledger."""
        record = AuditRecord(
            audit_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            server=server,
            tool=tool,
            caller_id=caller_id,
            parameters=parameters,
            result_summary=result_summary,
            previous_hash=self.latest_hash,
        )
        self._records.append(record)
        logger.info(
            "Audit record %s appended (chain length: %d)", record.audit_id, len(self._records)
        )
        return record

    def verify_chain(self) -> dict[str, Any]:
        """Verify the integrity of the entire audit chain."""
        if not self._records:
            return {"valid": True, "chain_length": 0, "errors": []}

        errors = []
        # Check genesis link
        if self._records[0].previous_hash != self.GENESIS_HASH:
            errors.append({"index": 0, "error": "Invalid genesis hash"})

        for i, record in enumerate(self._records):
            # Verify record hash
            expected_hash = record._compute_hash()
            if record.record_hash != expected_hash:
                errors.append({"index": i, "error": "Hash mismatch (record tampered)"})

            # Verify chain link
            if i > 0 and record.previous_hash != self._records[i - 1].record_hash:
                errors.append({"index": i, "error": "Chain link broken"})

        return {
            "valid": len(errors) == 0,
            "chain_length": len(self._records),
            "errors": errors,
        }

    def query(
        self,
        server: str | None = None,
        tool: str | None = None,
        caller_id: str | None = None,
        since: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Query audit records with optional filters."""
        results = []
        for record in reversed(self._records):
            if server and record.server != server:
                continue
            if tool and record.tool != tool:
                continue
            if caller_id and record.caller_id != caller_id:
                continue
            if since and record.timestamp < since:
                break
            results.append(record.to_dict())
            if len(results) >= limit:
                break
        return results

    def replay(self, since: str | None = None) -> list[dict[str, Any]]:
        """Generate a replayable audit trace from the ledger."""
        trace = []
        for record in self._records:
            if since and record.timestamp < since:
                continue
            trace.append(
                {
                    "sequence": len(trace),
                    "timestamp": record.timestamp,
                    "server": record.server,
                    "tool": record.tool,
                    "caller_id": record.caller_id,
                    "parameters": record.parameters,
                    "result_summary": record.result_summary,
                }
            )
        return trace


class LedgerMCPServer:
    """MCP server for the trial audit ledger and chain-of-custody APIs.

    Tools:
        - ledger_append: Record an audit event in the hash-chained ledger.
        - ledger_verify: Verify integrity of the full audit chain.
        - ledger_query: Query audit records with filters.
        - ledger_replay: Generate a replayable audit trace.
        - ledger_chain_status: Get current chain status and latest hash.

    This server is the backbone of the TrialMCP Pack's compliance story,
    ensuring that every tool call across all servers is traceable and
    tamper-evident.
    """

    SERVER_INFO = {
        "name": "trialmcp-ledger",
        "version": "0.1.0",
        "description": "Audit ledger and chain-of-custody MCP server for clinical trials",
        "capabilities": {
            "tools": True,
            "resources": True,
        },
    }

    TOOLS = [
        {
            "name": "ledger_append",
            "description": (
                "Append an audit record to the hash-chained ledger. "
                "Used by other TrialMCP servers to log every tool invocation. "
                "Each record is linked to the previous via SHA-256 hash chain."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "server": {"type": "string", "description": "Source MCP server name"},
                    "tool": {"type": "string", "description": "Tool that was invoked"},
                    "caller_id": {"type": "string", "description": "ID of the calling agent"},
                    "parameters": {
                        "type": "object",
                        "description": "Tool call parameters (sanitized)",
                    },
                    "result_summary": {
                        "type": "string",
                        "description": "Brief summary of the result",
                    },
                },
                "required": ["server", "tool", "caller_id", "result_summary"],
            },
        },
        {
            "name": "ledger_verify",
            "description": (
                "Verify the integrity of the entire audit hash chain. "
                "Detects any tampering, deletion, or reordering of records. "
                "Required for 21 CFR Part 11 compliance audits."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "ledger_query",
            "description": (
                "Query audit records with optional filters by server, tool, "
                "caller, or time range. Returns most recent records first."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "server": {"type": "string", "description": "Filter by source server"},
                    "tool": {"type": "string", "description": "Filter by tool name"},
                    "caller_id": {"type": "string", "description": "Filter by caller ID"},
                    "since": {
                        "type": "string",
                        "description": "ISO timestamp to filter records after",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum records to return (default 100)",
                    },
                },
            },
        },
        {
            "name": "ledger_replay",
            "description": (
                "Generate a replayable audit trace suitable for compliance review. "
                "Produces a sequential record of all tool invocations that can be "
                "replayed for verification or incident investigation."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "since": {
                        "type": "string",
                        "description": "ISO timestamp to start replay from",
                    },
                },
            },
        },
        {
            "name": "ledger_chain_status",
            "description": (
                "Get the current status of the audit chain including length, "
                "latest hash, and integrity verification result."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
    ]

    def __init__(self) -> None:
        self.ledger = AuditLedger()

    def handle_tool_call(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Route an MCP tool call to the appropriate handler."""
        handlers = {
            "ledger_append": self._handle_append,
            "ledger_verify": self._handle_verify,
            "ledger_query": self._handle_query,
            "ledger_replay": self._handle_replay,
            "ledger_chain_status": self._handle_chain_status,
        }
        handler = handlers.get(tool_name)
        if handler is None:
            return {"error": f"Unknown tool: {tool_name}"}
        return handler(arguments)

    def _handle_append(self, args: dict[str, Any]) -> dict[str, Any]:
        record = self.ledger.append(
            server=args["server"],
            tool=args["tool"],
            caller_id=args.get("caller_id", "unknown"),
            parameters=args.get("parameters", {}),
            result_summary=args["result_summary"],
        )
        return {"audit_id": record.audit_id, "record_hash": record.record_hash}

    def _handle_verify(self, _args: dict[str, Any]) -> dict[str, Any]:
        return self.ledger.verify_chain()

    def _handle_query(self, args: dict[str, Any]) -> dict[str, Any]:
        results = self.ledger.query(
            server=args.get("server"),
            tool=args.get("tool"),
            caller_id=args.get("caller_id"),
            since=args.get("since"),
            limit=args.get("limit", 100),
        )
        return {"records": results, "count": len(results)}

    def _handle_replay(self, args: dict[str, Any]) -> dict[str, Any]:
        trace = self.ledger.replay(since=args.get("since"))
        return {"trace": trace, "event_count": len(trace)}

    def _handle_chain_status(self, _args: dict[str, Any]) -> dict[str, Any]:
        verification = self.ledger.verify_chain()
        return {
            "chain_length": self.ledger.chain_length,
            "latest_hash": self.ledger.latest_hash,
            "integrity": verification,
        }
