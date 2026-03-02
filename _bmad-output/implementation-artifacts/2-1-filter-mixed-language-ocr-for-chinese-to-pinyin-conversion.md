# Story 2.1: Filter Mixed-Language OCR for Chinese-to-Pinyin Conversion

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As Clint,
I want non-Chinese OCR content filtered before pinyin conversion,
so that generated pronunciation output focuses on relevant Chinese text.

## Acceptance Criteria

1. Given OCR output contains Chinese and non-Chinese segments, when conversion preprocessing runs, then non-Chinese segments are excluded from pinyin generation and retained source text remains available for review.
2. Given OCR output is primarily non-Chinese, when filtering completes, then the system returns a structured recoverable response and guidance indicates how to retake for better Chinese capture.

## Tasks / Subtasks

- [ ] Implement explicit mixed-language filtering flow while preserving reviewable OCR source data (AC: 1, 2)
  - [ ] Refactor `backend/app/services/ocr_service.py` so filtering produces two clearly-defined sets:
    - [ ] `source_segments`: normalized OCR segments intended for review/debug display.
    - [ ] `chinese_segments`: subset eligible for pinyin generation.
  - [ ] Keep current CJK/language heuristics as the baseline (`CJK range` or `language` starts with `zh`) and centralize the check in one helper to avoid drift.
  - [ ] Ensure non-Chinese segments are never sent to `generate_pinyin`.
- [ ] Return structured recoverable behavior when Chinese content is absent/insufficient (AC: 2)
  - [ ] Update `backend/app/api/v1/process.py` to return a recoverable non-fatal path (`status="partial"`) for non-Chinese-dominant OCR outcomes.
  - [ ] Include actionable warning guidance for retake (`warnings[]`) while still returning available OCR context in `data`.
  - [ ] Keep typed category/code conventions stable and `snake_case` payloads unchanged.
- [ ] Preserve and extend schema contract without breaking existing consumers (AC: 1, 2)
  - [ ] Update `backend/app/schemas/process.py` to carry retained reviewable OCR content in a backward-compatible way.
  - [ ] Keep existing envelope invariants (`success|partial|error`) and `request_id` semantics.
- [ ] Surface recoverable guidance in the mobile UI (AC: 2)
  - [ ] Update `frontend/src/features/process/components/UploadForm.jsx` to render warning/recovery guidance for partial responses.
  - [ ] Ensure the primary recovery action remains obvious (`Take Photo` / retry flow) and does not regress current success/error behaviors.
- [ ] Add/adjust tests to lock in mixed-language behavior and prevent regressions (AC: 1, 2)
  - [ ] Extend `backend/tests/unit/services/test_ocr_service.py` for mixed-language classification and filtering behavior.
  - [ ] Extend `backend/tests/integration/api_v1/test_process_route.py` for partial recoverable response on non-Chinese-dominant input.
  - [ ] Extend `backend/tests/contract/response_envelopes/test_process_envelopes.py` for partial envelope expectations in this scenario.
  - [ ] Extend `frontend/src/__tests__/features/process/upload-form.test.jsx` for partial warning/recovery rendering.

## Dev Notes

### Story Foundation

- Source story: Epic 2, Story 2.1 in `_bmad-output/planning-artifacts/epics.md`.
- Epic intent: increase OCR-to-pinyin reliability and user trust for mixed-language pages without hard-failing useful requests.
- Scope boundary: this story focuses on filtering and recoverable behavior for mixed/non-Chinese OCR outcomes; alignment improvements belong to Story 2.2.

### Developer Context Section

Current baseline behavior in code:
- `backend/app/services/ocr_service.py` already normalizes OCR segments and filters for Chinese-usable content.
- `backend/app/api/v1/process.py` currently returns `error` when no usable Chinese segment remains after filtering.
- `frontend/src/features/process/components/UploadForm.jsx` shows error guidance for `status=error`, but has no explicit UI path for recoverable `partial` warnings in mixed-language scenarios.

Implementation goal for this story:
- Preserve strict typed contracts.
- Exclude non-Chinese content from pinyin generation.
- Keep source OCR context reviewable.
- Convert non-Chinese-dominant cases into structured recoverable responses with clear retake guidance.

### Technical Requirements

- Maintain `/v1/process` envelope contract stability:
  - `status` must remain one of `success|partial|error`.
  - `partial` responses must include both `data` and `warnings`.
- Keep `request_id` generation and pass-through unchanged.
- Keep error/warning payloads actionable and machine-readable (`code`, `message`, typed category if applicable).
- Do not route non-Chinese OCR segments into pinyin conversion path.
- Preserve Chinese segments for reading flow and preserve source OCR context for review.

