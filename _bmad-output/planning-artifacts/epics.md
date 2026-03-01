---
stepsCompleted:
  - step-01-validate-prerequisites
  - step-02-design-epics
  - step-03-create-stories
  - step-04-final-validation
inputDocuments:
  - /Users/clint/Documents/GitHub/test-bmad/_bmad-output/planning-artifacts/prd.md
  - /Users/clint/Documents/GitHub/test-bmad/_bmad-output/planning-artifacts/architecture.md
---

# test-bmad - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for test-bmad, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: Primary user can upload a photo from phone to start processing.
FR2: System can validate uploaded image quality before OCR processing.
FR3: System can reject invalid or unreadable images with actionable feedback.
FR4: System can retain upload metadata for diagnostics and history.
FR5: System can extract Chinese characters from uploaded images.
FR6: System can detect and ignore non-Chinese text when generating pinyin.
FR7: System can preserve extracted source text for user review.
FR8: System can indicate uncertain extraction segments to the user.
FR9: User can resubmit or retry processing when extraction quality is insufficient.
FR10: System can generate Hanyu Pinyin from extracted Chinese text.
FR11: System can return pinyin output aligned to extracted source text.
FR12: System can display uploaded image and generated pinyin in one result view.
FR13: System can return results as JSON for API consumers.
FR14: System can render HTML response for direct phone web usage.
FR15: System can provide clear processing status and completion outcome.
FR16: System can communicate processing failures with explicit reason categories.
FR17: System can provide fallback guidance when OCR confidence is low.
FR18: System can handle mixed Chinese/English page inputs without failing the whole request.
FR19: System can return partial results when full extraction is not possible.
FR20: System can allow user-initiated retry from the same interface flow.
FR21: User can view diagnostics in a collapsible section on the result page.
FR22: System can expose raw OCR output for troubleshooting.
FR23: System can expose confidence indicators for extracted text.
FR24: System can expose request timing details for each processing run.
FR25: System can expose LangChain/tool execution trace data for debugging.
FR26: System can emit usage and error telemetry suitable for optional Datadog integration.
FR27: System can provide service health status via API endpoint.
FR28: System can provide operational metrics via API endpoint.
FR29: System can estimate per-request processing cost.
FR30: System can track daily aggregate cost usage.
FR31: System can enforce or warn on a configurable daily budget threshold.
FR32: System can restrict oversized or potentially expensive inputs.
FR33: User can retrieve recent processing history.
FR34: User can retrieve a specific historical result by identifier.
FR35: System can store result artifacts required for later review.
FR36: System can support future extension to saved-book compilation workflows.
FR37: System can expose processing capabilities through versioned /v1 endpoints.
FR38: System can expose history capabilities through versioned /v1 endpoints.
FR39: System can operate in MVP without user authentication.
FR40: System can support future migration to Apple ID based authentication.

### NonFunctional Requirements

NFR1: End-to-end processing from upload acceptance to pinyin result should complete within 2 seconds for typical phone photos under normal operating conditions.
NFR2: The system should prioritize output correctness over response speed when tradeoffs occur.
NFR3: Health and metrics endpoints should respond quickly enough to support live troubleshooting.
NFR4: The processing pipeline should return a structured outcome for every request: success, partial success, or clear failure.
NFR5: The system should fail gracefully on low-quality images, OCR uncertainty, or provider/tool errors, with retry guidance.
NFR6: History and diagnostics data should be persisted reliably for recent sessions.
NFR7: All network traffic should use TLS in transit.
NFR8: Uploaded images and derived text artifacts should be stored with access controls appropriate for personal/private usage.
NFR9: Secrets should be managed outside source code (environment variables or secret store).
NFR10: The system should support future addition of Apple ID authentication without re-architecting core flows.
NFR11: The system should track per-request and daily estimated processing cost.
NFR12: The system should enforce or warn at a daily budget threshold of approximately 1 SGD/day.
NFR13: The system should apply request size and input constraints to prevent accidental high-cost usage.
NFR14: The system should expose request timings, OCR confidence indicators, and processing traces for debugging.
NFR15: The system should emit telemetry compatible with optional Datadog ingestion.
NFR16: Error events should include reason categories to support rapid root-cause identification.
NFR17: API contracts should be versioned under /v1 and remain backward compatible for non-breaking changes.
NFR18: The backend should provide JSON responses for API consumers and support rendered HTML flow for phone web usage.
NFR19: The design should preserve extensibility for future audio, translation, and personal book-compilation integrations.

### Additional Requirements

