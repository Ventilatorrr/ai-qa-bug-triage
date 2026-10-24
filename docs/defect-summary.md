# Defect Summary

**Snapshot:** 24 October 2026 · **Source:** read-only query (`mode=ro`) of the local application tracker, project **AI QA Bug Triage**. The application remains the source of truth; this is a dated record, not a live tracker. Records in four other local projects are fictional or scratch test data and are excluded.

**Summary:** 41 recorded defects (BUG-1–BUG-41), all Closed: 39 Fixed · 1 Not a Bug · 1 Won't Fix. Discovered 10 in September and 31 in October 2026 (first 7 September, latest 23 October).

| Metric | Distribution |
| --- | --- |
| Severity | 6 Major · 13 Moderate · 22 Minor (no Blocker) |
| Priority | 9 High · 20 Medium · 12 Low (no Urgent) |
| Affected Version | 8 `0.1.0-dev` · 3 `0.1.0` · 30 `1.0.0-dev` |
| Fix Version (as recorded) | 34 `1.0.0` · 5 `0.1.0` · 2 none (non-fix resolutions) |

| Severity \ Priority | High | Medium | Low |
| --- | ---: | ---: | ---: |
| Major | 5 | 1 | 0 |
| Moderate | 4 | 9 | 0 |
| Minor | 0 | 10 | 12 |

**Fix Version note:** Fix Version identifies the release in which a fix is included or planned to be included. `1.0.0` is the intended upcoming release and has not yet been published (the latest release tag is `v0.1.0`; the running version is `1.0.0-dev`); its final contents will be confirmed during release verification.

| Bug ID | Title | Severity | Priority | Resolution | Affected | Fix |
| --- | --- | --- | --- | --- | --- | --- |
| BUG-1 | System allows duplicate project names | Moderate | Medium | Not a Bug | 0.1.0-dev | — |
| BUG-2 | Textareas contain leading whitespace when creating a new bug | Minor | Low | Fixed | 0.1.0-dev | 0.1.0 |
| BUG-3 | Bug IDs are not project-specific | Minor | Low | Fixed | 0.1.0 | 1.0.0 |
| BUG-4 | New project owner can see bugs from a deleted project | Major | High | Fixed | 0.1.0-dev | 0.1.0 |
| BUG-5 | POST /register returns HTTP 500 for passwords over bcrypt's 72-byte limit | Moderate | Medium | Fixed | 0.1.0-dev | 0.1.0 |
| BUG-6 | Project form feedback remains stale after correction, successful edit, cancel, or reopening | Minor | Low | Fixed | 0.1.0-dev | 1.0.0 |
| BUG-7 | Project edit accepts whitespace-only project name | Minor | Medium | Fixed | 0.1.0-dev | 1.0.0 |
| BUG-8 | No success confirmation is displayed after project creation | Minor | Low | Fixed | 0.1.0-dev | 0.1.0 |
| BUG-9 | Removing an assigned project member leaves bugs assigned to that user | Moderate | Medium | Fixed | 0.1.0-dev | 0.1.0 |
| BUG-10 | AI Assist button is visible to Developer on New Bug form | Moderate | High | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-11 | Whitespace-only JWT_SECRET_KEY is accepted | Major | High | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-12 | JWT security tests delete shared test database and cause order-dependent failures | Major | High | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-13 | Multiline AI suggestion value changes when applied to a single-line bug field | Moderate | High | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-14 | Late Create or Save response can discard a reopened bug form and newer AI suggestions | Moderate | High | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-15 | Stale Create response can overwrite feedback in a newer bug form session | Moderate | High | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-16 | Bug list refresh error is hidden after successful New Bug creation | Moderate | Medium | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-17 | Delayed bug-list refresh can overwrite feedback from a newer New Bug session | Moderate | Medium | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-18 | Bug list sorting resets to Last Updated after navigating away and returning | Minor | Low | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-19 | POST /projects returns HTTP 500 when project name is not a string | Moderate | Medium | Fixed | 0.1.0 | 1.0.0 |
| BUG-20 | Lifecycle action buttons remain enabled when required selections are missing | Minor | Medium | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-21 | Concurrent bug deletion can cause edit or status update to fail during response readback | Moderate | Medium | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-22 | Bug action buttons shift vertically when feedback message appears | Minor | Low | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-23 | Stale success messages persist across bug and member workflows | Minor | Medium | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-24 | Fix Version is available when creating or editing unresolved bugs | Moderate | Medium | Fixed | 0.1.0 | 1.0.0 |
| BUG-25 | Lifecycle action controls move out of view after bug status transitions | Minor | Medium | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-26 | Original text field does not expand to use available space beside a taller AI suggestion panel | Minor | Medium | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-27 | Dropdown arrow color changes based on selected value | Minor | Low | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-28 | Unexpected black background bar behind AI Priority suggestion "Urgent" | Minor | Medium | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-29 | Incomplete horizontal dividers in bug details when Fix Version and Resolution are hidden | Minor | Low | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-30 | Double turquoise border appears when focusing form fields | Minor | Low | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-31 | WCAG 2.2 AA contrast failure for Blocker/Urgent text in dark theme | Major | High | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-32 | Bug List table does not fit mobile viewport, requiring horizontal scrolling to access bug information | Moderate | Medium | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-33 | AI suggestion validation accepts conflicting duplicate JSON properties | Major | Medium | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-34 | Success message overflows the viewport when creating a bug with an extremely long title | Minor | Low | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-35 | AI Assist does not use relevant historical bug data in suggestions | Minor | Medium | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-36 | Globally sequential project IDs expose internal project numbering | Minor | Low | Won't Fix | 1.0.0-dev | — |
| BUG-37 | New Bug form allows multiple submissions and creates duplicate reports | Major | High | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-38 | Adding a project member with an invalid email type returns HTTP 500 | Minor | Medium | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-39 | Inconsistent font family across application pages | Minor | Medium | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-40 | Bug List pagination controls shift vertically between pages with different title lengths | Minor | Medium | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-41 | Bug List background brightness changes with different Bugs per page settings | Minor | Low | Fixed | 1.0.0-dev | 1.0.0 |

Recorded execution evidence: [BUG-34](test-execution.md#bug-34-success-confirmation-overflow--19-october-2026), [BUG-37](test-execution.md#bug-37-duplicate-new-bug-submission--22-october-2026), [BUG-38](test-execution.md#malformed-add-member-email-http-500-audit-b2--22-october-2026), [BUG-39](test-execution.md#bug-39-global-base-font--23-october-2026) and [BUG-41](test-execution.md#bug-41-page-background-brightness-with-page-size--23-october-2026). For BUG-40, the [Bug List layout record](test-execution.md#bug-list-layout--23-october-2026) measured every desktop row at 61px regardless of title length, so the pagination controls stay fixed across full pages; [TC-411](test-cases.md#tc-411) asserts equal row heights for short and long titles. A partial final page still moves the controls up, which was left unchanged. Earlier defects predate the dated execution records.
