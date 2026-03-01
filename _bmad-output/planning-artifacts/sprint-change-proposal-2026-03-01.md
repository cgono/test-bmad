# Sprint Change Proposal

Date: 2026-03-01
Project: test-bmad
Mode: Incremental

## 1) Issue Summary

A readiness review identified planning-quality gaps that should be corrected before implementation scales:
- Missing early CI/CD quality-gate story in early epic sequence for a greenfield setup.
- Several acceptance criteria are not measurably bounded (use terms like "structured"/"consistent" without schema-level checks).
- Cross-epic dependency assumptions are implicit rather than explicitly documented.

Trigger context:
- Source artifact: `_bmad-output/planning-artifacts/implementation-readiness-report-2026-03-01.md`
- Discovery point: pre-implementation readiness assessment

## 2) Impact Analysis

### Epic Impact
- **Epic 1**: Requires scope adjustment to add a baseline CI quality-gate story early in sequence.
- **Epics 2-5**: No scope redefinition required, but dependency notes must be explicit.

### Story Impact
- Existing Epic 1 story numbering shifts due to inserted CI story.
- Selected stories in Epic 1 and Epic 2 require measurable acceptance-criteria refinements.

### Artifact Conflicts
- **epics.md**: Primary artifact requiring updates (new story, dependency notes, measurable AC language).
- **architecture.md**: No mandatory structural rewrite, but the CI quality-gate intent now becomes explicitly represented in epic/stories.
- **ux-design-specification.md**: No mandatory rewrite in this change set; measurable AC updates reduce interpretation drift against UX intent.

### Technical Impact
- Introduces early CI requirement coverage (backend lint/tests, frontend lint/tests, API envelope contract checks).
- Reduces risk of regression and cross-agent inconsistency by enforcing contract shape early.
- No rollback or MVP scope reduction needed.

## 3) Recommended Approach

Selected path: **Direct Adjustment (Option 1)**

Rationale:
- Resolves all identified issues with targeted artifact edits.
- Preserves MVP scope, epic order, and timeline assumptions.
- Lowest-risk correction with high readiness gain.

Effort estimate: **Low-Medium**
Risk assessment: **Low**
Timeline impact: **Minimal** (planning artifact updates before implementation expansion)

## 4) Detailed Change Proposals

### A) Stories (Epic 1)

#### A.1 Add missing early CI/CD quality-gate story and resequence Epic 1 stories

**Artifact:** `_bmad-output/planning-artifacts/epics.md`

**OLD**
- Story 1.1: Set Up Initial Project from Starter Template
- Story 1.2: Validate Uploaded Images and Return Actionable Errors
- Story 1.3: Extract Chinese Text from Valid Images
- Story 1.4: Generate Pinyin and Return Unified Result View

**NEW**
- Story 1.1: Set Up Initial Project from Starter Template
- Story 1.2: Establish Baseline CI Quality Gates (Backend + Frontend + Contract)
- Story 1.3: Validate Uploaded Images and Return Actionable Errors
- Story 1.4: Extract Chinese Text from Valid Images
- Story 1.5: Generate Pinyin and Return Unified Result View

**New Story 1.2 Acceptance Criteria**
- CI runs on pull requests and main updates.
- Backend checks execute (Ruff + backend tests).
- Frontend checks execute (ESLint + frontend tests).
- Contract checks validate `/v1/process` envelope required fields (`status`, `request_id`, and `data|warnings|error` as applicable).
- CI fails and blocks merge when quality gates fail.

**Rationale**
Adds the missing greenfield quality gate at the earliest practical point and enforces implementation consistency.

### B) Epic Overview Metadata

#### B.1 Add explicit `Depends on` notes for each epic

**Artifact:** `_bmad-output/planning-artifacts/epics.md`

**OLD**
- Epic overviews contain title, description, and FR coverage only.

**NEW**
- Epic 1: `Depends on: None (foundational epic)`
- Epic 2: `Depends on: Epic 1 (starter stack, /v1/process baseline, CI quality gates)`
- Epic 3: `Depends on: Epic 1 (request flow foundation), Epic 2 (quality/recovery signal sources)`
- Epic 4: `Depends on: Epic 1 (processing path and validation hooks), Epic 3 (metrics/telemetry foundations)`
- Epic 5: `Depends on: Epic 1 (core request/response and IDs), Epic 3 (diagnostics payload conventions)`

**Rationale**
Makes sequencing assumptions explicit and reduces planning ambiguity.

### C) Acceptance Criteria Precision

#### C.1 Tighten schema-level measurability in selected stories

**Artifact:** `_bmad-output/planning-artifacts/epics.md`

**Story 1.3 (old -> new)**
- OLD: "extracted Chinese text is produced in structured output"
- NEW: extracted text returned in `data.ocr.segments[]` with fields `text`, `language`, `confidence`; `status` must be one of `success|partial|error` in API response and reflected in UI state.

**Story 2.2 (old -> new)**
- OLD: "alignment data is represented consistently"
- NEW: return `data.pinyin.segments[]` with `source_text`, `pinyin_text`, `alignment_status`; uncertain alignment requires `alignment_status="uncertain"` and `reason_code`.

**Story 2.3 (old -> new)**
- OLD: "status is partial with usable output; failure category/code indicates what failed"
- NEW: use `status="partial"` when at least one stage succeeds and one fails; `error.category` and `error.code` must be populated from shared taxonomy.

**Rationale**
Converts subjective wording into contract-testable acceptance conditions.

## 5) Implementation Handoff

### Scope Classification
**Moderate**: backlog/story reorganization and explicit planning artifact edits are required before broad implementation.

### Handoff Recipients and Responsibilities
- **Product Owner / Scrum Master**
  - Update `epics.md` with approved story additions/resequencing, dependency notes, and AC refinements.
  - Reflect updated story order and dependencies in sprint planning.
- **Development Team**
  - Implement Story 1.2 quality gates before expanding feature stories.
  - Maintain contract schema consistency in subsequent implementation.
- **QA**
  - Validate CI gates execute and fail correctly on lint/test/contract violations.
  - Confirm AC measurability via contract-level checks.

### Success Criteria for Implementation
- Epic 1 contains explicit CI quality-gate story and updated numbering.
- Every epic has explicit `Depends on` notes.
- Updated stories include schema-level measurable acceptance criteria.
- CI pipeline validates lint/tests/contract envelope checks before merge.

## Approval and Handoff Log

- 2026-03-01: User approval received for implementation (`yes`).
- Scope classification confirmed: `Moderate`.
- Routed to: Product Owner / Scrum Master for backlog reorganization and artifact updates; Development Team for implementation execution; QA for quality-gate verification.
