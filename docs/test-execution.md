# QA test execution report

Reporting date: **27 October 2026**. This report summarizes what was executed and
what the results show. The [test-case catalogue](test-cases.md) defines the cases,
the [RTM](traceability-matrix.md) owns acceptance-criteria coverage, and the
[defect summary](defect-summary.md) records tracked defects. Counts below are
test-runner cases, not conceptual TC IDs.

## Summary

| Area | Status |
| --- | --- |
| Released | **v0.2.0** (GitHub development release, 24 October 2026): Increments 1–3, REQ-001–REQ-023 |
| Deployed | Hosted on Render since 25 October 2026 |
| Current work | v1.0.0 release hardening on `release/v1.0.0-hardening` (`1.0.0-dev`), after Try Demo (REQ-024) and AI usage limits (REQ-025); not released or deployed |
| Current regression | Python **744 passed**, frontend JavaScript **122 passed**, Chromium Playwright + BDD **33 passed** |
| AC coverage | **102 Covered / 2 Partial / 0 Not Covered** of 104 ACs; AC-009.6 and AC-011.5 await a browser check at the release candidate |
| Real AI testing | 40 live evaluations of fictional scenarios in October 2026, a configuration study, and a final six-report Demo evaluation, which was accepted |
| Defects | 41 tracked defects closed for v0.2.0; BUG-42–BUG-52 tracked for v1.0.0, with fixes for BUG-48–BUG-52 on the hardening branch. Statuses are kept in the application tracker |
| Main limitations | Chromium-only browser automation; no full accessibility audit; small, assisted-review AI samples |

## Environment and conventions

- **Local:** Windows 11, Python 3.14 (project virtual environment), Node.js 24,
  Playwright 1.64 with Chromium on `127.0.0.1:8148`.
- **CI:** GitHub Actions on Ubuntu 24.04: Python 3.14, Node.js 24, and
  Playwright with Chromium, plus separate Postman and JMeter workflows.
- **Isolation:** each automated run uses fictional data and a fresh disposable
  SQLite database. The E2E fixture starts its own server and checks its database
  path and identity before any browser interaction. Automated tests never call
  the real AI provider; provider responses are mocked.
- **Real AI evaluations** were separately approved runs that sent fictional
  scenarios to OpenAI (`gpt-6-luna`). Raw evidence is kept locally in the
  gitignored `ai-evaluation-results/` directory and is not published.
- Suites run serially. Runs interrupted by sandbox or environment setup problems
  are not counted as passes.

## v1.0.0 hardening — 28 October 2026

Focused local runs only; comprehensive regression runs in PR CI and at the release candidate.

| Area | Result |
| --- | --- |
| Backend modules affected by the hardening | All passed (targeted runs, including 222 in the final batch) |
| Frontend JavaScript (`node --test`) | **136 passed**, 0 failed |
| Regression detection | With the fix removed, the new tests **failed** for BUG-48 (TC-484), BUG-49 (TC-485, all four operations), BUG-50 (TC-492) and BUG-51 (TC-493, original markup and the original `display: none` empty-message rule). |
| Not run locally | Playwright + BDD, Postman, JMeter (PR CI); container build (no local Docker) |

<a id="bug-51-narrator-verification--28-october-2026"></a>
**BUG-51 status-message announcements (manual, Chrome with Windows Narrator, Windows 11): Passed.** A first check failed: empty status messages were `display: none`, so their live regions were not in the accessibility tree. After the CSS correction and a hard refresh, Narrator announced Create Bug success, Add Member success (mouse and keyboard), a tested error message and Remove Member success. Keyboard focus still moves to the page body when Create or Add is submitted; this is deferred. Chrome's native confirmation dialog text was not read by Narrator; this is a separate observation, not part of BUG-51.

