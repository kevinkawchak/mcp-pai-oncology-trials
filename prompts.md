# Build Prompts

## Research Papers Prompt (v0.3.0)

Your goal based on kevinkawchak/mcp-pai-oncology-trials is to write 3 10 page total papers from three different paper perspectives below (A) - C)). Each paper should be unique, based on the repository, and have a title that begins with "TrialMCP: MCP Servers for Physical AI Oncology Clinical Trial Systems - " and appends either A) "Clinical Operations" B) "Regulatory" or C) "Interoperability". All 3 papers will be under DOI 10.5281/zenodo.18870961 (https://doi.org/10.5281/zenodo.18870961) Include author Kevin Kawchak, CEO ChemicalQDevice, https://orcid.org/0009-0007-5457-8667, kevink@chemicalqdevice.com, today's date, and appropriate keywords. Don't use images in any of the papers; instead adapt new flowcharts, processes, structures, etc. from text and mermaid diagrams from the repository. Use the maximum 1M context length for processing; do not abbreviate inference time or inference-time compute.

Don't use the term "TrialMCP Pack" throughout each paper. Do not include "a pre-print" in the papers. Each of the papers must be comprehensive, and use information from the repository based on their respective perspectives that will yield new, state-of-the-art, and applicable MCP physical AI oncology trial papers.

Each perspective must have the following Paper Sections:
- Abstract
- Table of Contents
- Introduction
- Methods
- Results
- Discussion
- Limitations and Future Work
- Conclusion
- References
- Acknowledgments (see below)
- Ethical disclosures (see below)
- Rights and permissions (see below)
- Cite this article (see below)

"PAPER PERSPECTIVES"
A) Clinical Operations & Trial Sponsors Perspective
Audience: sponsors, CRO leadership, trial ops directors, site networks
Core story: "Make multi-site trial operations robot/agent-ready without brittle point-to-point integrations."
Emphasize: workflow sequence (token -> study status -> imaging pointer -> evidence logging -> provenance), scheduling/eConsent/EDC adjacency, adoption pathway/milestones, operational scalability.
De-emphasize: protocol internals and deep crypto details.
Re-order content: start with "why point-to-point doesn't scale" -> end-to-end workflow -> deployment topology -> roadmap.
Success criteria language: cycle time reduction, audit readiness, fewer integration projects, faster site onboarding.

B) Regulatory, Quality, and Compliance Perspective
Audience: QA/CSV teams, auditors, compliance officers, regulated engineering orgs
Core story: "A compliance-first interoperability layer: deny-by-default access, de-ID, tamper-evident audit, replayable traces."
Emphasize: 21 CFR Part 11 audit chain, ICH-GCP traceability, HIPAA Safe Harbor de-identification, permission matrix by role, replay and verification, error taxonomy, test evidence (security/audit/integration tests).
De-emphasize: robotics platform comparisons unless directly tied to validation scope.
Re-order content: compliance claims -> controls mapping -> verification approach/tests -> operational procedures -> limitations/assumptions.
Success criteria language: inspection readiness, trace completeness, least privilege, tamper evidence, defensible validation package.

C) Healthcare Interoperability & Standards Perspective (FHIR/DICOM/MCP)
Audience: health IT architects, interoperability engineers, standards contributors (HL7/IHE/DICOM), EHR/PACS teams
Core story: "MCP as the agent-tool interface that cleanly composes with FHIR + DICOM in federated, multi-site clinical environments."
Emphasize: tool surface area per server, read-only FHIR pattern + de-ID, DICOM query/retrieve gating, provenance gateway concept, role-scoped capabilities, integration patterns with HAPI/Orthanc/dcm4chee (as implementation pathways).
De-emphasize: robot brand names; focus on actors/transactions.
Re-order content: capability model -> server/tool definitions -> security gates -> deployment topology -> conformance considerations.
Success criteria language: reduced integration complexity, clean boundaries, predictable interfaces, audit hooks everywhere.

You are responsible for the full codebase and set of releases, changelog.md, prompts.md, readmes, documentation, etc. Incorporate release IDs (v0.0.0 format) where appropriate in text, tables, text diagrams, etc. Be sure to implement quantitative data and code snippets where appropriate. It is imperative that all types of information utilized from across the repository be accurate and appropriate to each section of the paper.

Make sure every section is properly formatted and seems attractive to read (bullet points and numbered lists where appropriate and other types of formatting to avoid many long paragraphs). For references: use the three references at the bottom of the main kevinkawchak/mcp-pai-oncology-trials Readme; and exact working URLs where necessary from kevinkawchak/physical-ai-oncology-trials. After finishing each of the papers, make sure end-to-end that all aesthetics regarding the title, white spacing, text diagrams, tables, etc. are appropriate.

In a new /papers directory on main, create a new readme and three subdirectories "ClinOps", "Regulatory", and "Interoperability" based on their respective perspectives. Each subdirectory should contain their respective 10 page pdf and a "LaTeX Source Files" zip file containing distinguishable file names based on their perspectives for (.tex, .bib, .sty, and README). Also provide a pdf in /papers that combines all three papers into one pdf in the order A), B), C) with no changes to any of the papers and no blank pages between them (do not re-number any of the pages): new pdf page format should be 1-10, 1-10, 1-10 .

Provide a copy of this prompt under the related prompts.md. Be sure to fix and address errors that would cause failed checks for the single pull request (such as Python environment issues to avoid the following error during final checks): "3 failing checks
x Cl / lint-and-format (3.10) (pull...
x Cl / lint-and-format (3.11) (pull...
x Cl / lint-and-format (3.12) (pull... " Place the new release notes in releases.md under main using the format below. Update changelog using v0.3.0. When you are finished, auto-push the update to GitHub on your own for my review. The user will then review your updates in GitHub prior to finalization.

"FORMAT"
Release title
v0.3.0 -

## Summary

## Features

## Contributors
@kevinkawchak
@claude
@openai

## Notes

(Below: Not part of release notes)
Acknowledgments
The author would like to acknowledge Anthropic for providing access to Claude Code Opus 4.6 for repository and paper generations; and OpenAI for providing access to GPT-5.2-Codex for peer-review recommendations, with ChatGPT 5.2 Thinking for project formulation and paper perspectives assistance.

Ethical disclosures
The author of the article declares no competing interests.

Rights and permissions
This article is distributed under the terms of the Creative Commons Attribution 4.0 International License (CC BY 4.0), which permits unrestricted use, distribution, and reproduction in any medium, provided the original author(s) and source are properly credited, a link to the Creative Commons license is provided, and any modifications made are indicated. To view a copy of this license, visit https://creativecommons.org/licenses/by/4.0/.

Cite this article
Kawchak K. TrialMCP: MCP Servers for Physical AI Oncology Clinical Trial Systems. Zenodo. 2026; 10.5281/zenodo.18870961.

---

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

---

## ChatGPT Perspectives Prompt 

Instead, based on the repo, provide 5 different perspectives Claude code could take to publish the paper to different audiences. 

---

## ChatGPT Paper Topic Prompt 

Based on the following LinkedIn profile: provide a Top 10 detailed list regarding what Claude Code GitHub projects should be pursued that would bring physical AI oncology clinical trials closer to reality. Each of your recommendations of course should be novel, awesome, and make the new industry real to the pharmaceutical industry, regulatory, and AI communities in using autonomous robots at scale in oncology clinical trials. https://www.linkedin.com/in/kevin-kawchak-38b52a4a
