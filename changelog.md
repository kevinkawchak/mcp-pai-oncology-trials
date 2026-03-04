# Changelog

All notable changes to the TrialMCP Pack project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-03-04

### Added

#### MCP Servers
- **trialmcp-fhir**: Read-only FHIR R4 MCP server with scoped access to 9 oncology trial resource types (Patient, ResearchStudy, ResearchSubject, Condition, MedicationAdministration, Observation, AdverseEvent, DiagnosticReport, ImagingStudy). Includes HIPAA Safe Harbor de-identification pipeline with HMAC-SHA256 pseudonymization.
- **trialmcp-dicom**: DICOM query/retrieve proxy MCP server with C-FIND and C-MOVE support, role-based permission enforcement (trial_coordinator, robot_agent, data_monitor, auditor), time-limited retrieval tokens, and RECIST 1.1 tumor measurement access.
- **trialmcp-ledger**: Append-only, hash-chained audit ledger MCP server for 21 CFR Part 11 compliance. SHA-256 linked records with tamper detection, chain verification, filtered queries, and replayable audit traces.
- **trialmcp-authz**: Authorization policy MCP server with RBAC policy engine, deny-by-default semantics, explicit DENY precedence, session token management, and pre-configured policy templates for clinical trial roles.
- **trialmcp-provenance**: Data provenance gateway MCP server with source registration, access recording, lineage tracking, actor history, and SHA-256 data integrity verification.

#### Reference Client
- **Trial Robot Agent**: Reference MCP client demonstrating autonomous trial robot integration. Six-step workflow: authenticate, fetch task order, retrieve imaging, execute procedure, upload evidence, record provenance. Supports Franka Panda, da Vinci dVRK, Kinova Gen3, and other USL-scored platforms.

#### Datasets
- Synthetic FHIR R4 bundles: 14 resources across 9 resource types for two oncology clinical trials (Phase II robotic biopsy, Phase III adaptive immunotherapy).
- Synthetic DICOM study index: 3 imaging studies (CT Chest, MR Abdomen, PET/CT) with RECIST 1.1 target lesion measurements across 2 trial sites.
- Simulated scheduling data: 3 robotic procedure events with USL-scored platform assignments and prerequisite tracking.

#### Testing
- Security test suite (10 tests): SSRF prevention, injection prevention, permission escalation defense, replay attack prevention.
- Audit completeness test suite (12 tests): Every MCP tool call produces signed audit records, hash-chain integrity, genesis hash verification, replay trace ordering.
- Integration test suite (8 tests): End-to-end robot agent workflow, de-identification verification, permission enforcement, audit chain integrity after workflows.

#### Documentation
- Comprehensive README with 6 text diagrams covering architecture, audit chain, robot workflow, federated deployment, data flow security, and tool surface area.
- Release notes, changelog, and build prompts.

#### Infrastructure
- Python 3.11+ project configuration via pyproject.toml
- 23 MCP tools across 5 servers
- 30 tests, all passing
