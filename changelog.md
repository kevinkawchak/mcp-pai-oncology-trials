# Changelog

## [0.2.0] - 2026-03-05

### Added
- Added `servers/common/__init__.py` shared module with machine-readable error codes (`AUTHZ_DENIED`, `VALIDATION_FAILED`, `NOT_FOUND`, `INTERNAL_ERROR`, `TOKEN_EXPIRED`, `PERMISSION_DENIED`, `INVALID_INPUT`), input validation utilities (FHIR ID, DICOM UID, SSRF prevention), and health/readiness endpoint helper.
- Added token expiry enforcement in `trialmcp-authz`: tokens now include `expires_at` and are automatically rejected after expiration.
- Added policy decision traces to `authz_evaluate` responses for auditable authorization decisions.
- Added FHIR ID input validation to `fhir_read` and `fhir_patient_lookup` (rejects URLs, enforces format).
- Added DICOM UID input validation to `dicom_retrieve_pointer` (rejects URLs, enforces numeric-dot format).
- Added health/readiness endpoints (`health` tool) to all five MCP servers.
- Added pagination guard (`max_results`) to FHIR search to prevent unbounded result sets.
- Added 9 new tests: token expiry enforcement, encoded SSRF variant, health endpoints (4 servers), policy decision traces (allow/deny), cross-server trace integration test.
- Added `datasets/README.md` with data dictionary, provenance, and known limitations.
- Added `datasets/manifest.json` with SHA-256 checksums for all dataset files.
- Added `SECURITY.md` with vulnerability reporting policy and security architecture overview.
- Added `CONTRIBUTING.md` with development guidelines and contribution process.
- Added `CITATION.cff` for academic citation metadata.
- Added `peer-review/v0.2.0_peer_review_response.md` documenting which @codex recommendations were implemented.
- Added 3 new professional Mermaid diagrams to README: peer-review development lifecycle, quality assurance cycle, and MCP PAI oncology trial lifecycle.
- Added contributor icons table in README Team section with @kevinkawchak, @claude, and @codex profile images.
- Added copy of v0.2.0 build prompt to `prompts.md`.

### Changed
- Updated all server versions from 0.1.0 to 0.2.0.
- Updated `pyproject.toml` version to 0.2.0.
- Modified all servers to use shared error codes from `servers/common` instead of ad-hoc error strings.
- Modified `authz_evaluate` to include trace of all matching rules in response.
- Modified token hash computation to include timestamp for uniqueness.
- Fixed test assertion in `test_robot_fetch_task_order` (was always passing due to OR logic).
- Updated README badges: version 0.2.0, 39 tests passing.
- Updated README security section to reflect expanded test suite and new hardening measures.
- Updated README repository structure to include new files and directories.

### Notes
- This version implements code fixes and structural improvements based on the @codex v0.1.1 peer-review recommendations.
- Test suite expanded from 30 to 39 tests (all passing).
- All servers now share a common error taxonomy and validation layer.

## [0.1.1] - 2026-03-05

### Added
- Added `peer-review/trialmcp_pack_v0.1.1_peer_review.md` with prioritized recommendations for server hardening, client orchestration improvements, dataset governance, test expansion, and publication-readiness repository structure.
- Added the exact latest user request into `prompts.md` for traceability of build/review intent.

### Changed
- Updated `releases.md` with v0.1.1 release notes in the required format.
- Updated `README.md` contributor visibility line to include `@codex` alongside `@claude` and `@kevinkawchak` on main.

### Notes
- This version contains recommendations/documentation updates only and intentionally applies no runtime code fixes.

## [0.1.0] - 2026-03-05

### Added
- Initial TrialMCP Pack release with five MCP servers (`trialmcp-fhir`, `trialmcp-dicom`, `trialmcp-ledger`, `trialmcp-authz`, `trialmcp-provenance`).
- Reference trial robot client with end-to-end workflow demonstration.
- Synthetic FHIR, DICOM, and scheduling datasets.
- Security, audit completeness, and integration test suites.
- Project documentation, release metadata, and prompt history.
