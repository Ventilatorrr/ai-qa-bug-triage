# AI QA Bug Triage — Agent Instructions

## Purpose and sources

This is a QA, QA Automation, and AI-QA portfolio and learning project.
Favor simple, understandable implementations and meaningful QA evidence.

The repository shows the current implementation. Requirements and approved
project decisions define intended behavior. Current user instructions override
older handoffs and these defaults.

If implementation, requirements, or approved decisions materially conflict,
surface the conflict rather than silently choosing one.

Use relevant sections of:

- `docs/requirements.md` for behavior and acceptance criteria;
- `docs/traceability-matrix.md` for coverage and test references;
- `docs/qa-strategy.md` for testing approach;
- `docs/definition-of-done.md` when assessing increment completion.

Read only the context needed for the task. Reuse established context and refresh
it when files change or assumptions need verification.

## Scope and collaboration

- Complete authorized work and proportionate verification without requesting
  approval for every routine step.
- Honor explicit review checkpoints, read-only requests, code-only requests,
  and other task-specific limits.
- Ask before expanding scope or making an unapproved product, requirement,
  architecture, dependency, or API-contract decision.
- Prefer focused changes and avoid bundling unrelated issues into one task.
- Preserve staged and unstaged user work.
- Avoid unrelated cleanup, speculative features, unnecessary abstractions,
  and new dependencies without a concrete need.
- Explain meaningful decisions and unfamiliar concepts clearly.
- Report unrelated findings separately rather than silently fixing them.

## Data and authorization

- Backend authorization is authoritative; UI visibility is not security.
- Use disposable databases for automated tests and defect reproduction.
- `tests/conftest.py` currently uses the fixed `test_bugtriage.db` filename;
  do not run test suites concurrently against it.
- Do not modify real application data or run migrations against the real
  application database unless the task explicitly requires and authorizes it.
- Do not manipulate real dogfooding bug records merely to test implementation;
  use supported test fixtures or explicitly authorized workflows.

## Verification and QA evidence

- Use the project virtual environment when running Python tests:
  `.\.venv\Scripts\python.exe -m pytest`
- Choose verification appropriate to the change and its risk.
- For regression defects, demonstrate that focused coverage detects the
  original failure when practical, then verify the correction.
- Prefer public API tests. Use direct database assertions when persistence or
  integrity cannot meaningfully be verified through the API.
- Follow existing fixtures and test style.
- Parameterize equivalent cases rather than duplicating tests.
- Authorization tests must otherwise satisfy request prerequisites so another
  validation failure does not mask the authorization behavior.
- Assert ordering only when ordering is part of the requirement.
- Report the evidence actually obtained.
- Distinguish source inspection, automated execution, and browser/manual
  verification.
- Do not claim visual or theme behavior was verified unless it was actually
  observed.

## Requirements and traceability

- Acceptance criteria are the primary behavioral specification.
- Keep BDD examples separate and representative; do not replace comprehensive
  acceptance criteria with exhaustive BDD scenarios.
- Preserve REQ, US, and AC identifiers and exact AC titles.
- Do not silently rewrite requirements to match the implementation.
- Keep affected implementation, tests, traceability, and documentation
  consistent within the authorized task scope.
- Traceability matrix columns are:
  `REQ | AC | Test Reference | Test Layer | Status`.
- Each automated test gets its own matrix row using its exact function name.
- Additional security, technical, or edge-risk tests may use `AC —`.
- Required UI or manual gaps prevent an AC from being marked fully `Covered`.
- Do not assign artificial manual test-case IDs to automated tests.
  Future formal manual cases may use identifiers such as `TC-PROJ-001`.
- Passing automated tests or implementing a page does not establish increment
  completion; use the Definition of Done.

## Product boundaries

- Use “bug report,” not “bug ticket.”
- Preserve defects and findings as QA evidence.
- Do not assign retrospective application versions.
- Until formal versioning is introduced, leave version fields blank for newly
  discovered self-bugs unless otherwise requested.
- Comments and version-management features remain deferred unless requested.
- AI suggestions remain visually and logically separate from authoritative bug
  data until accepted.
- If a user edits an AI suggestion before `Accept All`, the edited value must
  be applied rather than the original suggestion.
- Do not begin unrelated AI work during non-AI tasks.

## Git

Do not commit, rewrite history, delete branches, or perform destructive Git
operations unless explicitly authorized.

When a commit is requested, use a small logical Conventional Commit:

`type: imperative lowercase description`

No trailing period.
