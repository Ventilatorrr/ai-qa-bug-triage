# Defect Summary

This report summarizes the 53 defects recorded as bug reports in the application's own tracker during its development. Other issues were found and fixed during development without separate bug reports, so the figures represent recorded defects, not every issue encountered.

**Snapshot:** 28 October 2026 · **Source:** read-only extraction of the local application tracker, project **AI QA Bug Triage** (BUG-1–BUG-53). The application remains the source of truth; this is a dated record, not a live tracker. Fictional and scratch test projects and Try Demo copies are excluded. This snapshot is not a v1.0.0 Go/No-Go assessment; release verification is listed in the [execution report](test-execution.md#pending-release-verification).

## Summary

**53 recorded defects, all Closed:** 51 Fixed · 1 Not a Bug (BUG-1) · 1 Won't Fix (BUG-36). Discovered 10 in September and 43 in October 2026 (first 7 September, latest 28 October). BUG-1 and BUG-36 were closed without a fix and have no Fix Version.

| Fix Version | Fixed defects | Release |
| --- | ---: | --- |
| `0.1.0` | 5 | Released 21 September 2026 |
| `0.2.0` | 34 | Released 24 October 2026 |
| `1.0.0` | 12 | Planned; not yet released |
| **Total** | **51** | |

| Metric | Distribution |
| --- | --- |
| Severity | 1 Blocker · 8 Major · 15 Moderate · 29 Minor |
| Priority | 13 High · 25 Medium · 15 Low (no Urgent) |
| Affected Version | 8 `0.1.0-dev` · 3 `0.1.0` · 30 `0.2.0-dev` · 12 `1.0.0-dev` |

Affected Version records the version in which a defect was observed; `-dev` labels are development builds, not releases. See [versioning and defect versions](qa-strategy.md#14-versioning-and-defect-versions).

| Severity \ Priority | Urgent | High | Medium | Low |
| --- | ---: | ---: | ---: | ---: |
| Blocker | 0 | 1 | 0 | 0 |
| Major | 0 | 7 | 1 | 0 |
| Moderate | 0 | 4 | 11 | 0 |
| Minor | 0 | 1 | 13 | 15 |
| **Total** | **0** | **13** | **25** | **15** |

## Recorded defects

| Bug ID | Title | Severity | Priority | Resolution | Affected | Fix |
| --- | --- | --- | --- | --- | --- | --- |
| BUG-1 | System allows duplicate project names | Moderate | Medium | Not a Bug | 0.1.0-dev | — |
| BUG-2 | Textareas contain leading whitespace when creating a new bug | Minor | Low | Fixed | 0.1.0-dev | 0.1.0 |
| BUG-3 | Bug IDs are not project-specific | Minor | Low | Fixed | 0.1.0 | 0.2.0 |
| BUG-4 | New project owner can see bugs from a deleted project | Major | High | Fixed | 0.1.0-dev | 0.1.0 |
| BUG-5 | POST /register returns HTTP 500 for passwords over bcrypt's 72-byte limit | Moderate | Medium | Fixed | 0.1.0-dev | 0.1.0 |
| BUG-6 | Project form feedback remains stale after correction, successful edit, cancel, or reopening | Minor | Low | Fixed | 0.1.0-dev | 0.2.0 |
| BUG-7 | Project edit accepts whitespace-only project name | Minor | Medium | Fixed | 0.1.0-dev | 0.2.0 |
| BUG-8 | No success confirmation is displayed after project creation | Minor | Low | Fixed | 0.1.0-dev | 0.1.0 |
| BUG-9 | Removing an assigned project member leaves bugs assigned to that user | Moderate | Medium | Fixed | 0.1.0-dev | 0.1.0 |
| BUG-10 | AI Assist button is visible to Developer on New Bug form | Moderate | High | Fixed | 0.2.0-dev | 0.2.0 |
| BUG-11 | Whitespace-only JWT_SECRET_KEY is accepted | Major | High | Fixed | 0.2.0-dev | 0.2.0 |
| BUG-12 | JWT security tests delete shared test database and cause order-dependent failures | Major | High | Fixed | 0.2.0-dev | 0.2.0 |
| BUG-13 | Multiline AI suggestion value changes when applied to a single-line bug field | Moderate | High | Fixed | 0.2.0-dev | 0.2.0 |
| BUG-14 | Late Create or Save response can discard a reopened bug form and newer AI suggestions | Moderate | High | Fixed | 0.2.0-dev | 0.2.0 |
| BUG-15 | Stale Create response can overwrite feedback in a newer bug form session | Moderate | High | Fixed | 0.2.0-dev | 0.2.0 |
| BUG-16 | Bug list refresh error is hidden after successful New Bug creation | Moderate | Medium | Fixed | 0.2.0-dev | 0.2.0 |
| BUG-17 | Delayed bug-list refresh can overwrite feedback from a newer New Bug session | Moderate | Medium | Fixed | 0.2.0-dev | 0.2.0 |
| BUG-18 | Bug list sorting resets to Last Updated after navigating away and returning | Minor | Low | Fixed | 0.2.0-dev | 0.2.0 |
| BUG-19 | POST /projects returns HTTP 500 when project name is not a string | Moderate | Medium | Fixed | 0.1.0 | 0.2.0 |
| BUG-20 | Lifecycle action buttons remain enabled when required selections are missing | Minor | Medium | Fixed | 0.2.0-dev | 0.2.0 |
| BUG-21 | Concurrent bug deletion can cause edit or status update to fail during response readback | Moderate | Medium | Fixed | 0.2.0-dev | 0.2.0 |
| BUG-22 | Bug action buttons shift vertically when feedback message appears | Minor | Low | Fixed | 0.2.0-dev | 0.2.0 |
| BUG-23 | Stale success messages persist across bug and member workflows | Minor | Medium | Fixed | 0.2.0-dev | 0.2.0 |
| BUG-24 | Fix Version is available when creating or editing unresolved bugs | Moderate | Medium | Fixed | 0.1.0 | 0.2.0 |
| BUG-25 | Lifecycle action controls move out of view after bug status transitions | Minor | Medium | Fixed | 0.2.0-dev | 0.2.0 |
| BUG-26 | Original text field does not expand to use available space beside a taller AI suggestion panel | Minor | Medium | Fixed | 0.2.0-dev | 0.2.0 |
| BUG-27 | Dropdown arrow color changes based on selected value | Minor | Low | Fixed | 0.2.0-dev | 0.2.0 |
| BUG-28 | Unexpected black background bar behind AI Priority suggestion "Urgent" | Minor | Medium | Fixed | 0.2.0-dev | 0.2.0 |
| BUG-29 | Incomplete horizontal dividers in bug details when Fix Version and Resolution are hidden | Minor | Low | Fixed | 0.2.0-dev | 0.2.0 |
| BUG-30 | Double turquoise border appears when focusing form fields | Minor | Low | Fixed | 0.2.0-dev | 0.2.0 |
| BUG-31 | WCAG 2.2 AA contrast failure for Blocker/Urgent text in dark theme | Major | High | Fixed | 0.2.0-dev | 0.2.0 |
| BUG-32 | Bug List table does not fit mobile viewport, requiring horizontal scrolling to access bug information | Moderate | Medium | Fixed | 0.2.0-dev | 0.2.0 |
| BUG-33 | AI suggestion validation accepts conflicting duplicate JSON properties | Major | Medium | Fixed | 0.2.0-dev | 0.2.0 |
| BUG-34 | Success message overflows the viewport when creating a bug with an extremely long title | Minor | Low | Fixed | 0.2.0-dev | 0.2.0 |
| BUG-35 | AI Assist does not use relevant historical bug data in suggestions | Minor | Medium | Fixed | 0.2.0-dev | 0.2.0 |
| BUG-36 | Globally sequential project IDs expose internal project numbering | Minor | Low | Won't Fix | 0.2.0-dev | — |
| BUG-37 | New Bug form allows multiple submissions and creates duplicate reports | Major | High | Fixed | 0.2.0-dev | 0.2.0 |
| BUG-38 | Adding a project member with an invalid email type returns HTTP 500 | Minor | Medium | Fixed | 0.2.0-dev | 0.2.0 |
| BUG-39 | Inconsistent font family across application pages | Minor | Medium | Fixed | 0.2.0-dev | 0.2.0 |
| BUG-40 | Bug List pagination controls shift vertically between pages with different title lengths | Minor | Medium | Fixed | 0.2.0-dev | 0.2.0 |
| BUG-41 | Bug List background brightness changes with different Bugs per page settings | Minor | Low | Fixed | 0.2.0-dev | 0.2.0 |
| BUG-42 | Try Demo button on the Login page is misaligned and lacks visual distinction | Minor | High | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-43 | Authorization race allows access to or modification of another user's project | Blocker | High | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-44 | Login returns HTTP 500 for passwords exceeding 72 UTF-8 bytes | Moderate | Medium | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-45 | Delayed project rename can overwrite newer edits | Minor | Medium | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-46 | Creating a project discards unsaved edits to another project's name | Minor | Low | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-47 | Browser navigation can cause stale bug editor to overwrite newer changes | Major | High | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-48 | JWT for nonexistent user can create orphan project membership and prevent application startup | Major | High | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-49 | Project-ID reuse race can delete or expose another project's bug and member data | Moderate | Medium | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-50 | New Bug form loses selected assignee when project membership changes | Minor | Medium | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-51 | Project page status messages are not automatically announced to screen-reader users | Minor | Low | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-52 | Light theme briefly flashes dark when loading a page | Minor | Low | Fixed | 1.0.0-dev | 1.0.0 |
| BUG-53 | New Bug validation errors appear outside the visible viewport | Minor | Medium | Fixed | 1.0.0-dev | 1.0.0 |

## Verification evidence

Dated verification is recorded in the [execution report](test-execution.md) for [BUG-28](test-execution.md#bug-28-ai-urgent-suggestion-backplate--13-october-2026), [BUG-31](test-execution.md#contrast-measurements--13-october-2026), [BUG-34](test-execution.md#bug-34-success-confirmation-overflow--19-october-2026), [BUG-37](test-execution.md#bug-37-duplicate-new-bug-submission--22-october-2026), [BUG-38](test-execution.md#malformed-add-member-email-http-500-audit-b2--22-october-2026), [BUG-39](test-execution.md#bug-39-global-base-font--23-october-2026), [BUG-41](test-execution.md#bug-41-page-background-brightness-with-page-size--23-october-2026), [BUG-42](test-execution.md#try-demo-and-ai-usage-limits--27-october-2026), [BUG-48–BUG-51](test-execution.md#release-hardening--28-october-2026), [BUG-52](test-execution.md#bug-52-light-theme-flash--28-october-2026) and [BUG-53](test-execution.md#bug-53-ac-0115-limit-feedback--28-october-2026). For BUG-40, the [Bug List layout record](test-execution.md#bug-list-layout--23-october-2026) measured every desktop row at 61px regardless of title length, so the pagination controls stay fixed across full pages; [TC-411](test-cases.md#tc-411) asserts equal row heights for short and long titles. A partial final page still moves the controls up, which was left unchanged. Other defects have no separate dated execution record; their regression tests are listed in the [test-case catalogue](test-cases.md).
