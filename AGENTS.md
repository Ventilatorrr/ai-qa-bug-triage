\# AI QA Bug Triage — Agent Instructions



\## General

\- Keep implementation simple and portfolio-focused.

\- Do not introduce unnecessary abstractions, libraries, frameworks, services, or infrastructure.

\- Do not make unrelated refactors unless explicitly requested.

\- Preserve existing naming, API contracts, and project conventions unless a change is agreed first.

\- The repository is the source of truth for current code.

\- If requirements/docs conflict with current code, report the mismatch before changing behavior.



\## Working Style

\- Make small, scoped changes.

\- Do not modify unrelated files.

\- Show/review the diff before commit.

\- Run relevant tests after changes.

\- Do not commit automatically unless explicitly asked.

\- Prefer incremental implementation and testing.



\## Python Environment

\- Repository:

&#x20; D:\\Portfolio\\ai-qa-bug-triage

\- Use the project virtual environment:

&#x20; D:\\Portfolio\\ai-qa-bug-triage\\.venv\\Scripts\\python.exe

\- Prefer commands such as:

&#x20; .\\.venv\\Scripts\\python.exe -m pytest

\- Do not assume the global/system Python is correct.



\## Testing

\- Prefer testing behavior through the public API.

\- Use direct database assertions only for persistence/integrity behavior that cannot be meaningfully verified through the API.

\- Backend authorization is the security authority; do not rely on UI hiding controls.

\- Use pytest parametrization when the same behavior is tested across multiple roles/inputs.

\- Every automated test should eventually appear in the traceability matrix.

\- Do not mark an AC fully Covered if required UI/manual layers are still unverified.



\## Requirements / Documentation

\- Acceptance Criteria are the primary specification format.

\- Keep BDD examples separate and small; do not add a BDD Scenario column to the main traceability matrix.

\- Main matrix focuses on:

&#x20; REQ, US, AC, Automated Test, Test Type, Status.

\- Do not invent missing REQ/AC IDs or requirements.

\- Do not change requirements unless explicitly requested.



\## Git

\- Use Conventional Commits:

&#x20; type: imperative lowercase description

\- No trailing period.

\- Common types:

&#x20; feat, fix, test, docs, refactor, ci, chore, style

\- Commit at logical milestones rather than bundling many unrelated changes.



\## Product Rules

\- Use "bug report", not "bug ticket".

\- UI permissions are UX; backend permissions are authoritative.

\- Do not assign application versions retrospectively.

\- Until versioning is formally introduced, leave Affected Version and Fix Version blank for newly discovered self-bugs.

\- For self-discovered bugs, follow:

&#x20; discover -> report -> classify -> assign -> fix -> test -> close.



\## Scope Control

\- Do not turn the app into a generic issue tracker.

\- Comments are postponed.

\- Version entity / version CRUD is postponed.

\- Mobile polish is lower priority than core desktop functionality.

\- Do not fix known deferred bugs opportunistically unless explicitly asked.



\## AI-Assisted Triage

\- AI suggestions must remain clearly distinct from authoritative bug data.

\- Human QA review remains in control.

\- Support per-suggestion Edit / Accept / Reject and bulk Accept All / Reject All when implemented.

\- If a user edits a suggestion, Accept All must apply the edited value, not the original AI value.



\## Before Editing

\- Inspect git status and relevant files first.

\- Confirm the requested scope.

\- If something important is unclear or conflicts with existing docs/code, ask before changing behavior.

