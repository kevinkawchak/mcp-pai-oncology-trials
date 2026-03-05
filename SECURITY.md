# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.2.x   | Yes       |
| 0.1.x   | No        |

## Reporting a Vulnerability

If you discover a security vulnerability in the TrialMCP Pack, please report it responsibly:

1. **Do not** open a public GitHub issue for security vulnerabilities.
2. Email the maintainer at the contact listed in the repository profile.
3. Include a description of the vulnerability, steps to reproduce, and potential impact.
4. You will receive an acknowledgement within 48 hours.

## Security Architecture

The TrialMCP Pack implements multiple layers of defense:

- **Authorization:** Deny-by-default RBAC with explicit DENY precedence (`trialmcp-authz`)
- **Authentication:** Token-based session management with expiry enforcement
- **Input validation:** SSRF prevention, FHIR ID validation, DICOM UID validation
- **Privacy:** HIPAA Safe Harbor de-identification with HMAC-SHA256 pseudonymization
- **Integrity:** SHA-256 hash-chained audit ledger for tamper detection
- **Audit:** Every MCP tool call produces a signed audit record

## Security Testing

The test suite includes:

- SSRF prevention tests (URL-based resource IDs, encoded variants)
- Injection prevention tests (JSON injection, SQL injection patterns)
- Permission escalation tests (role boundary enforcement)
- Token lifecycle tests (revocation, expiry enforcement)
- Hash-chain integrity verification
- Health endpoint availability checks
- Policy decision trace validation
