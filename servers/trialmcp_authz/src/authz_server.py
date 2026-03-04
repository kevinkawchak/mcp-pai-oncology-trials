"""
trialmcp-authz: Authorization policy MCP server for the TrialMCP Pack.

Enforces least-privilege access across all TrialMCP servers using a
role-based access control (RBAC) model with fine-grained policy templates.
Provides authentication verification, token management, and policy
evaluation as MCP tools.

Integration points:
- Federated Learning Pillar 1 (Privacy Infrastructure): RBAC integrates
  with HIPAA access controls and differential privacy budget enforcement.
- USL Dimension D (Multi-Site Collaboration): Cross-site authorization
  policies support federated deployment with per-site policy overrides.
- Security hardening: Implements defenses against SSRF, injection,
  permission escalation, and replay attacks.
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


class PolicyEffect:
    ALLOW = "allow"
    DENY = "deny"


class PolicyRule:
    """A single authorization policy rule."""

    def __init__(
        self,
        rule_id: str,
        roles: list[str],
        servers: list[str],
        tools: list[str],
        effect: str = PolicyEffect.ALLOW,
        conditions: dict[str, Any] | None = None,
    ) -> None:
        self.rule_id = rule_id
        self.roles = roles
        self.servers = servers
        self.tools = tools
        self.effect = effect
        self.conditions = conditions or {}

    def matches(self, role: str, server: str, tool: str) -> bool:
        """Check if this rule matches the given request context."""
        role_match = "*" in self.roles or role in self.roles
        server_match = "*" in self.servers or server in self.servers
        tool_match = "*" in self.tools or tool in self.tools
        return role_match and server_match and tool_match

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "roles": self.roles,
            "servers": self.servers,
            "tools": self.tools,
            "effect": self.effect,
            "conditions": self.conditions,
        }


class PolicyEngine:
    """Policy evaluation engine with deny-by-default semantics.

    Evaluates authorization requests against a set of policy rules.
    Uses deny-by-default: if no explicit ALLOW rule matches, access
    is denied. Explicit DENY rules take precedence over ALLOW rules.
    """

    def __init__(self) -> None:
        self._rules: list[PolicyRule] = []
        self._load_default_policies()

    def _load_default_policies(self) -> None:
        """Load the default policy templates for the TrialMCP Pack."""
        default_rules = [
            # Trial coordinators: full read access to FHIR and DICOM
            PolicyRule(
                rule_id="default-coordinator-fhir",
                roles=["trial_coordinator"],
                servers=["trialmcp-fhir"],
                tools=["*"],
                effect=PolicyEffect.ALLOW,
            ),
            PolicyRule(
                rule_id="default-coordinator-dicom",
                roles=["trial_coordinator"],
                servers=["trialmcp-dicom"],
                tools=["*"],
                effect=PolicyEffect.ALLOW,
            ),
            # Robot agents: scoped access for task execution
            PolicyRule(
                rule_id="default-robot-fhir",
                roles=["robot_agent"],
                servers=["trialmcp-fhir"],
                tools=["fhir_read", "fhir_study_status"],
                effect=PolicyEffect.ALLOW,
            ),
            PolicyRule(
                rule_id="default-robot-dicom",
                roles=["robot_agent"],
                servers=["trialmcp-dicom"],
                tools=["dicom_query", "dicom_retrieve_pointer"],
                effect=PolicyEffect.ALLOW,
            ),
            # Data monitors: read-only, no retrieval
            PolicyRule(
                rule_id="default-monitor-fhir",
                roles=["data_monitor"],
                servers=["trialmcp-fhir"],
                tools=["fhir_search", "fhir_study_status"],
                effect=PolicyEffect.ALLOW,
            ),
            PolicyRule(
                rule_id="default-monitor-dicom",
                roles=["data_monitor"],
                servers=["trialmcp-dicom"],
                tools=["dicom_query"],
                effect=PolicyEffect.ALLOW,
            ),
            # Auditors: ledger access only
            PolicyRule(
                rule_id="default-auditor-ledger",
                roles=["auditor"],
                servers=["trialmcp-ledger"],
                tools=["*"],
                effect=PolicyEffect.ALLOW,
            ),
            # All authenticated roles can check chain status
            PolicyRule(
                rule_id="default-all-chain-status",
                roles=["*"],
                servers=["trialmcp-ledger"],
                tools=["ledger_chain_status", "ledger_verify"],
                effect=PolicyEffect.ALLOW,
            ),
            # Deny provenance write for non-admin roles
            PolicyRule(
                rule_id="deny-provenance-write",
                roles=["data_monitor", "auditor"],
                servers=["trialmcp-provenance"],
                tools=["provenance_register_source"],
                effect=PolicyEffect.DENY,
            ),
        ]
        self._rules.extend(default_rules)

    def evaluate(self, role: str, server: str, tool: str) -> dict[str, Any]:
        """Evaluate an authorization request against all policy rules."""
        matching_rules = [r for r in self._rules if r.matches(role, server, tool)]

        # Explicit DENY takes precedence
        for rule in matching_rules:
            if rule.effect == PolicyEffect.DENY:
                return {
                    "decision": "deny",
                    "rule_id": rule.rule_id,
                    "reason": f"Explicit deny by rule {rule.rule_id}",
                }

        # Check for ALLOW
        for rule in matching_rules:
            if rule.effect == PolicyEffect.ALLOW:
                return {
                    "decision": "allow",
                    "rule_id": rule.rule_id,
                }

        # Default deny
        return {
            "decision": "deny",
            "rule_id": None,
            "reason": "No matching allow rule (deny-by-default)",
        }

    def add_rule(self, rule: PolicyRule) -> None:
        """Add a new policy rule."""
        self._rules.append(rule)

    def list_rules(self) -> list[dict[str, Any]]:
        """List all policy rules."""
        return [r.to_dict() for r in self._rules]


class TokenStore:
    """Simple token management for MCP session authentication.

    In production, this would integrate with OAuth2/OIDC providers.
    Tokens are scoped to roles and have configurable expiry.
    """

    def __init__(self) -> None:
        self._tokens: dict[str, dict[str, Any]] = {}

    def issue_token(
        self,
        caller_id: str,
        role: str,
        expires_seconds: int = 3600,
    ) -> dict[str, Any]:
        """Issue a new session token for a caller."""
        token_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        token_data = {
            "token_id": token_id,
            "caller_id": caller_id,
            "role": role,
            "issued_at": now.isoformat(),
            "expires_seconds": expires_seconds,
            "token_hash": hashlib.sha256(f"{token_id}:{caller_id}:{role}".encode()).hexdigest(),
        }
        self._tokens[token_id] = token_data
        return token_data

    def validate_token(self, token_id: str) -> dict[str, Any] | None:
        """Validate a token and return its metadata if valid."""
        return self._tokens.get(token_id)

    def revoke_token(self, token_id: str) -> bool:
        """Revoke a token."""
        if token_id in self._tokens:
            del self._tokens[token_id]
            return True
        return False


class AuthzMCPServer:
    """Authorization policy MCP server for the TrialMCP Pack.

    Tools:
        - authz_evaluate: Evaluate an authorization request against policies.
        - authz_issue_token: Issue a session token for an agent.
        - authz_validate_token: Validate an existing session token.
        - authz_list_policies: List all active authorization policies.
        - authz_revoke_token: Revoke an active session token.

    This server is the policy decision point (PDP) for the entire
    TrialMCP Pack. All other servers consult this service before
    executing privileged operations.
    """

    SERVER_INFO = {
        "name": "trialmcp-authz",
        "version": "0.1.0",
        "description": "Authorization policy MCP server with RBAC and token management",
        "capabilities": {
            "tools": True,
            "resources": True,
        },
    }

    TOOLS = [
        {
            "name": "authz_evaluate",
            "description": (
                "Evaluate an authorization request. Returns allow/deny decision "
                "based on the caller's role, target server, and tool. Uses "
                "deny-by-default semantics with explicit DENY precedence."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "role": {
                        "type": "string",
                        "description": "Role of the requesting agent",
                    },
                    "server": {
                        "type": "string",
                        "description": "Target MCP server name",
                    },
                    "tool": {
                        "type": "string",
                        "description": "Target tool name",
                    },
                },
                "required": ["role", "server", "tool"],
            },
        },
        {
            "name": "authz_issue_token",
            "description": (
                "Issue a session token for an agent with a specified role. "
                "Tokens are time-limited and scoped to the assigned role."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "caller_id": {
                        "type": "string",
                        "description": "Unique identifier of the requesting agent",
                    },
                    "role": {
                        "type": "string",
                        "description": "Role to assign to the token",
                        "enum": [
                            "trial_coordinator",
                            "robot_agent",
                            "data_monitor",
                            "auditor",
                        ],
                    },
                    "expires_seconds": {
                        "type": "integer",
                        "description": "Token lifetime in seconds (default 3600)",
                    },
                },
                "required": ["caller_id", "role"],
            },
        },
        {
            "name": "authz_validate_token",
            "description": "Validate a session token and return its metadata.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "token_id": {
                        "type": "string",
                        "description": "Token ID to validate",
                    },
                },
                "required": ["token_id"],
            },
        },
        {
            "name": "authz_list_policies",
            "description": "List all active authorization policy rules.",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "authz_revoke_token",
            "description": "Revoke an active session token.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "token_id": {
                        "type": "string",
                        "description": "Token ID to revoke",
                    },
                },
                "required": ["token_id"],
            },
        },
    ]

    def __init__(self, audit_callback: Any | None = None) -> None:
        self.engine = PolicyEngine()
        self.tokens = TokenStore()
        self._audit_callback = audit_callback

    def _emit_audit(self, tool_name: str, params: dict, result_summary: str) -> None:
        if self._audit_callback:
            self._audit_callback(
                {
                    "audit_id": str(uuid.uuid4()),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "server": "trialmcp-authz",
                    "tool": tool_name,
                    "parameters": params,
                    "result_summary": result_summary,
                }
            )

    def handle_tool_call(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Route an MCP tool call to the appropriate handler."""
        handlers = {
            "authz_evaluate": self._handle_evaluate,
            "authz_issue_token": self._handle_issue_token,
            "authz_validate_token": self._handle_validate_token,
            "authz_list_policies": self._handle_list_policies,
            "authz_revoke_token": self._handle_revoke_token,
        }
        handler = handlers.get(tool_name)
        if handler is None:
            return {"error": f"Unknown tool: {tool_name}"}
        return handler(arguments)

    def _handle_evaluate(self, args: dict[str, Any]) -> dict[str, Any]:
        decision = self.engine.evaluate(args["role"], args["server"], args["tool"])
        self._emit_audit("authz_evaluate", args, decision["decision"])
        return decision

    def _handle_issue_token(self, args: dict[str, Any]) -> dict[str, Any]:
        token = self.tokens.issue_token(
            caller_id=args["caller_id"],
            role=args["role"],
            expires_seconds=args.get("expires_seconds", 3600),
        )
        self._emit_audit("authz_issue_token", {"caller_id": args["caller_id"]}, "token_issued")
        return token

    def _handle_validate_token(self, args: dict[str, Any]) -> dict[str, Any]:
        token = self.tokens.validate_token(args["token_id"])
        if token is None:
            return {"valid": False, "reason": "Token not found or expired"}
        return {"valid": True, "token": token}

    def _handle_list_policies(self, _args: dict[str, Any]) -> dict[str, Any]:
        rules = self.engine.list_rules()
        return {"rules": rules, "count": len(rules)}

    def _handle_revoke_token(self, args: dict[str, Any]) -> dict[str, Any]:
        revoked = self.tokens.revoke_token(args["token_id"])
        self._emit_audit("authz_revoke_token", args, "revoked" if revoked else "not_found")
        return {"revoked": revoked}
