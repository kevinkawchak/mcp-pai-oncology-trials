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
