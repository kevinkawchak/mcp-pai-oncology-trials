Release title
v0.2.0 - TrialMCP Pack: Peer-Review Hardening and Publication Readiness

## Summary
This release implements code fixes and structural improvements based on the @codex v0.1.1 peer-review recommendations, advancing the TrialMCP Pack toward full-length paper publication readiness. Key changes include token expiry enforcement, shared error taxonomy across all servers, input validation with SSRF prevention, health/readiness endpoints, policy decision traces, pagination guards, dataset governance artifacts, and expanded test coverage from 30 to 39 tests (all passing).

## Features
- **Shared common module** (`servers/common/`): Machine-readable error codes (`AUTHZ_DENIED`, `VALIDATION_FAILED`, `NOT_FOUND`, etc.), input validation utilities (FHIR ID format, DICOM UID format, URL rejection), and health endpoint helper -- addressing peer-review recommendation 1.1 (cross-server contracts).
- **Token expiry enforcement**: Tokens now include `expires_at` timestamps and are automatically rejected after expiration -- addressing peer-review recommendation 1.2 (token lifecycle).
- **Policy decision traces**: `authz_evaluate` responses now include a trace of all matching rules for auditable authorization decisions -- addressing peer-review recommendation 1.2 (policy decision traces).
- **Input validation**: FHIR resource IDs and DICOM UIDs are validated against format patterns; URLs are rejected at the validation layer with `VALIDATION_FAILED` error codes -- addressing peer-review recommendations 1.1 and 1.4 (security controls).
- **Health endpoints**: All five MCP servers expose a `health` tool returning server name, version, status, and timestamp -- addressing peer-review recommendation 1.7 (operational robustness).
- **Pagination guard**: FHIR search now enforces `max_results` to prevent unbounded result sets -- addressing peer-review recommendation 1.3 (query guardrails).
- **Dataset governance**: `datasets/README.md` with data dictionary, provenance, and known limitations; `datasets/manifest.json` with SHA-256 checksums -- addressing peer-review recommendation 3.1.
- **Repository-level files**: `SECURITY.md`, `CONTRIBUTING.md`, `CITATION.cff` for publication readiness -- addressing peer-review repository-level recommendations.
- **3 new Mermaid diagrams** in README: peer-review development lifecycle, quality assurance cycle, and MCP PAI oncology trial lifecycle.
- **Expanded test suite**: 9 new tests including token expiry, encoded SSRF variants, health endpoints, policy traces, and cross-server integration trace.
- **Contributor icons**: @kevinkawchak, @claude, and @codex profile images in README Team section.

## Contributors
@kevinkawchak
@claude
@codex

## Notes
- All 39 tests pass. Test suite expanded from 30 (v0.1.0) to 39.
- All five MCP server versions updated to 0.2.0.
- This release addresses peer-review recommendations from `peer-review/trialmcp_pack_v0.1.1_peer_review.md` sections 1.1 (shared contracts), 1.2 (token lifecycle, policy traces), 1.3 (pagination), 1.4 (DICOM security), 1.7 (health endpoints), 3.1 (dataset governance), and repository-level recommendations (SECURITY.md, CONTRIBUTING.md, CITATION.cff).
- Remaining peer-review recommendations (1.3 de-identification profiles, 1.5 signature support, 1.6 W3C PROV alignment, 2.1 client state machine, 4.1-4.3 adversarial tests, paper/ directory, CI/CD workflows) are documented as future work.
- Python 3.11+ required. No new external dependencies.

---

Release title
v0.1.1 - Publication-Readiness Recommendations and Peer Review Packaging

## Summary
This release adds a formal peer-review recommendations package for preparing TrialMCP Pack for a full-length academic paper and production-oriented hardening roadmap. The update intentionally avoids direct code or file fixes to server/client runtime behavior and instead documents prioritized remediation and expansion guidance.

## Features
- Added a new peer-review recommendation file under `/peer-review/` with detailed add/remove/modify guidance spanning `/servers`, `/clients`, `/datasets`, `/tests`, and repository-level publication assets.
- Added v0.1.1 changelog entry focused on recommendation-only scope.
- Updated `prompts.md` with the exact latest user prompt for downstream Claude Code iteration.
- Added visible top-level contributor references so `@codex` appears alongside `@claude` and `@kevinkawchak` on main documentation surfaces.

