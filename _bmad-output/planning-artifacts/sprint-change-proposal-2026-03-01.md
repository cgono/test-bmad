# Sprint Change Proposal

Date: 2026-03-01
Project: test-bmad
Workflow: Correct Course (`bmad-bmm-correct-course`)
Mode: Incremental

## 1) Issue Summary

Implementation readiness validation identified one major issue and two minor issues that reduce execution quality if left unresolved:

- Major: missing explicit CI/CD quality-gate story.
- Minor: telemetry minimum fields are not explicit in Story 3.3.
- Minor: optional `job_id` is not explicit in Story 1.4 response contract language.

Context: These findings came from the readiness report generated on 2026-03-01 and were confirmed by user review.

Evidence:
- `_bmad-output/planning-artifacts/implementation-readiness-report-2026-03-01.md`

## 2) Impact Analysis

### Epic Impact

- Epic 1 is affected: add a CI quality-gate story early in sequence.
- Epic 3 is affected: Story 3.3 acceptance criteria need explicit telemetry field requirements.
- No new epic required; no epic removal required.

### Story Impact

- Add Story 1.2: Establish CI Quality Gates.
- Renumber existing Epic 1 stories:
  - Old 1.2 -> 1.3
  - Old 1.3 -> 1.4
  - Old 1.4 -> 1.5
- Update Story 3.3 AC to define minimum telemetry payload fields.
- Update Story 1.5 (renumbered from old 1.4) AC to include optional `job_id` contract behavior.

### Artifact Conflicts

- PRD: no conflict; changes reinforce existing NFR intent.
- Architecture: aligns with existing guidance on contract tests and consistent response envelope.
- UX: intentionally excluded for this correction pass per user instruction.

### Technical Impact

- Adds CI pipeline work (lint/format/contract checks).
- Tightens API contract and observability acceptance criteria.
- Low-to-moderate implementation effort; low risk; positive quality and regression impact.

## 3) Recommended Approach

Selected path: **Direct Adjustment** (Option 1)

Rationale:
- Resolves all three validated issues with minimal disruption.
- Preserves MVP scope and momentum.
- Avoids unnecessary rollback or PRD scope change.

Effort estimate: Low-Medium
Risk estimate: Low
Timeline impact: Small near-term increase; reduces downstream rework and debugging risk.

## 4) Detailed Change Proposals

### A) Stories

#### Change A1: Add CI story in Epic 1 (Major)

Story: Epic 1 (new insertion)
Section: Stories / Acceptance Criteria

OLD:
- Epic 1 has stories 1.1-1.4 only.
- No explicit CI quality-gate story.

NEW:
- Add **Story 1.2: Establish CI Quality Gates**.
- Renumber downstream Epic 1 stories by +1.

Proposed Story 1.2 text:

- As a solo builder,
- I want automated CI checks for backend and frontend quality,
- So that regressions and contract drift are detected early before feature expansion.

FR/NFR alignment: NFR4, NFR14, NFR17

Acceptance Criteria:
- Given a pull request or main-branch push
  When CI runs
  Then backend lint/format checks execute (`ruff`, `black --check`)
  And frontend lint/format checks execute (`eslint`, `prettier --check`).
- Given backend API response envelope contracts
  When CI runs
  Then contract tests validate success/partial/error envelope shape
  And required fields include `status`, `request_id`, and payload-specific sections.
- Given failing quality checks
  When CI evaluates the run
  Then the pipeline fails clearly with actionable job output
  And merge is blocked until checks pass.
- Given local developer workflow
  When quality commands are run locally
  Then commands mirror CI and are documented.

#### Change A2: Story 3.3 telemetry AC specificity (Minor)

Story: 3.3 Implement Health, Metrics, and Telemetry Hooks
Section: Acceptance Criteria

OLD:
- "emitted telemetry is compatible with optional Datadog integration."

NEW (addition):
- Given any processing lifecycle event (success/partial/error)
  When telemetry is emitted
  Then each event includes at minimum:
  - `request_id`
  - `event_category` (`validation` | `ocr` | `pinyin` | `budget` | `upstream` | `system`)
  - `status` (`success` | `partial` | `error`)
  - `latency_ms_total`
  - `latency_ms_by_stage` (when available)
  - `cost_estimate`
  - `timestamp_utc` (ISO 8601 UTC)
  And fields are emitted in Datadog-compatible structured format.

#### Change A3: Story 1.5 response envelope continuity (Minor)

Story: 1.5 Deliver JSON and HTML Result Views (renumbered from old 1.4)
Section: Acceptance Criteria

OLD:
- JSON response includes `status`, `request_id`, and `data`.

NEW:
- JSON response includes `status`, `request_id`, `data`, and optional `job_id` (nullable/omitted in synchronous MVP flow).
- When synchronous processing is used, `job_id` is absent or null, preserving forward compatibility for async evolution.

### B) PRD

- No direct PRD text change required.
- Optional editorial improvement: add one line in implementation readiness/quality section noting CI quality gate as MVP implementation prerequisite.

### C) Architecture

- No structural change required.
- Optional traceability update: reference new Story 1.2 in architecture-to-story mapping and quality enforcement checklist.

### D) UI/UX

- No changes in this pass by explicit user direction.

## 5) Implementation Handoff

Scope classification: **Moderate**

Reason:
- Story additions/renumbering and acceptance criteria updates require backlog maintenance and development execution coordination, but do not require full strategic replanning.

Handoff recipients and responsibilities:
- Scrum Master / Product Owner:
  - Update epic/story artifact ordering and IDs in `epics.md`.
  - Ensure sequencing places CI story before feature-heavy stories.
- Development Agent:
  - Implement CI checks and contract tests per updated story AC.
  - Preserve response-envelope compatibility and telemetry field schema.
- Architect (advisory):
  - Validate contract and telemetry updates stay aligned with architecture standards.

Success criteria:
- Epic 1 includes approved Story 1.2 and correct renumbering.
- Story 3.3 includes explicit telemetry minimum fields.
- Story 1.5 includes optional `job_id` contract statement.
- CI pipeline fails on lint/format/contract-test violations.

---

Approval status: Pending user approval
