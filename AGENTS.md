# AI QA Bug Triage — Agent Instructions

## General and sources of truth

- Keep implementation simple and portfolio-focused. Do not introduce unnecessary abstractions, libraries, frameworks, services, or infrastructure.
- Preserve existing naming, API contracts, and product decisions unless a change is agreed first.
- The repository is the source of truth for current code, not proof that current behavior is correct. Requirements and approved decisions define intended behavior.
- Current explicit user instructions take precedence over older handoffs and these working defaults. Do not revive superseded decisions or requirement numbering.
- Read the current requirements, relevant acceptance criteria, traceability entries, and nearby implementation/tests before proposing changes.
- Report conflicts between code, documentation, and handoffs before changing behavior. Ask when an ambiguity affects implementation.

## Before editing

- Inspect `git status`, `git diff`, `git diff --cached`, and `git log -5 --oneline`.
- Preserve existing staged and unstaged changes. Do not discard, overwrite, or commit unrelated user work.
- Confirm the requested scope. Work on one issue at a time; do not perform opportunistic cleanup or unrelated refactors.
- Read-only inspection and reproduction in a disposable test database may proceed within the requested scope.

## Step-by-step approval workflow

Unless the user explicitly changes these checkpoints:

1. Inspect and reproduce the issue. Explain its cause, proposed regression test or verification, and smallest likely fix. Wait for approval before editing files.
2. After test approval, add or adjust only the focused test. Demonstrate failure for the expected reason when handling a regression defect. Show the change and result, then stop for review.
3. Wait for approval to implement the fix. Apply the smallest coherent change, run focused tests and the appropriate wider/full regression suite, and show the diff and results. Stop for review.
4. Propose the corresponding traceability/documentation update. Apply it after approval, using the existing format and accurate coverage by layer.
5. Do not move to another issue or commit without explicit approval.

- Follow existing test style, fixture patterns, naming, and assertions. Explain changes in plain language so the user can understand and review them.
- If a test is not appropriate, explain the proposed verification instead of adding a test that merely mirrors implementation.
- Do not change bug lifecycle status, classification, assignment, or closure unless explicitly delegated. The user manages these actions by default.

## Python environment and test data

- Local repository: `D:\Portfolio\ai-qa-bug-triage`
- Project Python: `D:\Portfolio\ai-qa-bug-triage\.venv\Scripts\python.exe`
- From the repository root, use commands such as `.\.venv\Scripts\python.exe -m pytest`.
- Do not assume global/system Python is correct. In another environment, inspect its configuration rather than treating the Windows path as available.
- Reproduce defects and run automated tests only against disposable test databases. Confirm isolation before running database-writing checks.
- Do not modify real application records, migrate the application database, or delete real projects without explicit authorization for that action.
- Inspect the current test database setup before concurrent runs; do not run tests concurrently when they share a fixed database filename.

## Testing and traceability

- Prefer public API behavior tests. Use direct database assertions only for persistence/integrity behavior that cannot meaningfully be verified through the API.
- Backend authorization is authoritative; hiding UI controls does not establish security.
- Reuse existing fixtures and use pytest parameterization for the same behavior across roles or inputs. Avoid duplicate test names and redundant coverage.
- Run relevant tests and report actual results, including limitations. A passing API suite does not prove UI completion.
- Keep automated coverage traceable. Map tests to existing REQ/US/AC entries where applicable; record additional security/regression coverage explicitly without inventing or forcing an AC mapping.
- Do not mark an AC fully Covered if required UI/manual behavior is still unverified. Preserve Partial/Pending distinctions by layer.

## Requirements and documentation

- Acceptance Criteria are the primary specification format. Do not change requirements without approval.
- Keep approximately five representative BDD examples separate from the main matrix. Do not add a BDD Scenario column.
- Main matrix columns: REQ, AC, Test Reference, Test Layer, Status.
- Follow existing Test Layer conventions, such as API, UI (Playwright), API / Security, UI / Security, Manual, or API + UI, as applicable.
- Do not invent REQ/US/AC IDs. Use current repository numbering.
- Keep detailed product specifications and current progress in requirements/project documentation and handoffs rather than duplicating them here.

## Git

- No automatic commits. Show the diff and test evidence first; commit only when explicitly authorized.
- Use Conventional Commits: `type: imperative lowercase description`, with no trailing period.
- Common types: feat, fix, test, docs, refactor, ci, chore, style.
- Prefer logical milestones rather than bundling unrelated changes.

## Product and scope rules

- Use “bug report”, not “bug ticket”. Do not turn the app into a generic issue tracker.
- For self-discovered bugs, preserve the real process: discover → report → classify → assign → fix → test → close. This does not authorize automatic application-record or lifecycle changes.
- Do not assign application versions retrospectively. Until versioning is introduced, leave Affected Version and Fix Version blank for newly discovered self-bugs.
- Comments and version entities/version CRUD are postponed.
- Mobile polish is lower priority than core desktop functionality.
- Do not implement deferred ideas or fix unrelated known defects opportunistically.

## AI-assisted triage

- AI suggestions remain clearly distinct from authoritative bug data until accepted. Human QA review remains in control.
- When this increment is selected, support per-suggestion Edit / Accept / Reject and bulk Accept All / Reject All.
- If a user edits a suggestion, Accept All must apply the edited value, not overwrite it with the original AI suggestion.
- Do not begin AI work during unrelated defect cleanup.