## Contributors
@kevinkawchak
@codex

## Notes
This is a recommendation-only release and is intended as an input artifact for subsequent implementation work.

## Release title
v0.1.0 - TrialMCP Pack: MCP Servers for Physical AI Oncology Clinical Trial Systems

## Summary

Initial release of the TrialMCP Pack, a suite of five open MCP (Model Context Protocol) servers and a reference trial robot agent client for Physical AI oncology clinical trial systems. This release establishes the foundational M1 milestone: read-only clinical data MCP servers with a complete authorization framework, privacy-preserving data access, and 21 CFR Part 11 compliant audit logging. The system bridges autonomous oncology trial robots (scored via the Unification Standard Level framework) with clinical infrastructure including FHIR repositories, DICOM imaging archives, and trial scheduling systems through the MCP protocol.

## Features

- **trialmcp-fhir**: Read-only FHIR R4 MCP server providing scoped access to 9 oncology trial resource types with HIPAA Safe Harbor de-identification (HMAC-SHA256 pseudonymization, 18-identifier removal, birth date generalization). Tools: `fhir_read`, `fhir_search`, `fhir_patient_lookup`, `fhir_study_status`.

- **trialmcp-dicom**: DICOM query/retrieve proxy MCP server with C-FIND/C-MOVE support, role-based permission matrix (4 roles x 3 query levels x 10 modalities), time-limited secure retrieval tokens, and RECIST 1.1 tumor measurement access. Tools: `dicom_query`, `dicom_retrieve_pointer`, `dicom_study_metadata`, `dicom_recist_measurements`.

- **trialmcp-ledger**: Append-only, SHA-256 hash-chained audit ledger for 21 CFR Part 11 and ICH-GCP E6(R2) compliance. Tamper-evident chain with verification, filtered queries, and replayable audit traces. Tools: `ledger_append`, `ledger_verify`, `ledger_query`, `ledger_replay`, `ledger_chain_status`.

- **trialmcp-authz**: Authorization policy decision point with deny-by-default RBAC, explicit DENY precedence, session token management, and pre-configured policy templates for trial coordinators, robot agents, data monitors, and auditors. Tools: `authz_evaluate`, `authz_issue_token`, `authz_validate_token`, `authz_list_policies`, `authz_revoke_token`.

- **trialmcp-provenance**: Data provenance gateway enforcing least-privilege access with source registration, access/transformation recording, lineage tracking, actor history, and SHA-256 data integrity verification. Tools: `provenance_register_source`, `provenance_record_access`, `provenance_get_lineage`, `provenance_get_actor_history`, `provenance_verify_integrity`.

- **Trial Robot Agent**: Reference MCP client demonstrating end-to-end autonomous robot integration across all 5 servers. Six-step workflow from authentication through provenance recording, supporting USL-scored platforms (Franka Panda 7.4, da Vinci dVRK 7.1, Kinova Gen3 5.7).

- **Synthetic Datasets**: FHIR R4 bundles (14 resources, 2 trials), DICOM study index (3 studies with RECIST 1.1), and scheduling data (3 robotic procedures across 2 sites).

- **Security Test Suite**: 30 tests covering SSRF prevention, injection defense, permission escalation, replay attacks, audit completeness, hash-chain integrity, and end-to-end robot workflows.

## Contributors
@kevinkawchak
@claude

## Notes

- This release represents the M1 milestone (0-4 months): read-only clinical data MCP servers with authorization framework.
- All MCP servers are currently in-memory implementations. Production deployments will require integration with actual FHIR servers (HAPI FHIR), PACS systems (Orthanc, dcm4chee), and persistent storage.
- The authorization framework uses simplified token management. Production deployments should integrate with OAuth2/OIDC providers.
- Synthetic datasets are provided for development and testing. Real clinical data requires institutional partnerships and IRB approval.
- USL scores referenced from the Unification Standard Level evaluation framework for robotic platform readiness assessment.
- Federated learning integration points are documented but not yet implemented as live cross-site communication. See M2 milestones for planned federated deployment.
- Python 3.11+ required. No external dependencies beyond jsonschema for validation.

