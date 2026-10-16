# Improvement Backlog

Proposed features and enhancements for the AI QA Bug Triage application. This is a lightweight planning backlog, **not** a list of implemented requirements or verified defects.

| ID | Type | Improvement | Priority | Status |
| --- | --- | --- | --- | --- |
| BL-001 | UX enhancement | Preselect the assigned Developer when moving a bug from Open to Development | Low | Proposed |

## BL-001 — Preselect the assigned Developer

**Current behavior:** When a bug is already assigned to a Developer, moving it from Open to Development still requires selecting a Developer again.

**Proposed behavior:** Preselect the current assignee if they are an eligible Developer on that project. The user can keep that selection or choose another Developer.

**Expected behavior:**
- Eligible Developer already assigned → preselected.
- QA Analyst or no assignee → no Developer preselected.
- Selection does not automatically trigger the transition; existing permissions and validation still apply.

**Status:** Proposed. Not implemented.

## Backlog conventions

- Use the next `BL-###` ID for any new feature, enhancement, or improvement; never reuse an ID.
- **Types:** New feature, UX enhancement, Technical improvement.
- **Statuses:** Proposed, Approved, In Progress, Done, Deferred, Rejected.
- Keep proposals brief. Add detailed requirements and test cases only when an improvement is approved for implementation.
- Record defects in the application itself; do not duplicate them here.
