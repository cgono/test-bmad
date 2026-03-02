# Sprint Change Proposal

## 1. Issue Summary

### Trigger
After creating Story 1.6, a remaining alignment gap was identified: the planned LangChain graph refactor does not yet explicitly require OCR to be modeled as a graph tool and does not explicitly require an LLM graph node call.

### Problem Statement
The current story/doc set partially addresses the learning goal (explicit graph), but still misses the stronger requirement for a full graph pattern: OCR as a tool boundary plus an LLM node invocation. This limits learning value around practical tool-calling orchestration.

### Evidence
- User clarification on 2026-03-02: "I need the LangChain graph to implement OCR functionality as a tool, and the graph should call an LLM like gpt-5-mini."
- Current Story 1.6 text (pre-update) required graph nodes/edges but did not explicitly require OCR-as-tool and `gpt-5-mini` invocation.

## 2. Impact Analysis

### Epic Impact
- Affected epic: **Epic 1: Foundation & Capture-to-Result Vertical Slice**
- Impact type: story-scope refinement (no epic replan)
- Outcome: Epic 1 remains valid and in-progress; Story 1.6 scope is strengthened.

### Story Impact
- Primary impacted story: **Story 1.6** (requirements strengthened, still ready-for-dev)
- Secondary impacts: none on other story IDs; no renumbering required.

### Artifact Conflicts
- PRD: no conflict; update increases alignment with LangChain learning objective.
- Architecture: needed clearer integration wording for tool + LLM node expectations.
- UX: no direct changes.
- Artifacts requiring edits:
  - `_bmad-output/planning-artifacts/epics.md`
  - `_bmad-output/planning-artifacts/architecture.md`
  - `_bmad-output/implementation-artifacts/1-6-refactor-ocr-provider-to-langchain-graph-orchestrated-flow.md`
  - `_bmad-output/planning-artifacts/sprint-change-proposal-2026-03-02.md`

### Technical Impact
- `/v1/process` response envelope/contract remains unchanged.
- OCR adapter internals now require explicit graph-tool boundary and explicit LLM node call (`gpt-5-mini`).
- Tests must verify node order/invocation and typed OCR error mapping remains stable.

## 3. Recommended Approach

### Selected Path
**Direct Adjustment** (Option 1)

### Why
- Minimal disruption: no rollback, no MVP scope reduction.
- Keeps existing Story 1.6 and sprint tracking intact while clarifying implementation intent.
- Maximizes learning objective fidelity with low planning overhead.

### Effort / Risk / Timeline
- Effort: **Low** (planning artifact refinement only)
- Risk: **Low-Medium** (implementation complexity increases slightly with tool+LLM orchestration)
- Timeline impact: **Small** (contained to Story 1.6 implementation detail)

## 4. Detailed Change Proposals

### 4.1 Story Change (Epic Story Definition)

Story: **1.6 Refactor OCR Provider to LangChain Graph-Orchestrated Flow**
Section: Story intent + acceptance criteria

OLD:
- Story required explicit graph nodes/edges.
- Did not explicitly require OCR to be a tool node.
- Did not explicitly require a specific LLM call.

NEW:
- Story explicitly requires OCR to run as a graph tool node.
- Story explicitly requires graph call to LLM node using `gpt-5-mini`.
- Tests explicitly verify OCR tool node and LLM node invocation order.

Rationale:
- Makes learning objective concrete, inspectable, and testable.

### 4.2 Implementation Story File Change

Artifact: **`1-6-refactor-ocr-provider-to-langchain-graph-orchestrated-flow.md`**
Section: Acceptance criteria, tasks, dev notes, testing requirements

OLD:
- Graph nodes focused on transformation pipeline only.

NEW:
- Added `ocr_tool_node` and `llm_reasoning_node` requirements.
- Added explicit edge sequence including tool and LLM nodes.
- Added test requirements for invocation sequence and model node presence.

Rationale:
- Ensures implementation handoff is actionable and unambiguous.

### 4.3 Architecture Change

Artifact: **Architecture**
Section: Integration Points -> External Integrations

OLD:
- OCR graph requirement present, but no explicit tool/LLM call detail.

NEW:
- Architecture now states OCR graph should include OCR as graph tool node and an LLM node call to `gpt-5-mini` in the same graph path.

Rationale:
- Prevents drift between story-level and architecture-level guidance.