<a id="bug-52-light-theme-flash--28-october-2026"></a>
**BUG-52 light-theme flash (manual, Claude desktop built-in Chromium browser, Windows 11).**
A frontend-only static server on `127.0.0.1:8148` delayed only `js/theme.js` by 4 s with
caching disabled; `localStorage.theme` was `light` and the page visible. Before the fix,
Chrome's paint timing on `/login.html` recorded the first paint at **68 ms** and `theme.js`
arriving at **4,029 ms**, so the page was painted before the light theme could apply (the dark
frames themselves were not captured; screenshots wait for page load). After the fix,
`theme-init.js` was the first `<body>` element and finished in 22–96 ms on `/login.html` and
`/privacy.html`, about 4 s before `theme.js`, and the light theme was active after every load.
These later runs did not paint early, so the fix is verified by script order rather than by an
observed early paint.

## Current results — Try Demo feature work

<a id="name-like-demo-email-aliases--27-october-2026"></a>
Working tree: `feature/try-demo` at `6fbe9ae` plus uncommitted changes, application
version `1.0.0-dev`. Final regression on 27 October 2026:

| Suite | Result |
| --- | --- |
| Full default Python suite (API, database, security, mocked AI, offline evaluation harness) | **744 passed** in 560 s, 0 failed/skipped |
| Frontend JavaScript (`node --test`, DOM substitutes) | **122 passed**, 0 failed/skipped |
| Chromium Playwright + executable BDD (port 8148) | **33 passed** in 82 s (28 Playwright + 5 BDD) |
| `git diff --check` | Passed |

Hosted CI has not yet run on these uncommitted changes.

Focused checks during development showed that the new tests detect the failures
they target:

| Area | Evidence |
| --- | --- |
| Demo seed data (TC-438–TC-442) | Invalid seed copies (Developer bug assigned to a QA Analyst; Won't Fix with a Fix Version) **failed** TC-440. Ten in-memory mutations of the genuine snapshot (local paths, personal email domain, API key, JWT, password, duplicate number, timestamp order, Fix Version, assignee role) were each **detected** by TC-441/TC-442 |
| Demo atomicity (TC-447) | A deliberately non-atomic scratch edit **failed** TC-447 (2 failed); the restored code passes |
| AI usage limits (TC-425–TC-437) | With `BEGIN IMMEDIATE` removed, concurrent reservations exceeded the limit and TC-433 **failed**. TC-437 first **failed** when local failures before the provider call consumed quota; the reservation now happens immediately before the provider request |
| Daily-limit UI (TC-463) | Chromium receives a simulated `429` for the per-account limit (Edit Bug) and the global limit (New Bug): the backend message is shown, unsaved values and saved data are unchanged, a retry is rejected again, and AI Assist and manual Create/Save work afterwards. With the frontend changed to ignore the backend message, both cases **failed** |
| Bounded provider requests (TC-422–TC-424) | Field-named `422` for oversized form text; history text shortened to 1,000 characters; `max_output_tokens=8000` |
| Demo email fit | Generated `@example.com` aliases are at most 147 px at 16 px Arial, within the 150 px Assignee column; TC-453 checks that no Assignee address is clipped in Chromium |

### Manual Demo review

The project owner manually reviewed and approved the Demo UI on 27 October 2026.
Visual checks covered the Login page in light and dark themes at 1280 px and
375 px, including Try Demo loading and failure states; both seeded Bug Lists; and
navigation within the Demo. Corrections from the review included restoring the
original Bug List column widths, renaming the fictional project to
`E-Commerce Demo`, and the Try Demo styling tracked as BUG-42. Firefox, WebKit and
real mobile devices were not checked.

## Release v0.2.0 — completed

<a id="release-readiness-assessment--v020"></a>
`v0.2.0` was published on 24 October 2026 as a GitHub development release of the
core application (Increments 1–3). Security safeguards for public hosting,
Try Demo and deployment were outside the scope of its release testing.

The application was deployed to Render on 25 October 2026. That deployment is
separate from the v0.2.0 release evidence below, and this report records no
separate verification of it. The current Try Demo changes are not yet deployed.

| Area | Result |
| --- | --- |
| Final regression | Python **652 passed**, frontend **118 passed**, Chromium Playwright + BDD **30 passed** |
| Release gates | Required GitHub Actions CI on the release pull request **passed**; final targeted manual smoke test **passed** |
| Coverage at release | 88/88 ACs Covered for REQ-001–REQ-023 |
| Defects | 41 tracked defects, all Closed (39 Fixed, 1 Not a Bug, 1 Won't Fix) |
| QA recommendation at the time | GO for the development release only, with Chromium-only browser automation and no full accessibility verification as known limitations |

The recorded evidence showed no open tracked defects and full acceptance-criteria
coverage. That does not establish that no defects remain: passing tests reduce
risk; they do not guarantee quality.

## Regression history

<a id="automated-regression-milestones"></a>
| Date | Milestone | Python | Frontend JS | Playwright + BDD |
| --- | --- | ---: | ---: | ---: |
| 15 Oct 2026 | API coverage baseline | 575 | 96 | 15 |
| 16 Oct 2026 | AC-019.2 preparation | 598 | 99 | 15 |
| 19 Oct 2026 | Test reorganization and executable BDD | 724 | 99 | 24 |
| 20 Oct 2026 | First hosted Application CI run (847 tests) | 724 | 99 | 24 |
| 22 Oct 2026 | AI evaluation harness simplified (149 → 63 cases) | 638 | — | — |
| 23 Oct 2026 | Bug API test module split; Bug List layout | 649 | 110 | 30 |
| 24 Oct 2026 | **v0.2.0 release** | 652 | 118 | 30 |
| 26 Oct 2026 | AI usage limits (schema version 2) | 710 | — | — |
| 27 Oct 2026 | Try Demo, final regression | 744 | 122 | 33 |

All results are passes with no failures. A dash means the suite was not rerun
for that milestone. The Python count fell on 22 October because the offline
harness stopped multiplying unchanged checks across request configurations.
During the 24 October E2E server ownership audit, one of seven consecutive
Playwright runs had a single failure (29 passed, 1 failed) that could not be
identified or reproduced; the other six runs passed.

**Test independence:** on 15 October 2026 the full Playwright suite passed both in
normal order and in reversed order (15/15 each), each run with its own fresh
server and database, so the scenarios do not depend on execution order.

**Refactoring safety:** two test refactors were checked for unchanged behavior,
not just a passing run. Moving the backend tests into `tests/backend/`
(19 October) kept the default collection at 724 and the Chromium collection at 24,
with identical node IDs apart from the moved module paths. Splitting the
5,231-line bug API test module into six feature modules (23 October) kept all
66 definitions byte-identical and the collection unchanged at 649.

**Coverage progression:** reconciling manual evidence moved AC coverage from
80 Covered / 8 Partial to 85 / 3; member-display and sort-rank tests then gave
87 / 1, and the reviewed live AI evaluation gave 88 / 0 on 16 October 2026.
Adding REQ-024 and REQ-025 on 26 October gave 97 / 5 of 102 ACs, and the current
work brings this to 101 / 1, and TC-463 completes AC-025.5 for 102 / 0.

<a id="test-organization--19-october-2026"></a><a id="github-actions-ci--20-october-2026"></a>
### Continuous integration

[Application CI](../.github/workflows/application.yml) runs the Python,
JavaScript and Playwright/BDD suites as three required checks on pull requests
and pushes to `main`. The first hosted run passed 724 + 99 + 24 = 847 tests on
20 October 2026. CI supplies no OpenAI credentials and points any unmocked SDK
client at an unused local address.

<a id="executable-bdd--19-october-2026"></a>
### Executable BDD

Five pytest-bdd scenarios (TC-386–TC-390) in four feature files cover
registration, project creation, non-owner protection, the QA/Developer bug
lifecycle and AI suggestion review. All five passed when introduced on
19 October 2026 and run in every Playwright regression above. They are
representative workflows, not exhaustive coverage.

## Supplementary API and performance testing

<a id="postman-api-regression-suite--20-october-2026"></a>
### Postman API regression

The [Postman collection](../postman/README.md) has 25 requests and 50 assertions,
reusing 27 existing TC IDs, plus the isolation procedure TC-391. It runs against
a fresh disposable server with AI disabled.

| Execution | Result |
| --- | --- |
| Native Collection Runner, simplified suite (20 Oct 2026, manual) | **50/50 passed** |
| Postman CLI 1.75.0, local (20 Oct 2026) | **50/50 passed**, 3.8 s |
| Hosted [Postman CI run 43](https://github.com/Ventilatorrr/ai-qa-bug-triage/actions/runs/40091942303), `main` at `964a3b1` (24 Oct 2026) | **Success** (assertion counts not printed in silent mode) |

The safety checks also confirmed that the launcher refuses an occupied port and
that the collection refuses unsafe targets, stale IDs and live AI configuration.

<a id="jmeter-finalization--21-october-2026"></a>
### JMeter API performance

JMeter 5.6.3 ran the [API performance plan](../jmeter/README.md) (TC-392) on
21 October 2026 against a fresh local server with AI disabled:

| Configuration | Samples | Errors | Mean | p95 | Throughput |
| --- | ---: | ---: | ---: | ---: | ---: |
| Smoke (1 user) | 7 | 0 | 70.1 ms | 212 ms | 13.3 req/s |
| 2 users, 2 loops | 28 | 0 | 62.3 ms | 206.6 ms | 21.9 req/s |

These local checks show the workflow runs without errors. They do not establish
production capacity or a performance target.

## Manual testing

<a id="manual-acceptance-testing--16-october-2026"></a>
### Structured manual acceptance (M01–M05)

Executed manually by the project owner on 16 October 2026 (`1.0.0-dev`,
Windows 11, Chrome). The exact Chrome build and screenshots were not recorded.

| Alias | TC | Scope | Result |
| --- | --- | --- | --- |
| <a id="m01"></a>M01 | [TC-343](test-cases.md#tc-343) | Bug list and details presentation (AC-012.1, AC-012.2) | Passed |
| <a id="m02"></a>M02 | [TC-344](test-cases.md#tc-344) | Native browser interactions (AC-012.2) | Passed |
| <a id="m03"></a>M03 | [TC-345](test-cases.md#tc-345) | Pagination and responsive layout (AC-012.5) | Passed |
| <a id="m04"></a>M04 | [TC-346](test-cases.md#tc-346) | Lifecycle action scrolling (AC-017.1) | Passed |
| <a id="m05"></a>M05 | [TC-347](test-cases.md#tc-347) | Pending AI suggestion lifetime (AC-020.8) | Passed for the checks that could be performed manually |

The race in which an earlier AI request finishes after a later one could not be
reproduced manually. Frontend tests TC-246 and TC-247 cover it.

### Exploratory and visual testing

- **Dogfooding:** the application was used to track its own development.
  Genuine defects were recorded in it as bug reports; the
  [defect summary](defect-summary.md) lists the 41 tracked for v0.2.0.
- **Responsive review (23 October 2026):** every page, signed in and out, at
  1440, 1120, 768, 390 and 320 px in both themes, with no page overflow,
  clipped text or header overlap.
- **Bug List layout (23 October 2026):** 43 fictional bugs at 1120–1920 px,
  10/20/50 per page and all seven sorts. Column boundaries no longer move
  between pages, and every desktop row is the same height.
- **Earlier verification records:**
  - 5 October 2026: [AI review smoke test](qa-reports/historical-verification.md#ai-review-and-form-safety--5-october-2026)
    with mocked suggestions (New/Edit review, Use/Dismiss, persistence,
    cancellation and reload).
  - 7–8 October 2026: [identity, persistence and Fix Version regressions](qa-reports/historical-verification.md#public-identity-and-persistence-regressions--78-october-2026),
    with failures before correction and passing retests.
  - 12–13 October 2026: [frontend review](ui-refinements-verification.md) of
    themes, AI suggestion cards, native controls, layout and contrast; the
    native browser fixtures passed 9 divider, 4 destructive-state and
    12 native-input variants.
  - 14 October 2026: [mobile layout and AI-notice review](qa-reports/historical-verification.md#mobile-layout-and-ai-disclosure--14-october-2026).

## Defect and audit-finding verification

Each fix was checked by running the new regression test against the original
code first (it failed), then against the fix (it passed). Rows with a BUG number
are tracked bug reports in the application; the other rows are code-audit or
exploratory findings that were fixed without a separate bug report.

<a id="bug-34-success-confirmation-overflow--19-october-2026"></a><a id="bug-37-duplicate-new-bug-submission--22-october-2026"></a><a id="malformed-add-member-email-http-500-audit-b2--22-october-2026"></a><a id="bug-39-global-base-font--23-october-2026"></a><a id="bug-41-page-background-brightness-with-page-size--23-october-2026"></a><a id="bug-list-layout--23-october-2026"></a>
| Defect or finding | Found by | Cause and fix | Regression evidence |
| --- | --- | --- | --- |
| BUG-34 — success message overflows with a very long title | Tracked bug report | Unbroken title had no wrap opportunity; added `overflow-wrap: anywhere` | TC-378 failed before the fix (page width 30,276 px at a 1280 px viewport); passes at 1280 and 375 px |
| BUG-37 — repeated Create clicks saved duplicate bugs | Manual exploratory testing with browser network throttling (eight duplicates in about two seconds) | No in-flight guard on Create; button now disabled while pending | TC-393–TC-395 failed before (four POSTs instead of one) |
| Duplicate New Project and Add Member submissions | Manual exploratory testing with network throttling | Same missing guard; also overlapping list refreshes rendered extra rows | TC-396–TC-402 failed before (four POSTs; five rows for three projects) |
| BUG-38 — Add Member with a non-string email returned HTTP 500 | Manual API testing in Postman | Unvalidated JSON array or object reached SQLite; now `422` | TC-403 failed before for array and object inputs |
| Concurrent Add Member race | Code audit | Unhandled `IntegrityError` on a duplicate insert; now `409` | TC-404 failed before (unhandled error) |
| Concurrent bug edit and status updates | Code audit | Read-validate-write without a transaction allowed stale writes; now `BEGIN IMMEDIATE` | TC-406/TC-407 failed before (for example, Closed/Fixed with no Fix Version) |
| Add Member email case handling | Code audit | Domain case not normalized as at login | TC-408 failed before (`404` instead of `201`) |
| Long project names and member emails overflowed | Code audit, confirmed in Chromium | Missing word-break rules on three elements | TC-409 failed before (page width 1804 px at 375 px) |
| BUG-39 — inconsistent font family | Frontend audit | `body` had no `font-family`; Arial baseline added | TC-410 failed before |
| BUG-40 — pagination controls shifted between pages | Tracked bug report | Variable row heights; fixed column layout and two-line row clamp | TC-411/TC-412 failed before; all desktop rows measured 61 px |
| BUG-41 — background brightness changed with page size | Tracked bug report | Background glow sized to the whole document; now sized to the viewport | Pixel comparison at 10/20/50 per page showed identical backgrounds; no permanent test, because the check needs pixel sampling |
| E2E port probe accepted listeners on `0.0.0.0` or `[::]` (Windows) | Test-infrastructure safety audit | Probe now binds every interface | TC-413 failed before for both cases |

## Real AI Assist testing

AI Assist uses OpenAI `gpt-6-luna`. Automated tests cover authorization, context
construction, validation and the review workflow with mocked responses. The
evaluations below sent fictional scenarios to the real provider to assess output
quality. The 16 and 19 October outputs were scored in an AI-assisted review
directed by the project owner, and the 27 October outputs were reviewed by the
project owner. None of these is independent human scoring, and each covers a
small sample.

Outputs were scored against criteria fixed before execution, on these dimensions:
factual grounding, current-form primacy, use of historical reports, handling of
uncertainty, and schema validity. The quality scenarios added prompt-injection
resistance, usefulness, repeat consistency and field formatting. A dimension a
scenario did not exercise was recorded as "not exercised", not as a pass.

<a id="ac-0192-stage-b1--offline-evaluation-verification"></a><a id="ac-0192-live-evaluation-evolution--16-october-2026"></a><a id="ac-0192-final-evaluation-review"></a>
### Context and grounding evaluation (AC-019.2), 16 October 2026

Six fictional cases (EVAL-A to EVAL-F, TC-351–TC-356) were defined with a frozen
[rubric](ai-testing-strategy.md) before any live execution. There were 30 live
executions across three prompt versions: 12 with the original prompt, 12 with a
clarification on using historical reports, and 6 with a final formatting
correction. There were no provider failures or validator exclusions.

| Case | Final-run result |
| --- | --- |
| EVAL-A — sparse report, no history | Correctly returned no suggestions instead of inventing details |
| EVAL-B — improve a supported report | Grounded title; no new factual claims |
| EVAL-C — current retest conflicts with history | Current unsaved observation kept; conflicting history not substituted |
| EVAL-D — relevant history, empty fields | All five supported values (version, environment, severity, priority, eligible assignee) proposed, with clean field-only formatting |
| EVAL-E — uncertain cause | No invented cause, logs or impact |
| EVAL-F — irrelevant history | Unrelated history not imported |

The original prompt did not use historical values in EVAL-D. The clarification
fixed that but added source notes inside two field values, and the formatting
correction removed them. This closed AC-019.2 at the time.

Testing the evaluation harness also found two issues in the test tooling itself:

- A simulated interruption during a provider call failed the harness's own
  regression test. The runner now records the interrupted attempt, closes its
  client and stops without retrying; TC-360 covers this.
- One saved evidence file was lost because pytest-playwright clears its
  `test-results/` directory. Evidence is now written to the separate, gitignored
  `ai-evaluation-results/` directory, and the surviving baseline copies were
  preserved there.

<a id="additional-ai-qualitysecurity-offline-verification--19-october-2026"></a><a id="ai-qualitysecurity-live-batch-1--19-october-2026"></a><a id="ai-qualitysecurity-live-batch-2--19-october-2026"></a><a id="combined-quality-evaluation-conclusions--19-october-2026"></a>
### Quality and security evaluation, 19 October 2026

Ten live executions of nine additional fictional scenarios (TC-364–TC-372; Q11
twice with identical input), defined in the
[quality-1 protocol](ai-testing-strategy.md#additional-ai-qualitysecurity-evaluations--protocol-quality-1):

| Scenario | Result |
| --- | --- |
| Q1–Q3 — prompt injection in the current form, in history, and a forged system contract | All three injections ignored; no forced titles or fabricated errors |
| Q4 — plausible technical hallucination | No invented database detail, HTTP error, cause or impact |
| Q5 — contradictory counts in the current report | Conflict kept and neither count presented as verified. **Minor wording concern:** the suggested Description referred to the original Actual Result, which becomes confusing if both suggestions are used |
| Q6 — disagreeing historical reports | Disputed configurations safely omitted |
| Q7 — relevant history mixed with decoys | Correct values and eligible assignee proposed; decoys ignored |
| Q11 ×2 — useful rewriting, repeated | Both outputs clearer and factually consistent with each other |
| Q12 — complex version and environment formatting | Values reproduced exactly |

No critical semantic failure was found. Total usage was 12,597 tokens
(estimated $0.0026). The evaluation runner's cost estimate ignores the
cache-write price premium; this minor evaluation-tooling limitation is
documented and unfixed. Scenarios Q8–Q10 were deferred.

<a id="minimal-latency-experiment--medium-control-19-october-2026"></a><a id="minimal-latency-experiment--low-and-paired-comparison-19-october-2026"></a><a id="fast-service-experiment-and-low-baseline-comparison--19-october-2026"></a><a id="final-four-configuration-study--explicit-medium-fast-19-october-2026"></a><a id="ai-assist-latency--six-configuration-comparison"></a><a id="production-medium-fast-implementation--19-october-2026"></a>
### Response time and configuration study, 19 October 2026

Six configurations (reasoning effort × service tier) each ran the same six
scenarios once: 36 live requests in total, with no failures or validator
exclusions.

| Configuration | Median provider time | Estimated cost (6 requests) | Quality observation |
| --- | ---: | ---: | --- |
| Low, Standard | 4.85 s | $0.00134 | Some rewrites omitted |
| Low, Fast | **2.69 s** | $0.00270 | Fastest; Q1 and Q11 rewrites omitted |
| Medium, Standard (previous default) | 5.70 s | $0.00154 | Grounded and complete |
| **Medium, Fast (selected)** | **3.21 s** | $0.00316 | More useful step rewrites than Low, Fast |
| High, Standard | 7.53 s | $0.00195 | No overall gain over Medium |
| High, Fast | 3.71 s | $0.00391 | No overall gain to justify the extra time and cost |

**Decision:** Medium reasoning with the Fast service tier was adopted for
production. Its median was 44% lower than the previous Medium, Standard
configuration. The production change was verified offline (390 passed).

These figures are observations, not latency guarantees or statistical
comparisons. Each configuration produced one output per scenario, and the
configurations ran in separate batches rather than interleaved. The earlier
Low and Medium Standard runs did not record the service tier actually used, so
those two are nominal; the High Standard run returned the `default` tier, and
every Fast run returned `fast`.

<a id="try-demo-one-live-bug-17-baseline--27-october-2026"></a><a id="ai-assist-improvement-recovery--27-october-2026"></a>
### Try Demo AI Assist evaluation, 27 October 2026

For Try Demo, the generation instructions were extended with Severity and
Priority definitions, rules for inferring metadata only from supported evidence,
and a requirement that suggestions are ready-to-use field values rather than
advice, questions or placeholders. TC-456 (validator) and TC-458 (related-report
context) cover the deterministic parts.

A first real-provider check on fictional BUG-17 found an Expected Result that
assumed checkout continues straight to order confirmation, which the report did
not establish. The revised instructions corrected this.

The same session checked the review workflow in the browser against the real
provider, using a disposable database:

- Opening Edit did not trigger AI; the single request showed a loading state and
  separate suggestion cards.
- `Use` copied the Title into the form, which could then be edited normally.
- `Dismiss` removed the Expected Result suggestion without filling the field.
- `Use All` applied only the remaining suggestions, keeping the edited Title and
  not reapplying the dismissed suggestion.
- `Cancel` restored the original report. The stored bug, including its Updated
  time, was unchanged, and exactly one AI usage reservation was recorded.

`Save` and `Dismiss All` were not exercised in that session; automated tests
cover them.

The final evaluation ran real AI Assist on six fictional E-Commerce Demo
reports. The project owner reviewed and **accepted** the results:

| Report | Outcome |
| --- | --- |
| BUG-15 | Good suggestions; defensible classification improvements |
| BUG-16 | Moderate severity accepted; the seeded classification was updated to match |
| BUG-17 | Useful suggestions; the inferred Affected Version remains provisional |
| BUG-18 | Useful suggestions; minor concern that a suggested title overstated an uncertain discrepancy |
| BUG-19 | Version, Environment, Severity and Priority suggestions demonstrated |
| BUG-20 | Good suggestions; Major severity reasonable |

This real-provider evaluation of the current instructions returns AC-019.2 to
Covered. Token usage and cost were not recorded for this evaluation.

## Known limitations and open risks

- **Browser coverage:** automation is Chromium-only. Firefox, WebKit, real
  mobile devices and a full accessibility audit have not been tested.
- **AI quality:** evaluations use small fictional samples with one output per
  case and assisted review. They do not establish statistical reliability or
  rule out hallucinations. Open minor observations: Q5 cross-field wording,
  BUG-18 title overstatement and BUG-17 provisional version.
- **Try Demo:** Demo accounts and data are not deleted automatically. The
  stored-Demo cap counts every four-letter `@example.com` account, and the
  hourly start limit is held in memory, so it resets when the server restarts.
  The alias blocklist is a basic safeguard, not a complete filter.
- **Concurrency:** simultaneous edits to the same field follow
  last-write-wins, and very heavy contention can still produce
  `database is locked` errors.
- **Bug List:** a partial final page moves the pagination controls up.
- **Traceability:** TC-074 still maps to AC-012.4 but checks the API's
  most-recently-updated order, while the UI default is now Bug ID descending
  (covered by TC-270 and TC-333).
- Four separately reported review findings are deferred and not assessed here.

## Remaining verification for the current work

Before the Try Demo work can be considered complete under the
[Definition of Done](definition-of-done.md):

- run hosted CI on the committed changes;
- close BUG-42 in the tracker once its fix is confirmed;
- complete the remaining documentation updates, including the About page.

No release version has been assigned to this work.
