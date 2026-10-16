# Selected historical verification evidence

Curated from the former RTM at `ec567dd`. These are historical execution/source
records, not new runs or current tracker status. Repeated implementation chronology,
old aggregate totals and superseded palette/header measurements are omitted.
Current results are in [test execution](../test-execution.md); detailed 12–13 October
theme/native evidence remains in the [existing report](../ui-refinements-verification.md).

## Public identity and persistence regressions — 7–8 October 2026

- Public project-local identity refinement initially observed 18 Python failures/28 passes and 16 frontend failures/23 passes. One initial Python failure was a test-stub constructor error; its corrected isolated case then failed on the intended global-ID routing assertion. Final focused API verification passed 293 cases; full backend 510 and frontend 76 passed at that checkpoint.
- Numbering/migration tests verify complete legacy-field preservation, deterministic per-project backfill, rollback before replacement and before commit, unchanged repeated startup, and no number consumption after failed creation. These use disposable databases. Source references are now catalogued under technical cases, not invented business ACs.
- Fix Version lifecycle correction demonstrated the defect before correction: 11 failures/39 deselected. An initial wider run had two new list/detail-shape assertion errors; after test correction, focused Fix Version/readback verification passed 54 cases, full backend 544 and frontend 77 at that checkpoint. These counts are historical, not current suite totals.

## Frontend diagnostics — 6–9 October 2026

- Recorded sorting diagnostics executed actual handlers/rendering with DOM/API substitutes: columns/directions, case-insensitive text, missing values last, indicators, unchanged values/links, no sorting writes/source mutation, refresh and empty recovery. Complete classification/status rank datasets are not recorded; AC-012.4 retains that gap.
- Thirteen pagination diagnostic groups passed for sizes/ranges/navigation, full-list sorting before slicing, resets, local-number links, unchanged source data, per-user size persistence and independent sorting, invalid/blocked storage, added/reduced/exact-boundary refresh counts, empty recovery and persisted Back/Forward entry. The attempted browser connection timed out; those diagnostics alone establish no native layout or browser create/delete workflow.
- Nine clickable-row diagnostic groups covered anchor-destination reuse, native-link/modifier/nonprimary/prevented-event exclusion, selected-text and nested-control guards, semantics, sorting, pagination/size changes and refresh. Native mouse/keyboard/theme verification was still pending at that checkpoint; later M02 evidence is recorded separately.
- Thirteen one-off lifecycle visibility checks passed for viewport edges, offscreen/hidden/disabled controls, feedback visibility and absent scrolling APIs. They were simulated checks, not native scroll geometry. The current M04 report is separate.
- Recorded BUG-20 browser observations covered whitespace feedback, meaningful correction, Cancel/reopen and successful project Save/Create feedback cleanup. Unrelated-feedback preservation also has maintained actual-handler frontend tests.

Temporary diagnostics are executed historical evidence, not maintained tests with
new TC IDs. No unavailable scripts or external artifact paths are presented as
current repeatable commands.

## AI review and form safety — 5 October 2026

Recorded disposable-app browser smoke used mocked AI output with the authoritative
validator and exercised Owner/QA paths. New/Edit observations included review/use,
individual/bulk dismissal, subsequent manual editing, repeat requests, safe failure
and empty outcomes. AI actions left authoritative data unchanged until normal
Create/Save; Edit Cancel restored stored values, and blank-title validation remained
active after Use All. Pending Edit review was discarded on reload/navigation.
Script-like suggestions displayed as literal text. Later delayed Create/Save
Cancel/reopen verification preserved newer form values, review and feedback while
persisted older submissions refreshed surrounding data. Temporary test resources
were reported removed. This is historical smoke evidence, not real-model quality.

## Mobile layout and AI disclosure — 14 October 2026

Recorded isolated mobile checks exercised actual renderers at narrow/desktop widths
in both themes, mobile sort/pagination and preference continuity. Later static
header refinements retained theme/navigation/Logout behavior; they do not establish
physical-device, screen-reader or other-engine coverage.

Recorded actual-app notice checks used a verified temporary database and mocked
provider: New/Edit notice placement, keyboard dismissal, preservation of pending
cards/form guidance, removal from accessible description, and persistence across
reload/reopen and navigation between forms. Static follow-ups checked final compact
notice text/spacing in both themes. Cached-navigation notice behavior also has
maintained JavaScript tests. No application-managed secrets are inferred from
user-entered content; arbitrary secret detection/redaction was never claimed.

Known limitations and unverified assertions remain explicit in the current RTM,
execution record and Definition of Done. Historical non-Fixed Failed-version
preservation observations were superseded by the 8 October clearing requirement
and its API tests; they are not retained as current behavior.
