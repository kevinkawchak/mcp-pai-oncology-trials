# TrialMCP Pack v0.1.1 Peer Review Recommendations (No Code Changes)

## Proposed Repository Title (Initial)
**TrialMCP Pack: Secure MCP Infrastructure for Autonomous Oncology Clinical Trial Operations**

## Proposed Repository Title (Post-Review Final)
**TrialMCP Pack: Verified MCP Servers for Autonomous Oncology Trial Robotics and Clinical Data Governance**

---

## Scope and Constraints
This peer review provides **recommendations only** (add/remove/modify guidance) to prepare the repository for a full-length academic-style paper and a more production-ready open-source release. No implementation changes are prescribed here as completed work.

---

## Executive Assessment
The repository is already strong in architecture clarity, modular MCP server boundaries, and baseline security/audit testing. To become paper-ready and replication-ready, the project should prioritize:
1. **Server hardening and inter-server contract enforcement** (highest priority).
2. **Deterministic reproducibility artifacts** (datasets + environment pinning + evaluation scripts).
3. **Coverage expansion from happy-path to adversarial and compliance edge cases**.
4. **Research packaging for publication** (methodology, limitations, and statistical/operational metrics).

---

## Critical Recommendations by Directory

## 1) `/servers` (Most Important)

### 1.1 Cross-server architecture and contracts (modify/add)
- **Add a shared `servers/common/` module** with:
  - canonical request/response envelope schemas,
  - shared error taxonomy,
  - structured audit event contract,
  - common input validation utilities.
- **Add JSON Schema/OpenAPI-like MCP tool contracts** for each server tool and version them (`contracts/v1/*.json`).
- **Modify all servers** to return stable machine-readable error codes (e.g., `AUTHZ_DENIED`, `VALIDATION_FAILED`, `NOT_FOUND`, `INTERNAL_ERROR`) in addition to human text.

### 1.2 `trialmcp-authz` (modify/add)
- **Modify token lifecycle**:
  - add token expiration, renewal policy, revocation list, and audience scoping.
- **Add policy semantics tests and policy fixtures**:
  - explicit DENY precedence tests for conflicting policy sets,
  - role inheritance and override behavior,
  - minimum required claims validation.
- **Add policy decision traces**:
  - deterministic, explainable decision logs suitable for auditor review.

### 1.3 `trialmcp-fhir` (modify/add)
- **Modify de-identification implementation**:
  - replace simplistic field dropping with profile-driven rules (resource-specific PHI handling matrix),
  - add configurable de-identification mode (Safe Harbor vs expert determination placeholder mode).
- **Add terminology and profile validation**:
  - optional checks for required coding systems (LOINC, SNOMED CT, RxNorm as applicable).
- **Add pagination and query guardrails**:
  - max page size, max query depth, and result truncation metadata.

### 1.4 `trialmcp-dicom` (modify/add)
- **Modify DICOM query/retrieve security controls**:
  - strict allowlist for query tags,
  - bounded query complexity and request timeouts,
  - retrieval pointer TTL and scope constraints.
- **Add reproducible RECIST extraction assumptions doc**:
  - clarify if measurements are metadata-driven, parser-driven, or synthetic annotation mapping.

### 1.5 `trialmcp-ledger` (modify/add)
- **Modify hash-chain design for stronger paper claims**:
  - explicit canonical serialization before hashing,
  - deterministic ordering and anti-tamper validation rules.
- **Add optional signature support recommendation**:
  - detached signatures or key-based record signing (for non-repudiation claims).
- **Add compaction/snapshot strategy** for long-running chains and replay performance.

### 1.6 `trialmcp-provenance` (modify/add)
- **Modify provenance model**:
  - align event fields with W3C PROV-inspired naming (`entity`, `activity`, `agent` mappings),
  - add linkage to ledger hash IDs for end-to-end traceability.
- **Add provenance consistency checker**:
  - detect missing source registrations,
  - validate referential integrity between provenance records and originating server events.