- Starter template requirement (prominent): initialize implementation with a minimal dual-starter setup using FastAPI backend plus Vite React frontend; this should be Epic 1 Story 1.
- Backend and frontend should be organized as a split architecture (`backend/` and `frontend/`) with a clean /v1 API boundary.
- API contracts should use standardized response envelopes (`success`, `partial`, `error`) with `request_id` and optional `job_id` for async-ready evolution.
- MVP public processing path should be synchronous (`POST /v1/process`) while preserving domain/service decoupling for future async queue execution.
- Enforce consistent API field naming (`snake_case`) and ISO 8601 UTC datetime formatting.
- Implement standardized error taxonomy/categories (`validation`, `ocr`, `pinyin`, `system`, `budget`, `upstream`) and avoid raw provider exception leakage.
- Implement middleware and patterns for request correlation (`request_id`) and structured client-safe error handling.
- Include operational endpoints (`GET /v1/health`, `GET /v1/metrics`) and diagnostics payload support for troubleshooting.
- Introduce repository/storage interfaces from day one (for history/artifacts) even though MVP persistence is no-database/ephemeral.
- Security baseline requirements include localhost-focused CORS allowlist, request size limits, MIME/type validation, environment-based secrets, and TLS when beyond localhost.
- Keep MVP unauthenticated but include an optional API-key middleware toggle path to ease future hardening.
- Frontend should use TanStack Query for API server-state and retry/cache behavior.
- Provide Docker Compose local runtime as baseline developer workflow for backend/frontend orchestration.
- Ensure architecture preserves extension path for AWS target (S3/CloudFront frontend, Lambda/API Gateway backend, future DynamoDB/S3 persistence) and Terraform IaC later.
- Enforce cross-agent consistency via naming conventions, API contracts, and contract tests/lint gates (Ruff + Black; ESLint + Prettier).

### FR Coverage Map

### FR Coverage Map

FR1: Epic 1 - Start flow with photo upload
FR2: Epic 1 - Validate image quality
FR3: Epic 1 - Reject invalid images with guidance
FR4: Epic 3 - Retain upload metadata for diagnostics/history
FR5: Epic 1 - OCR Chinese text extraction
FR6: Epic 1 - Ignore non-Chinese text in pinyin generation
FR7: Epic 2 - Preserve extracted source text
FR8: Epic 2 - Flag uncertain extraction segments
FR9: Epic 2 - Support resubmit/retry on low quality
FR10: Epic 1 - Generate Hanyu Pinyin
FR11: Epic 1 - Align pinyin with extracted text
FR12: Epic 1 - Show image and pinyin together
FR13: Epic 1 - Return JSON output
FR14: Epic 1 - Return phone-friendly HTML output
FR15: Epic 1 - Provide processing status/outcome
FR16: Epic 2 - Use explicit error reason categories
FR17: Epic 2 - Provide low-confidence fallback guidance
FR18: Epic 2 - Handle mixed-language pages gracefully
FR19: Epic 2 - Return partial results when needed
FR20: Epic 2 - Support user-initiated retry
FR21: Epic 3 - Collapsible diagnostics panel
FR22: Epic 3 - Expose raw OCR output
FR23: Epic 3 - Expose confidence indicators
FR24: Epic 3 - Expose request timing details
FR25: Epic 3 - Expose LangChain/tool execution trace
FR26: Epic 3 - Emit telemetry for optional Datadog
FR27: Epic 3 - Provide health endpoint
FR28: Epic 3 - Provide metrics endpoint
FR29: Epic 3 - Estimate per-request cost
FR30: Epic 3 - Track daily aggregate cost
FR31: Epic 3 - Enforce/warn daily budget threshold
FR32: Epic 3 - Restrict oversized/high-cost inputs
FR33: Epic 4 - Retrieve recent history
FR34: Epic 4 - Retrieve history item by id
FR35: Epic 4 - Store artifacts for later review
FR36: Epic 4 - Support future saved-book compilation
FR37: Epic 1 - Versioned /v1 processing APIs
FR38: Epic 4 - Versioned /v1 history APIs
FR39: Epic 1 - MVP no-auth operation
FR40: Epic 4 - Future Apple ID migration support

## Epic List

### Epic 1: Launch the Core Reading Assistant
User can upload a photo and get usable pinyin output in one phone-friendly flow (JSON + HTML), with versioned API baseline and MVP access model.
**FRs covered:** FR1, FR2, FR3, FR5, FR6, FR10, FR11, FR12, FR13, FR14, FR15, FR37, FR39

### Epic 2: Build Reliable Processing and Recovery
User gets dependable behavior on imperfect input through confidence-aware extraction, partial results, clear errors, and retry flow.
**FRs covered:** FR7, FR8, FR9, FR16, FR17, FR18, FR19, FR20

### Epic 3: Add Diagnostics, Observability, and Cost Guardrails
User can troubleshoot quality/performance issues and keep operational/cost control during daily use.
**FRs covered:** FR4, FR21, FR22, FR23, FR24, FR25, FR26, FR27, FR28, FR29, FR30, FR31, FR32

