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
  architecture, dependency, provider, or API-contract decision.
- Prefer focused changes and avoid bundling unrelated issues into one task.
- Preserve staged and unstaged user work.
- Avoid unrelated cleanup, speculative features, unnecessary abstractions,
  and new dependencies without a concrete need.
- Explain meaningful decisions and unfamiliar concepts clearly.
- Report unrelated findings separately rather than silently fixing them.
- If manual or browser verification discovers a genuine application defect,
  stop before fixing it when practical and report it clearly so it can first
  be recorded as a real bug report in the application.


## Data and authorization

- Backend authorization is authoritative; UI visibility is not security.
- All automated testing, defect reproduction, and agent-driven browser interaction must use isolated, disposable test data.
- Never open, inspect, query, copy, modify, overwrite, delete, or migrate any real/non-test application database. This includes read-only inspection.
- Never interact with genuine dogfooding projects or bug reports through browser automation, APIs, scripts, or database tools. The user manages genuine QA records manually.
- Do not access a real database merely to verify that it is not being used. Verify test configuration and process startup instead.
- `tests/conftest.py` uses a fresh absolute database path per test under pytest's temporary directory; verify that configuration before startup. Keep test suites serial.
- Use fictional accounts, projects, bug reports, and mocked AI responses for automated testing unless explicitly instructed otherwise.


### Local browser testing

- Always use `http://127.0.0.1:8148` for agent-driven local browser testing of this project.
- This is the approved browser-testing origin. Do not select random alternative ports.
- Before starting a server, check whether port 8148 is available.
- If port 8148 is occupied, identify the existing process and its configuration. Never assume that an existing localhost server is safe, and never terminate or reuse an unidentified process.
- For frontend-only visual checks, prefer a static server with no database or application API access.
- For tests requiring a running backend, explicitly configure a fresh, isolated, disposable database before starting the application.
- Verify the effective database configuration and server process before any browser or API interaction. Do not rely on the port number alone as proof of isolation.
- If isolation cannot be verified, do not proceed with browser testing. Report the blocker instead.
- Never modify the browser's global site permissions or request unrestricted access to all websites.
- If the designated port cannot be used safely, ask before using another port.
- Shut down only test servers started and owned by the current task. Preserve unrelated processes and data.


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
- Running existing automated tests with the project's virtual environment
  against the disposable test database is pre-approved and expected when
  relevant. Do not ask for permission before running focused or full existing
  test suites unless the command would access real/non-test data or leave the
  repository sandbox.


## Requirements and traceability

- Acceptance criteria are the primary behavioral specification.
- Work through traceability alongside each requirement rather than treating the
  matrix as end-of-project documentation.
- Preserve REQ, US, and AC identifiers and exact AC titles.
- Do not silently rewrite requirements to match the implementation.
- Keep affected implementation, tests, traceability, and documentation
  consistent within the authorized task scope.
- Traceability matrix columns are:
  `REQ | AC | TC IDs | Test Type | Overall Coverage`.
- Keep exactly one authoritative RTM row per AC. Assess collective evidence;
  do not assign overall AC coverage to individual test contributions.
- Catalogue every maintained automated case and structured manual group in
  `docs/test-cases.md` using the global `TC-001`, `TC-002`, ... sequence.
  Never renumber or reuse an assigned ID; consult the catalogue's next ID.
- Keep exact implementation references and concise TC/AC comments in test source.
  Equivalent parameter variants share an ID. Approved distinct conceptual cases
  may share a function; record exact selectors and all applicable IDs without
  refactoring the function merely for documentation. Report new ambiguities.
- Technical/security/infrastructure cases still receive IDs and may use `—`
  for their AC mapping. Do not invent requirements to justify tests.
- Record suite-level results and manual/exploratory provenance in
  `docs/test-execution.md`; retain M01–M05 as manual aliases. Keep genuine defect
  references in `docs/defect-summary.md`, with the application as source of truth.