### Architecture Compliance

Follow architecture constraints from `_bmad-output/planning-artifacts/architecture.md`:
- Keep API contracts under `/v1` and `snake_case` fields.
- Keep route thin in `backend/app/api/v1/process.py`; place filtering logic in service layer.
- Preserve error taxonomy discipline (`validation`, `ocr`, `pinyin`, etc.) and avoid ad hoc shapes.
- Maintain frontend progressive disclosure model where details are secondary to the primary reading flow.

### Library / Framework Requirements

Current repository pins (must be respected unless explicitly required):
- Backend: `fastapi==0.129.0`, `pydantic==2.11.9`, `langchain-core==0.3.61`, `pypinyin==0.55.0`.
- Frontend: `react==19.1.1`, `@tanstack/react-query==5.87.1`, `vite==7.1.4`.

Implementation guidance:
- This story should be delivered without dependency upgrades unless a blocking issue is discovered.
- Prefer internal logic/schema updates and test coverage over stack churn.

### File Structure Requirements

Primary files expected to change:
- `backend/app/services/ocr_service.py`
- `backend/app/api/v1/process.py`
- `backend/app/schemas/process.py`
- `frontend/src/features/process/components/UploadForm.jsx`

Likely test files to update:
- `backend/tests/unit/services/test_ocr_service.py`
- `backend/tests/integration/api_v1/test_process_route.py`
- `backend/tests/contract/response_envelopes/test_process_envelopes.py`
- `frontend/src/__tests__/features/process/upload-form.test.jsx`

### Testing Requirements

Backend unit:
- Validate mixed-language input keeps source OCR context and isolates Chinese-eligible segments.
- Validate non-Chinese-only path returns recoverable structured behavior as designed.

Backend integration/contract:
- Verify `/v1/process` returns valid `partial` envelope for non-Chinese-dominant OCR outcomes.
- Verify existing success and error envelope behavior remains unchanged.

Frontend tests:
- Verify partial warnings are visible and actionable.
- Verify no regression in success rendering (pinyin + image) and known error guidance paths.

### Latest Tech Information

Latest checks relevant to this story (verified 2026-03-02):
- FastAPI 0.129.0 release information confirms current pin is recent and stable for this story scope.
- `langchain-core` latest release is 1.0.1 while repository currently pins 0.3.61.
- `pypinyin` latest release is 0.55.0 (matches current pin).
- `@tanstack/react-query` latest npm release is 5.90.2; repository currently uses 5.87.1.

Guidance from these checks:
- No mandatory upgrade is required to implement Story 2.1.
- Avoid major LangChain version migration in this story; keep mixed-language filtering scope-focused.

### Project Context Reference

- `project-context.md` not found in repository.
- Primary context sources used:
  - `_bmad-output/planning-artifacts/epics.md`
  - `_bmad-output/planning-artifacts/architecture.md`
  - `_bmad-output/planning-artifacts/prd.md`
  - `_bmad-output/planning-artifacts/ux-design-specification.md`
  - `_bmad-output/implementation-artifacts/1-6-refactor-ocr-provider-to-langchain-graph-orchestrated-flow.md`

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-2.1-Filter-Mixed-Language-OCR-for-Chinese-to-Pinyin-Conversion]
- [Source: _bmad-output/planning-artifacts/architecture.md#Implementation-Patterns--Consistency-Rules]
- [Source: _bmad-output/planning-artifacts/architecture.md#Project-Structure--Boundaries]
- [Source: _bmad-output/planning-artifacts/prd.md#Text-Extraction--Language-Handling]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Core-User-Experience]
- [Source: backend/app/services/ocr_service.py]
- [Source: backend/app/api/v1/process.py]
- [Source: backend/app/schemas/process.py]
- [Source: frontend/src/features/process/components/UploadForm.jsx]
- [Source: backend/tests/unit/services/test_ocr_service.py]
- [Source: backend/tests/integration/api_v1/test_process_route.py]
- [Source: backend/tests/contract/response_envelopes/test_process_envelopes.py]
- [Source: https://fastapi.tiangolo.com/release-notes/]
- [Source: https://pypi.org/project/langchain-core/]
- [Source: https://pypi.org/project/pypinyin/]
- [Source: https://www.npmjs.com/package/@tanstack/react-query]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Workflow: `_bmad/bmm/workflows/4-implementation/create-story`

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Story assembled with mixed-language filtering guardrails, recoverable response expectations, and explicit test targets.

### File List

- `_bmad-output/implementation-artifacts/2-1-filter-mixed-language-ocr-for-chinese-to-pinyin-conversion.md` (created)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (updated: story state set to `ready-for-dev`)