### Epic 4: Enable History and Future Evolution
User can retrieve prior sessions/results while the system preserves extension paths (saved-book workflows and future auth migration).
**FRs covered:** FR33, FR34, FR35, FR36, FR38, FR40

## Epic 1: Launch the Core Reading Assistant

Deliver a complete first-use experience where a user uploads a photo and receives pinyin output through stable `/v1` APIs and phone-friendly rendering.

### Story 1.1: Set up initial project from starter template

As a solo builder,
I want the project scaffolded with FastAPI backend and Vite React frontend,
So that implementation starts from a consistent architecture baseline.

**FRs:** FR37, FR39

**Acceptance Criteria:**

**Given** a new repository state
**When** the scaffold setup is executed
**Then** `backend/` and `frontend/` applications exist and run locally
**And** API routing supports a `/v1` prefix with no auth required in MVP.

**Given** the baseline architecture requirements
**When** project structure is reviewed
**Then** backend and frontend boundaries match the architecture document
**And** starter scaffolding supports future Docker Compose use.

### Story 1.2: Implement Upload Intake and Image Validation

As a user reading with my phone,
I want to upload a page image and receive immediate validation feedback,
So that only usable images proceed to OCR.

**FRs:** FR1, FR2, FR3

**Acceptance Criteria:**

**Given** a valid image upload
**When** I submit it to `POST /v1/process`
**Then** the request is accepted and image metadata is captured
**And** processing moves to extraction flow.

**Given** an unreadable or invalid file
**When** I submit it
**Then** the API returns a structured validation error
**And** the response includes actionable retry guidance.

### Story 1.3: Extract Chinese Text and Generate Pinyin

As a user,
I want Chinese text extracted and converted to Hanyu Pinyin,
So that I can continue reading correctly.

**FRs:** FR5, FR6, FR10, FR11

**Acceptance Criteria:**

**Given** a valid uploaded image containing Chinese text
**When** processing executes
**Then** OCR extracts Chinese characters
**And** non-Chinese text is excluded from pinyin conversion by default.

**Given** extracted Chinese text
**When** pinyin conversion runs
**Then** pinyin output is returned aligned with source text
**And** output is structured for downstream display.

### Story 1.4: Deliver JSON and HTML Result Views

As a user,
I want both API JSON output and a phone-friendly HTML result view,
So that I can use the same backend for direct reading and integrations.

**FRs:** FR12, FR13, FR14, FR15

**Acceptance Criteria:**

**Given** a successful processing request
**When** I call the API programmatically
**Then** I receive a JSON response with `status`, `request_id`, and `data`
**And** field naming follows `snake_case`.

**Given** a browser-based phone flow
**When** processing completes
**Then** the rendered page shows uploaded image and generated pinyin together
**And** completion status is clearly visible.

## Epic 2: Build Reliable Processing and Recovery

Deliver resilient behavior for imperfect real-world inputs through confidence signaling, partial results, categorized errors, and retry-friendly flow.

### Story 2.1: Preserve Source Text and Confidence Signals

As a user validating output quality,
I want to see extracted text with confidence indicators,
So that I can judge whether results are trustworthy.

**FRs:** FR7, FR8

**Acceptance Criteria:**

**Given** OCR extraction completes
**When** response payload is built
**Then** extracted source text is included in results
**And** uncertain segments are explicitly marked.

**Given** low-confidence extraction
**When** results are returned
**Then** the user sees warning-level confidence messaging
**And** guidance is provided for retaking the photo.

### Story 2.2: Implement Structured Failure Taxonomy

As a user troubleshooting failures,
I want explicit, categorized errors,
So that I can take the right recovery action quickly.

**FRs:** FR16, FR17

**Acceptance Criteria:**

**Given** a processing failure
**When** the API responds
**Then** error payload includes standardized category and code
**And** provider-internal exception details are not leaked.

**Given** different failure classes (`validation`, `ocr`, `pinyin`, `budget`, `upstream`, `system`)
**When** each is triggered
**Then** the response message is actionable and consistent
**And** status envelope shape remains stable.

### Story 2.3: Support Partial Results for Mixed/Uncertain Pages

As a user with complex book pages,
I want partial output instead of complete failure,
So that I can still continue reading with best available data.

**FRs:** FR18, FR19

**Acceptance Criteria:**

**Given** mixed-language or partially recognized input
**When** full extraction is not possible
**Then** response status is `partial`
**And** successfully extracted text and pinyin are still returned.

**Given** partial completion
**When** output is displayed
**Then** limitations are clearly explained
**And** user receives recommended next steps.

### Story 2.4: Add User-Initiated Retry Path