- Required UI or manual gaps prevent an AC from being marked fully `Covered`.
- Separate Covered/Partial/Not Covered AC assessments from execution results.
  BDD specifications without executable bindings receive no execution TC IDs
  and do not count as passing automation.
- Passing automated tests or implementing a page does not establish increment
  completion; use the Definition of Done.
- BDD is not the normal implementation or traceability workflow for this
  project. Do not add or expand BDD coverage unless explicitly requested.
- A small set of representative BDD examples may be added separately near the
  end of the project as portfolio evidence; do not attempt exhaustive BDD
  coverage.


## Versioning

- Application versioning is active.
- `APP_VERSION` is the application source of truth for the running version.
- Git tags and GitHub Releases represent releases and are distinct from normal
  commits.
- Affected Version means a version in which the bug was observed or reproduced;
  it does not necessarily identify the version in which the defect was first
  introduced.
- Do not assign a released version to a defect that exists only in unreleased
  feature work.
- Leave Affected Version blank when no appropriate released/observed version is
  known.
- Fix Version means the released version in which the fix actually became
  available.
- Do not populate Fix Version merely with a planned or expected future release.
- Non-fix resolutions may legitimately have no Fix Version.


## AI-assisted triage boundaries

- Follow `docs/requirements.md` REQ-018 through REQ-023 as the source of truth
  for Increment 3 behavior.
- Do not use historical AI requirement drafts when they conflict with the
  current requirements.
- AI Assist is explicitly triggered by the user; opening New Bug or Edit Bug
  must not automatically invoke AI behavior.
- Pending AI suggestions remain visually and logically separate from normal
  editable bug fields.
- Per-suggestion actions are `Use` and `Dismiss`.
- Bulk actions are `Use All` and `Dismiss All`.
- `Use` copies the suggested value into the corresponding normal form field.
  The user may then edit that field normally.
- `Use All` copies only the remaining pending suggestions. Suggestions already
  used or dismissed are not reapplied.
- `Dismiss` and `Dismiss All` do not revert values that were previously used.
- AI suggestions never directly create, save, or modify authoritative bug data.
  Only the normal `Create` or `Save` action persists form values.
- Do not introduce AI suggestions for Fix Version, Status, Resolution, Created,
  or Updated.
- Do not fabricate missing factual details merely to populate a field.
- Do not introduce agents, vector search, embeddings, RAG, or other additional
  AI architecture unless explicitly approved.
- Do not choose an AI provider, model, dependency, or external API contract
  without explicit approval when the project has not already established one.
- Do not begin unrelated AI work during non-AI tasks.


## Product boundaries

- Use “bug report,” not “bug ticket,” in product/documentation terminology.
- Preserve genuine defects and findings as QA evidence.
- Comments and version-management features remain deferred unless requested.
- Prefer simple implementations suitable for the portfolio project rather than
  enterprise-scale abstractions without a demonstrated need.


## Git

Do not commit, rewrite history, delete branches, or perform destructive Git
operations unless explicitly authorized.

When a commit is requested, use a small logical Conventional Commit:

`type: imperative lowercase description`

No trailing period.


## Agent Final Handoff

For implementation, testing, documentation, or refactoring tasks, do not commit
unless explicitly instructed.

At the end of each task, provide a concise handoff containing:

1. A summary of what was implemented.
2. Every file changed, added, or deleted.
3. Tests and verification commands run, with exact results.
4. Bugs or issues discovered during the task.
5. Decisions, assumptions, and intentionally deferred work.
6. Relevant requirement/traceability status when applicable.
7. Output of `git status --short`.
8. Output of `git diff --stat HEAD`.
9. Whether the work is a clean commit-sized slice.

Do NOT include the complete Git diff or complete contents of changed/untracked
files unless explicitly requested. The user will generate the complete handoff
locally when needed.

Do not stage files merely to produce the handoff.

If the task explicitly requires staging after review, additionally provide:

- `git status --short`;
- `git diff --cached --stat`;
- confirmation that all intended files are staged and no unrelated files are
  staged.

Do not commit unless explicitly authorized.