### 1.7 Operational robustness across all servers (add)
- Add:
  - health/readiness endpoints,
  - structured logging format and correlation IDs,
  - rate limiting and concurrency test harness,
  - server benchmark script for latency/throughput metrics used in paper tables.

---

## 2) `/clients` recommendations

### 2.1 `clients/reference_agent` (modify/add)
- **Modify workflow orchestration**:
  - explicit state machine with retry/backoff/idempotency controls,
  - failure compensation paths (partial workflow rollback semantics).
- **Add typed client interfaces** for each MCP server to prevent schema drift.
- **Add reproducibility mode** with deterministic IDs/seeds for paper experiment reruns.
- **Add telemetry export** for workflow timing, failure rates, and audit round-trip latency.

### 2.2 Additional client artifacts (add)
- Add a second reference client profile (e.g., `monitor_agent`) to demonstrate role-specific tool surfaces and least-privilege behavior in the paper.

---

## 3) `/datasets` recommendations

### 3.1 Dataset governance and reproducibility (add/modify)
- **Add `datasets/README.md`** with:
  - provenance of synthetic data generation,
  - schema versions and known limitations,
  - data dictionary for each file.
- **Add checksums/manifest** (`datasets/manifest.json` with SHA-256 per file).
- **Modify dataset structure** to include `raw/`, `processed/`, and `metadata/` split for clearer research workflows.

### 3.2 Scientific utility improvements (add)
- Add richer synthetic cohort diversity (age bands, disease stage variability, treatment arms).
- Add edge-case records intentionally designed for stress testing (missing fields, malformed coding, temporal inconsistencies).
- Add licensing and usage note per dataset subfolder for publication clarity.

---

## 4) `/tests` recommendations

### 4.1 Security tests (add/modify)
- Expand SSRF/injection coverage to include:
  - encoded payload variants,
  - nested object injection,
  - boundary condition fuzzing.
- Add authz abuse tests:
  - token replay across roles,
  - stale token use,
  - cross-server privilege escalation attempts.

### 4.2 Integration and systems tests (add)
- Add full cross-server trace test:
  - `authz -> fhir/dicom -> provenance -> ledger` linkage integrity verification.
- Add deterministic regression snapshots for representative tool outputs.
- Add load/performance tests with fixed scenarios to support methodology section metrics.

### 4.3 Compliance-oriented tests (add)
- Add explicit 21 CFR Part 11 mapping tests for audit trail completeness assumptions.
- Add de-identification leakage tests with red-team style PHI probes.

---

## Repository-level Recommendations (Main Branch)

### Include these additional files/directories on `main`
- `paper/`
  - `paper/main.tex` (or markdown equivalent),
  - figures/tables used in the manuscript,
  - reproducibility appendix.
- `docs/`
  - threat model,
  - architecture decision records,
  - interoperability profiles.
- `contracts/`
  - versioned MCP tool schemas and compatibility policy.
- `scripts/`
  - benchmark runner,
  - dataset validation,
  - reproducibility bootstrap.
- `.github/workflows/`
  - CI for tests + lint + schema validation + docs link checks.
- `SECURITY.md`, `GOVERNANCE.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`.
- `CITATION.cff` and `codemeta.json` for academic indexing.

### Remove or refactor recommendations
- Remove implicit behavior where tool-side defaults can hide security assumptions.
- Refactor any duplicated validation logic into shared modules to avoid divergence.

---

## Paper-Readiness Checklist (Recommended)
- Threat model complete and linked to test cases.
- Reproducibility package can recreate benchmark tables from clean environment.
- Dataset manifest and schema docs finalized.
- Each key claim in README tied to a test, benchmark, or documented limitation.
- Versioned API/tool contracts frozen for the submission window.

---

## Proposed Release Positioning Note
For v0.1.1, describe this as a **stabilization and publication-readiness planning release** focused on contract hardening, reproducibility, and compliance/testing expansion recommendations.

---

## Contributor/Identity Display Recommendation
To ensure visibility on `main`, include explicit contributor mentions in top-level docs and release metadata:
- `@kevinkawchak`
- `@claude`
- `@codex`

