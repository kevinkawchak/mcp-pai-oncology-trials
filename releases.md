# Releases

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
