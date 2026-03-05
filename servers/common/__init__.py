"""
servers.common: Shared utilities for the TrialMCP Pack server suite.

Provides canonical request/response envelope schemas, a shared error
taxonomy with machine-readable error codes, structured audit event
contracts, and common input validation utilities used across all five
MCP servers.

This module was introduced in v0.2.0 following peer-review recommendation
1.1 (cross-server architecture and contracts) to eliminate duplicated
validation logic and enforce consistent error surfaces.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any


# ---------------------------------------------------------------------------
# Machine-readable error codes  (peer-review rec 1.1)
# ---------------------------------------------------------------------------

class ErrorCode:
    """Stable, machine-readable error codes returned by all servers."""

    AUTHZ_DENIED = "AUTHZ_DENIED"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    NOT_FOUND = "NOT_FOUND"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_REVOKED = "TOKEN_REVOKED"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    INVALID_INPUT = "INVALID_INPUT"
    RATE_LIMITED = "RATE_LIMITED"


def error_response(
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a standardised error envelope."""
    resp: dict[str, Any] = {"error": message, "error_code": code}
    if details:
        resp["details"] = details
    return resp


# ---------------------------------------------------------------------------
# Input validation utilities  (peer-review rec 1.1 / 1.4)
# ---------------------------------------------------------------------------

_URL_PATTERN = re.compile(r"https?://", re.IGNORECASE)
_DICOM_UID_PATTERN = re.compile(r"^[\d.]+$")
_FHIR_ID_PATTERN = re.compile(r"^[A-Za-z0-9\-._]+$")


def validate_fhir_id(value: str) -> bool:
    """Return True if *value* looks like a valid FHIR logical ID."""
    if _URL_PATTERN.search(value):
        return False
    return bool(_FHIR_ID_PATTERN.match(value))


def validate_dicom_uid(value: str) -> bool:
    """Return True if *value* looks like a valid DICOM UID."""
    if _URL_PATTERN.search(value):
        return False
    return bool(_DICOM_UID_PATTERN.match(value))


def validate_no_url(value: str) -> bool:
    """Reject values that embed URLs (SSRF prevention)."""
    return not _URL_PATTERN.search(value)


# ---------------------------------------------------------------------------
# Health / readiness helpers  (peer-review rec 1.7)
# ---------------------------------------------------------------------------

def health_status(server_name: str, version: str) -> dict[str, Any]:
    """Return a standard health-check response."""
    return {
        "server": server_name,
        "version": version,
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
