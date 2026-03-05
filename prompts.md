# Build Prompts

## Publication Readiness Prompt (v0.2.0)

Based on addressing these @codex peer-review recommendations and performing additional checks and tests by yourself: prepare the repository for a future full-length paper publication: kevinkawchak/mcp-pai-oncology-trials/blob/main/peer-review/trialmcp_pack_v0.1.1_peer_review.md
Keep the existing "MCP Servers for Physical AI Oncology Clinical Trial Systems" and "TrialMCP Pack: MCP servers for oncology clinical trial systems" titles.

Distribute 3 new professional colored mermaid diagrams that are novel vs. other repo diagrams throughout the readme (2 on the repo's peer-review process, 1 on the overall mcp pai oncology trial) (white background, clean, modern, subtle "3D" card feel with rounded rectangles, cylinder shapes, thin darker border around nodes, soft pastel fills with high contrast centered text, readable, and consistent sizing, with short labels.)

Make sure to clone the current repo. Be sure to fix and address errors that would cause failed checks for the single pull request. Place the new release notes in releases.md under main using the format below. Again, take the time to make sure the entire repository context is consistent for a future full-length paper.

Provide an updated changelog.md (v0.2.0). Provide a copy of this prompt under the main prompts.md file. Provide a new markdown under /peer-review in response to the @codex recommendation fixes you made. Make sure @codex icons also show in main contributors section (by the user and @claude round icons). When you are finished, auto-push the update to GitHub on your own for my review. The user will then review your updates in GitHub prior to finalization.

"FORMAT"
Release title
v0.2.0 -

## Summary

## Features

## Contributors
@kevinkawchak
@claude
@codex

## Notes

---

## Peer Review Prompt (v0.1.1)

Your goal for the mcp-pai-oncology-trials repository is to provide recommendations regarding code fixes and repo fixes in order to make TrialMCP Pack ready for a full-length academic style paper. Be sure to provide recommended fixes to /clients, /datasets, and /tests directories code and files. Most importantly, provide code and file fix recommendations (add/remove/modify) to the /servers directory. Only recommendations are needed, no fixes. Also include what other files and directories should be included on main that are relevant to the project. Place your exact output in a new /peer-review directory markdown file based on this version. Claude Code will then utilize your file in future steps to then create a new version based on your recommendations. 

Provide a new proposed title for the existing mcp-pai-oncology-trials repository (if different from “MCP Servers for Physical AI Oncology Clinical Trial Systems”) then after making code fix and repo fix recommendations, provide a new title (if different from “MCP Servers for Physical AI Oncology Clinical Trial Systems”). Make sure the @codex icon logo will show on main alongside the user and @claude. 

Make sure to clone the current repo. Place the new release notes in releases.md under main using the format below. Do not make any code fixes or file fixes, only recommendations. Provide an updated changelog.md (v0.1.1). Provide a copy of this  exact prompt under a main prompts.md file. When you are finished, auto-push the update to GitHub on your own for my review. The user will then review your updates in GitHub prior to finalization.

“FORMAT”
Release title
v0.1.1 -

## Summary

## Features

## Contributors
@kevinkawchak
@codex

## Notes

---

## Initial Build Prompt (v0.1.0)

MCP Servers for Physical AI Oncology Clinical Trial Systems (TrialMCP Pack)
Your goal is to build a suite of open MCP servers and reference clients for the GitHub repository mcp-pai-oncology-trials primarily using the following guides, and the instructions at the bottom:
1) kevinkawchak/physical-ai-oncology-trials (Integrate codebase from robots, software, connectivity, etc., where appropriate)
2) kevinkawchak/physical-ai-oncology-trials/blob/main/unification/usl/paper/usl_oncology_trials.tex (Integrate unification standard level and implications, where appropriate)
3) kevinkawchak/pai-oncology-trial-fl/blob/main/paper/main.tex (Integrate federated learning pai oncology trials, where appropriate)

Use 3 flow chart text diagrams and 3 text diagrams that describe different perspectives on the process and/or the utility to the field - distributed throughout main Readme. The main readme needs badges at the top for language version, date, etc. Make sure all relevant information is included for the mcp servers and process as a whole, as a paper based on your output will be published in future steps.

Make sure to clone the current repo. Be sure to fix and address errors that would cause failed checks for the single pull request Place the new release notes in releases.md under main using the format below.

Provide an updated changelog.md (v0.1.0). Provide a copy of this prompt under a main prompts.md file. When you are finished, auto-push the update to GitHub on your own for my review. The user will then review your updates in GitHub prior to finalization.

"FORMAT"
Release title
v0.1.0 -

## Summary

## Features

## Contributors
@kevinkawchak
@claude

## Notes


"INSTRUCTIONS"
Problem statement Autonomous oncology trial robots and agents must interface with real systems: scheduling, eConsent, EDC/eSource repositories, imaging archives, lab systems. Point-to-point integrations do not scale. MCP is an emerging open protocol for connecting AI tools to external data and tools.
Technical scope Build a suite of open MCP servers and reference clients for:
* FHIR access patterns (read-only, scoped) for trial-relevant resources.
* DICOM query/retrieve proxies with strict permissions.
* Trial audit ledger and chain-of-custody APIs (Projects A/D).
* "Data provenance gateway" enforcing least privilege, logging all tool calls, and providing replayable audit traces.
Required datasets
* Public synthetic FHIR bundles; DICOM sample datasets; simulated scheduling data (real systems require partners; unspecified).
Algorithms/models
* Emphasis on authorization, policy enforcement, and semantic mapping; minimal ML.
Hardware/robotics integration
* Robot control agents can call MCP tools for "fetch task order," "upload certified evidence," "retrieve DICOM study pointer," etc.
Regulatory/compliance considerations
* Security is pivotal: recent reporting highlights vulnerabilities in agentic toolchains and MCP-related components, reinforcing the need for explicit authentication/authorization and safe defaults.
* Electronic records guidance: the system must preserve metadata and traceability when copying records.
Validation plan
* Security test suite: SSRF, injection, permission escalation, replay attacks.
* Audit completeness tests: every MCP call produces a signed audit record.
Milestones
* M1 (0–4 mo): "read-only clinical data" MCP servers + auth framework
* M2 (4–8 mo): DICOM/FHIR provenance gateway + replay logs
* M3 (8–12 mo): reference "trial robot agent" integration demo
Team roles and timeline 12 months: security engineer, backend engineer, clinical interoperability engineer, QA.
Potential collaborators Hospital IT; EHR integration teams; open interoperability communities.
Adoption pathway Start with "read-only" plus audit logging, then progress to controlled write operations for eSource uploads.
Open-source deliverables
* trialmcp-fhir, trialmcp-dicom, trialmcp-ledger
* trialmcp-authz (policy templates)
* Security playbook + reproducible hardening guides
