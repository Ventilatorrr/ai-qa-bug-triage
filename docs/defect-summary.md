# Defect Summary

**Snapshot:** 16 October 2026 · **Source:** two screenshots of the application's bug list (34 records across two pages), with a subsequent user-confirmed status update for BUG-33. The application is the source of truth; this is a dated record, not a live tracker.

**Summary:** 34 recorded defects · 32 Closed (Fixed) · 1 Closed (Not a Bug) · 0 Open · 1 Triage.

| Bug ID | Title | Severity | Priority | Status | Resolution |
| --- | --- | --- | --- | --- | --- |
| BUG-1 | System allows duplicate project names | Moderate | Medium | Closed | Not a Bug |
| BUG-2 | Textareas contain leading whitespace when creating a new bug | Minor | Low | Closed | Fixed |
| BUG-3 | Bug IDs are not project-specific | Minor | Low | Closed | Fixed |
| BUG-4 | New project owner can see bugs from a deleted project | Major | High | Closed | Fixed |
| BUG-5 | POST /register returns HTTP 500 for passwords over bcrypt's 72-byte limit | Moderate | Medium | Closed | Fixed |
| BUG-6 | Project form feedback remains stale after correction, successful edit, cancel, or reopening | Minor | Low | Closed | Fixed |
| BUG-7 | Project edit accepts whitespace-only project name | Minor | Medium | Closed | Fixed |
| BUG-8 | No success confirmation is displayed after project creation | Minor | Low | Closed | Fixed |
| BUG-9 | Removing an assigned project member leaves bugs assigned to that user | Moderate | Medium | Closed | Fixed |
| BUG-10 | AI Assist button is visible to Developer on New Bug form | Moderate | High | Closed | Fixed |
| BUG-11 | Whitespace-only JWT_SECRET_KEY is accepted | Major | High | Closed | Fixed |
| BUG-12 | JWT security tests delete shared test database and cause order-dependent failures | Major | High | Closed | Fixed |
| BUG-13 | Multiline AI suggestion value changes when applied to a single-line bug field | Moderate | High | Closed | Fixed |
| BUG-14 | Late Create or Save response can discard a reopened bug form and newer AI suggestions | Moderate | High | Closed | Fixed |
| BUG-15 | Stale Create response can overwrite feedback in a newer bug form session | Moderate | High | Closed | Fixed |
| BUG-16 | Bug list refresh error is hidden after successful New Bug creation | Moderate | Medium | Closed | Fixed |
| BUG-17 | Delayed bug-list refresh can overwrite feedback from a newer New Bug session | Moderate | Medium | Closed | Fixed |
| BUG-18 | Bug list sorting resets to Last Updated after navigating away and returning | Minor | Low | Closed | Fixed |
| BUG-19 | POST /projects returns HTTP 500 when project name is not a string | Moderate | Medium | Closed | Fixed |
| BUG-20 | Lifecycle action buttons remain enabled when required selections are missing | Minor | Medium | Closed | Fixed |
| BUG-21 | Concurrent bug deletion can cause edit or status update to fail during response readback | Moderate | Medium | Closed | Fixed |
| BUG-22 | Bug action buttons shift vertically when feedback message appears | Minor | Low | Closed | Fixed |
| BUG-23 | Stale success messages persist across bug and member workflows | Minor | Medium | Closed | Fixed |
| BUG-24 | Fix Version is available when creating or editing unresolved bugs | Moderate | Medium | Closed | Fixed |
| BUG-25 | Lifecycle action controls move out of view after bug status transitions | Minor | Medium | Closed | Fixed |
| BUG-26 | Original text field does not expand to use available space beside a taller AI suggestion panel | Minor | Medium | Closed | Fixed |
| BUG-27 | Dropdown arrow color changes based on selected value | Minor | Low | Closed | Fixed |
| BUG-28 | Unexpected black background bar behind AI Priority suggestion "Urgent" | Minor | Medium | Closed | Fixed |
| BUG-29 | Incomplete horizontal dividers in bug details when Fix Version and Resolution are hidden | Minor | Low | Closed | Fixed |
| BUG-30 | Double turquoise border appears when focusing form fields | Minor | Low | Closed | Fixed |
| BUG-31 | WCAG 2.2 AA contrast failure for Blocker/Urgent text in dark theme | Major | High | Closed | Fixed |
| BUG-32 | Bug List table does not adapt to mobile viewport, requiring horizontal scrolling to access full bug information | Moderate | Medium | Closed | Fixed |
| BUG-33 | AI suggestion validation accepts conflicting duplicate JSON properties | Major | Medium | Closed | Fixed |
| BUG-34 | Success message overflows the viewport when creating a bug with an extremely long title | Minor | Low | Triage | — |

**Status note:** BUG-33 was shown as Open in the screenshots; the user subsequently confirmed closing it as Fixed. BUG-34 remains in Triage. Update this snapshot after future tracker changes.

**BUG-34 verification (19 October 2026):** a focused CSS correction and TC-378
browser regression passed at desktop and narrow viewports; see the
[execution evidence](test-execution.md#bug-34-success-confirmation-overflow--19-october-2026).
The user's current task confirms Affected Version `1.0.0-dev` and tracker status
Triage. Closure awaits review; no Fix Version has been assigned and no genuine
tracker record was accessed or changed by the agent.
