---
date: 2026-03-26
workflow: correct-course
project: test-bmad
change_scope: moderate
mode: batch
---

# Sprint Change Proposal - Render Hosting and Sentry Monitoring

## 1. Issue Summary

### Trigger

The project's planning artifacts still assume an AWS-forward hosted target and optional Datadog integration, but implementation decisions have now shifted to:

- Render as the hosted deployment platform
- Sentry as the primary error tracking and performance monitoring tool

### Problem Statement

This is a strategic platform correction rather than a functional product change. The current documents create a mismatch between the intended operational path and the actual preferred platform. If left unchanged, future implementation stories would continue to optimize for AWS-oriented deployment and Datadog-oriented telemetry instead of the simpler Render + Sentry path chosen for the MVP.

### Evidence

- Architecture currently names AWS S3/CloudFront + Lambda/API Gateway as the future cloud target.
- PRD and epics currently describe observability in terms of optional Datadog integration.
- The backlog includes a Datadog-oriented telemetry story, but no story for Render deployment.

## 2. Impact Analysis

### Epic Impact

- **Epic 3** is directly affected.
  - Story 3.4 needs to change from generic Datadog-compatible telemetry to explicit Sentry integration.
  - A new deployment story is needed so the backlog includes Render hosting work.
- **Epics 1, 2, 4, and 5** remain structurally valid.
  - No story rollback is required.
  - No epic resequencing is required.

### Artifact Conflicts

- **PRD**
  - Observability language must change from optional Datadog integration to Sentry-based monitoring.
  - Hosted deployment target should explicitly name Render.
- **Architecture**
  - AWS-forward hosting references need to be replaced with Render as the hosted target.
  - Observability guidance needs to name Sentry.
  - Future persistence and deployment notes should become cloud-neutral or Render-oriented.
- **Epics**
  - FR26/NFR7 wording must be updated.
  - Story 3.4 must be rewritten for Sentry.
  - New Story 3.5 should cover Render deployment.
- **UX**
  - No user-flow or UI-spec change is required.

### Technical Impact

- Deployment work will target a Render static site plus Render web service.
- Error and performance monitoring will use Sentry SDKs instead of planning for Datadog ingestion.
- Health/metrics endpoints remain relevant and unchanged in principle.

## 3. Recommended Approach

### Selected Path

**Option 1: Direct Adjustment**

### Rationale

This is the lowest-risk correction. Product scope, UX flow, and core API behavior remain intact. The change is primarily operational and architectural, so the right move is to update planning artifacts and backlog stories without rolling back completed implementation work.

### Effort and Risk

- **Effort:** Low to Medium
- **Risk:** Low
- **Timeline impact:** Minimal; the change clarifies future implementation rather than expanding MVP scope materially

## 4. Detailed Change Proposals

### PRD

**Section: Observability references**

OLD:
- optional Datadog integration
- telemetry suitable for optional Datadog ingestion

NEW:
- Sentry integration for error and performance monitoring
- telemetry suitable for Sentry monitoring

Rationale: Aligns observability requirements with the chosen tooling.

**Section: Hosted deployment target**

OLD:
- Hosted platform not explicitly named in requirements

NEW:
- Render is the target hosted platform for the MVP

Rationale: Prevents future deployment stories from drifting back toward AWS-oriented assumptions.

### Architecture

**Section: Infrastructure and deployment target**

OLD:
- Future AWS target architecture: S3 + CloudFront, Lambda + API Gateway, DynamoDB + S3
- Terraform for AWS environments

NEW:
- Hosted target architecture: Render static site + Render web service
- Sentry for monitoring
- Render Blueprint (`render.yaml`) as deployment configuration direction
- Future persistence described as managed Postgres plus S3-compatible object storage when needed

Rationale: Matches the selected platform while preserving a clean future evolution path.

### Epics

**Story 3.4**

OLD:
- Emit telemetry for optional Datadog-compatible ingestion

NEW:
- Integrate Sentry error and performance monitoring

Rationale: Converts a generic observability placeholder into the actual chosen monitoring work.

**New Story 3.5**

NEW:
- Deploy frontend and backend to Render

Rationale: The selected platform must exist as backlog work, not just architecture prose.

### UX Design

- No change required.

## 5. Implementation Handoff

### Scope Classification

**Moderate**

The change affects architecture and backlog planning, but it does not require a product replan or code rollback.

### Handoff Recipients

- **Product Owner / Scrum Master**
  - Maintain backlog consistency with Story 3.4 and new Story 3.5
  - Keep sprint-status aligned to the approved story set
- **Architect**
  - Treat Render + Sentry as the operational source of truth for future design decisions
- **Development Team**
  - Implement Sentry instrumentation and Render deployment when Epic 3 is pulled into execution

### Success Criteria

- Planning artifacts no longer reference AWS-forward hosting as the target platform for MVP hosting
- Observability artifacts no longer position Datadog as the intended monitoring path
- Backlog contains explicit stories for Sentry integration and Render deployment

## Approval

Approved by user request on 2026-03-26 as the selected operational direction for the project.