### 4.4 Sprint Tracking Change

Artifact: **`sprint-status.yaml`**

OLD:
- Story 1.6 is `ready-for-dev`.

NEW:
- No status change required; story remains `ready-for-dev`.
- No epic/story ID additions/removals/renumbering required.

Rationale:
- Scope changed within existing story boundary only.

## 5. Implementation Handoff

### Scope Classification
**Moderate** (planning change is small, implementation complexity is moderate)

### Route
- **Development team** for direct implementation of updated Story 1.6
- **PO/SM** informed only (no backlog restructuring required)

### Deliverables
- Updated Story 1.6 in epics with tool+LLM acceptance criteria.
- Updated implementation story file with concrete tool+LLM tasks.
- Updated architecture integration guidance for consistency.
- Updated sprint change proposal record.

### Success Criteria
- Story 1.6 implementation includes explicit OCR tool node and `gpt-5-mini` node call.
- `/v1/process` response contract remains unchanged.
- Tests validate graph path, node invocation order, and stable typed OCR errors.

## Checklist Status Snapshot

### Section 1: Understand Trigger and Context
- 1.1 Trigger story identified: `[x] Done`
- 1.2 Core problem defined: `[x] Done`
- 1.3 Evidence gathered: `[x] Done`

### Section 2: Epic Impact Assessment
- 2.1 Current epic evaluated: `[x] Done`
- 2.2 Epic-level changes determined: `[x] Done`
- 2.3 Remaining epics reviewed: `[x] Done`
- 2.4 Future epic invalidation/new epic check: `[x] Done`
- 2.5 Priority/order review: `[x] Done`

### Section 3: Artifact Conflict and Impact
- 3.1 PRD conflict checked: `[x] Done`
- 3.2 Architecture conflict checked: `[x] Done`
- 3.3 UX conflict checked: `[N/A]`
- 3.4 Other artifacts impact checked: `[x] Done`

### Section 4: Path Forward Evaluation
- 4.1 Direct Adjustment: `[x] Viable`
- 4.2 Potential Rollback: `[x] Not viable`
- 4.3 PRD MVP Review: `[x] Not viable`
- 4.4 Recommended path selected: `[x] Done`

### Section 5: Sprint Change Proposal Components
- 5.1 Issue summary: `[x] Done`
- 5.2 Impact and adjustments documented: `[x] Done`
- 5.3 Recommended path with rationale: `[x] Done`
- 5.4 MVP impact and action plan: `[x] Done`
- 5.5 Handoff plan: `[x] Done`

### Section 6: Final Review and Handoff
- 6.1 Checklist completion reviewed: `[x] Done`
- 6.2 Proposal accuracy verified: `[x] Done`
- 6.3 Explicit user approval: `[x] Done` (captured from direct user request)
- 6.4 Sprint-status updates applied: `[N/A]` (no ID/status structure changes needed)
- 6.5 Next steps and handoff confirmed: `[x] Done`

## Approval and Handoff Record

- User approval status: **Approved** (`yes`)
- Approval date: **2026-03-02**
- Scope classification: **Moderate**
- Routed to: **Development + PO/SM informed**

### Workflow Execution Log

- Correct-course rerun executed for tool+LLM requirement clarification.
- Artifacts updated for consistency:
  - `_bmad-output/planning-artifacts/epics.md`
  - `_bmad-output/planning-artifacts/architecture.md`
  - `_bmad-output/implementation-artifacts/1-6-refactor-ocr-provider-to-langchain-graph-orchestrated-flow.md`
  - `_bmad-output/planning-artifacts/sprint-change-proposal-2026-03-02.md`
- Sprint-status kept unchanged because story IDs/status structure did not change.

## Workflow Completion Summary

- Issue addressed: Story 1.6 lacked explicit OCR-as-tool and LLM-call requirements.
- Change scope: Moderate.
- Artifacts modified:
  - `_bmad-output/planning-artifacts/sprint-change-proposal-2026-03-02.md`
  - `_bmad-output/planning-artifacts/epics.md`
  - `_bmad-output/planning-artifacts/architecture.md`
  - `_bmad-output/implementation-artifacts/1-6-refactor-ocr-provider-to-langchain-graph-orchestrated-flow.md`
- Handoff recipients: Development (implementation), PO/SM (awareness).