As a user,
I want a direct retry path from the same flow,
So that I can quickly resubmit improved images.

**FRs:** FR9, FR20

**Acceptance Criteria:**

**Given** a failed or low-confidence result
**When** I choose retry
**Then** I can resubmit from the same interface
**And** a new processing request is started cleanly.

**Given** repeated retries
**When** each request completes
**Then** each run has its own request identifier
**And** results are isolated per attempt.

## Epic 3: Add Diagnostics, Observability, and Cost Guardrails

Provide transparent diagnostics and operational controls so quality, performance, and spend remain visible and manageable.

### Story 3.1: Expose Diagnostics Panel and Raw OCR Data

As a user debugging quality issues,
I want a collapsible diagnostics panel with raw OCR output,
So that I can identify whether failures come from extraction or conversion.

**FRs:** FR21, FR22, FR23

**Acceptance Criteria:**

**Given** any processed request
**When** I open diagnostics
**Then** raw OCR text is visible
**And** confidence indicators are included.

**Given** normal usage view
**When** diagnostics are not needed
**Then** diagnostics remain collapsed by default
**And** primary reading result stays uncluttered.

### Story 3.2: Add Timing and Trace Diagnostics

As a user learning LangChain orchestration,
I want request timing and tool-trace details,
So that I can understand performance and pipeline behavior.

**FRs:** FR24, FR25

**Acceptance Criteria:**

**Given** a processed request
**When** diagnostics are returned
**Then** total and stage-level timings are available
**And** trace metadata is associated with `request_id`.

**Given** a troubleshooting scenario
**When** diagnostics are reviewed
**Then** execution path details are sufficient to isolate bottlenecks
**And** trace output is structured for future telemetry ingestion.

### Story 3.3: Implement Health, Metrics, and Telemetry Hooks

As an operator of the app,
I want health and metrics endpoints with telemetry emissions,
So that system behavior is observable and monitorable.

**FRs:** FR26, FR27, FR28

**Acceptance Criteria:**

**Given** service is running
**When** `GET /v1/health` is called
**Then** it returns service readiness status
**And** response remains lightweight for quick checks.

**Given** operational monitoring
**When** `GET /v1/metrics` is called
**Then** usage/error/performance metrics are returned
**And** emitted telemetry is compatible with optional Datadog integration.

### Story 3.4: Add Budget Guardrails and Input Cost Protection

As a cost-conscious user,
I want per-request and daily budget guardrails,
So that prototype usage stays within the target spend.

**FRs:** FR4, FR29, FR30, FR31, FR32

**Acceptance Criteria:**

**Given** each processing request
**When** execution completes
**Then** estimated per-request cost is calculated
**And** daily aggregate usage is updated.

**Given** daily usage reaches configured threshold
**When** a new request arrives
**Then** system warns or blocks per policy
**And** response clearly explains budget state.

**Given** oversized or risky input files
**When** they are submitted
**Then** request is constrained or rejected before expensive processing
**And** the user receives corrective guidance.

## Epic 4: Enable History and Future Evolution

Introduce history retrieval and architecture seams that support later saved-book and authentication evolution without rework.

### Story 4.1: Store and Retrieve Recent Processing History

As a user,
I want to view recent processed sessions,
So that I can revisit prior results during reading.

**FRs:** FR33, FR35

**Acceptance Criteria:**

**Given** completed processing runs
**When** I call `GET /v1/history`
**Then** recent entries are returned in a stable response envelope
**And** each entry includes identifiers and summary metadata.

**Given** MVP storage constraints
**When** history is implemented
**Then** repository interfaces abstract persistence
**And** current implementation can remain ephemeral/in-memory.

### Story 4.2: Retrieve Detailed History Records by ID

As a user,
I want to fetch a specific prior result,
So that I can inspect exact output and diagnostics from earlier runs.

**FRs:** FR34, FR38

**Acceptance Criteria:**

**Given** a valid history identifier
**When** I call `GET /v1/history/{id}`
**Then** detailed record data is returned
**And** includes required artifacts for later review.

**Given** an unknown identifier
**When** lookup is attempted
**Then** API returns a structured not-found error
**And** error format matches shared taxonomy.

### Story 4.3: Preserve Future Extension Contracts

As the system owner,
I want stable contracts for future saved-book workflows and auth migration,
So that post-MVP features can be added without breaking existing flows.

**FRs:** FR36, FR40

**Acceptance Criteria:**

**Given** current `/v1` API contracts
**When** extension seams are reviewed
**Then** history and processing models include fields/interfaces needed for saved-book evolution
**And** no breaking change is required for near-term expansion.

**Given** future Apple ID authentication plans
**When** architecture is implemented
**Then** MVP remains unauthenticated
**And** integration path for later auth is explicitly preserved in boundaries/config.
