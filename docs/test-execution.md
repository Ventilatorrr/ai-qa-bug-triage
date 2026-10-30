# QA test execution report

Reporting date: **30 October 2026**. This report summarizes what was executed and
what the results show. The [test-case catalogue](test-cases.md) defines the cases,
the [RTM](traceability-matrix.md) owns acceptance-criteria coverage, and the
[defect summary](defect-summary.md) records tracked defects. Counts below are
test-runner results, not conceptual TC IDs; collection counts (tests discovered,
not run) are labelled as such.

## Summary

| Area | Status |
| --- | --- |
| Released | **v0.2.0** (GitHub development release, 24 October 2026): Increments 1–3, REQ-001–REQ-023 |
| Deployed | v0.2.0 development deployment on Render since 25 October 2026, currently suspended; `v1.0.0-rc.1` on Render staging since 30 October 2026. v1.0.0 is not deployed to production |
| Release candidate | `v1.0.0-rc.1` at `22af3b3` (`APP_VERSION` 1.0.0), with Try Demo (REQ-024), AI usage limits (REQ-025) and the v1.0.0 release hardening. v1.0.0 is not publicly released |
| Latest full local regression | 30 October 2026, release candidate: Python **829 passed** (backend 766, offline AI evaluation 63), frontend JavaScript **138 passed**, Chromium Playwright + BDD full suite passed (count not recorded), Postman **50/50** assertions, JMeter 0 errors. See [release-candidate verification](#v100-release-candidate-verification--30-october-2026) |
| Pull request CI | All five required checks passed on the release-candidate pull request #90 and its merge commit. CI runs for the earlier pull requests #84 and #85 are not recorded here; the release-candidate runs cover the merged code |
| Release-candidate checks | Staging verification **passed** on 30 October 2026. Production deployment, production smoke testing and the final Go/No-Go decision are pending (see [pending release verification](#pending-release-verification)) |
| AC coverage | **109 Covered / 0 Partial / 0 Not Covered** of 109 ACs. This assesses test evidence for each AC; it does not by itself establish release readiness |
| Defects | 54 tracked defects in the [defect summary](defect-summary.md) (28 October 2026 snapshot, plus BUG-54 on 29 October), all Closed: 39 fixed in v0.1.0–v0.2.0, 13 fixed for the planned v1.0.0 (including BUG-54), and 2 closed without a fix |
| Main limitations | Chromium-only browser automation; no full accessibility audit; small, assisted-review AI samples |

## Environment and conventions

- **Local:** Windows 11, Python 3.14 (project virtual environment), Node.js 24,
  Playwright 1.64 with Chromium on `127.0.0.1:8148`.
- **CI:** GitHub Actions on Ubuntu 24.04: Python 3.14, Node.js 24, and
  Playwright with Chromium, plus separate Postman and JMeter workflows.
- **Isolation:** automated tests use fictional data. Backend tests use a fresh
  temporary SQLite database for each test. Each Playwright run starts its own
  server with a new temporary database and checks its path and identity before
  any browser interaction. Node frontend tests use DOM substitutes, and the
  offline AI evaluation harness uses no application database. Automated tests
  never call the real AI provider; provider responses are mocked.
- **Real AI evaluations** were separately approved runs that sent fictional
  scenarios to OpenAI (`gpt-6-luna`). Raw evidence is kept locally in the
  gitignored `ai-evaluation-results/` directory and is not published.
- Suites run serially. Runs interrupted by sandbox or environment setup problems
  are not counted as passes.

## v1.0.0 release-candidate verification — 30 October 2026

| Item | Value |
| --- | --- |
| Git tag | `v1.0.0-rc.1` |
| Commit | `22af3b38b924173f3cb0e765a9b3ffc2f497c1e7` (merge of pull request #90; `APP_VERSION` 1.0.0) |
| Image | `ghcr.io/ventilatorrr/ai-qa-bug-triage@sha256:521487fab6b59b20c1aafbfad4ef1a8b4a7993a16479ff8ecca1d18bc60a3bef` (tag `1.0.0-rc.1`) |

**Automated verification.** The hosted runs are tied to the exact commits shown. The local
records do not name the commit tested.

| Check | Result |
| --- | --- |
| Local regression (serial, disposable databases, no real OpenAI calls) | Backend pytest **766 passed** in 529.61 s; offline AI evaluation **63 passed** in 10.92 s; frontend JavaScript **138 passed**; Chromium Playwright + BDD full suite passed (count not recorded), plus 2 tests in a separate headed run. Postman CLI: 25 requests, **50/50** assertions in 4.3 s. JMeter: smoke 7, small load 28 and timed load 335 samples, 0 errors. A first JMeter attempt failed because no server was listening; that setup failure is not counted |
| Required checks on pull request #90 (`24458b5`) | **Passed:** [Application CI run 76](https://github.com/Ventilatorrr/ai-qa-bug-triage/actions/runs/41045547126) (Python, Frontend JavaScript, Playwright and BDD jobs), [Postman CI run 83](https://github.com/Ventilatorrr/ai-qa-bug-triage/actions/runs/41045547264), [JMeter CI run 77](https://github.com/Ventilatorrr/ai-qa-bug-triage/actions/runs/41045547232) |
| Required checks on the merge commit (`22af3b3`, push to `main`) | **Passed:** [Application CI run 77](https://github.com/Ventilatorrr/ai-qa-bug-triage/actions/runs/41048019000), [Postman CI run 84](https://github.com/Ventilatorrr/ai-qa-bug-triage/actions/runs/41048019018), [JMeter CI run 78](https://github.com/Ventilatorrr/ai-qa-bug-triage/actions/runs/41048019066) |
| Release image | **Passed:** [Release image run 1](https://github.com/Ventilatorrr/ai-qa-bug-triage/actions/runs/41063245078) confirmed the commit, built the image, smoke-tested the container and published it to GHCR. The registry returns the digest above for tag `1.0.0-rc.1` |

**Render staging (manual, project owner).** The project owner performed and reported these
checks; they are not independently verified automated results.

| Check | Result |
| --- | --- |
| Deployment | Successful in Frankfurt (EU Central), with the SQLite database on the persistent disk at `/var/data` |
| [Smoke checklist](release-runbook.md#5-smoke-checklist-staging-then-production) | Manual smoke testing passed |
| AI Assist | Real provider requests succeeded, including classification suggestions (see the observation below) |
| Restart | Data persisted after a Render service restart |
| `python -m app.admin status` | Expected database path; no expired Demos |
| Security headers | `X-Frame-Options: DENY` and `X-Content-Type-Options: nosniff` present |
| HSTS | `Strict-Transport-Security` absent; Render provides HTTPS redirection. Accepted as a non-blocking hardening observation |

**AI classification observation (quality, not a confirmed defect).** For an unusable
application with no workaround and no stated affected-user scope, AI Assist suggested
Blocker severity / Medium priority; adding "Affects all users" gave Blocker / Urgent, and a
separate scenario affecting one user gave Medium priority. Priority suggestions are sensitive
to the stated impact and scope, and Medium may underestimate urgency when scope is
unspecified. Non-blocking for v1.0.0, because suggestions require human review before they
are used; further AI evaluation is deferred.

Six live AI evaluation attempts also ran locally on 30 October. Their outputs have not been
semantically reviewed, so they are not reported as quality results.

**Staging verification: Passed.** This is not a public release or a production Go decision;
the remaining steps are listed under [pending release verification](#pending-release-verification).

## v1.0.0 development verification

<a id="name-like-demo-email-aliases--27-october-2026"></a>
### Try Demo and AI usage limits — 27 October 2026

Final local regression of the Try Demo work (`1.0.0-dev`, before merging):

| Suite | Result |
| --- | --- |
| Full default Python suite (API, database, security, mocked AI, offline evaluation harness) | **744 passed** in 560 s, 0 failed/skipped |
| Frontend JavaScript (`node --test`, DOM substitutes) | **122 passed**, 0 failed/skipped |
| Chromium Playwright + executable BDD (port 8148) | **33 passed** in 82 s (28 Playwright + 5 BDD) |

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

**Manual Demo review.** The project owner manually reviewed and approved the Demo UI on 27 October 2026.
Visual checks covered the Login page in light and dark themes at 1280 px and
375 px, including Try Demo loading and failure states; both seeded Bug Lists; and
navigation within the Demo. Corrections from the review included restoring the
original Bug List column widths, renaming the fictional project to
`E-Commerce Demo`, and the Try Demo styling tracked as BUG-42. Firefox, WebKit and
real mobile devices were not checked.

### Release hardening — 28 October 2026

Focused local runs only; the full suites run in pull request CI and at the release candidate.

| Area | Result |
| --- | --- |
| Backend modules affected by the hardening | All passed (targeted runs, including 222 in the final batch) |
| Frontend JavaScript (`node --test`) | **136 passed**, 0 failed |
| Regression detection | With the fix removed, the new tests **failed** for BUG-48 (TC-484), BUG-49 (TC-485, all four operations), BUG-50 (TC-492) and BUG-51 (TC-493, original markup and the original `display: none` empty-message rule). |
| Not run locally | Playwright + BDD, Postman, JMeter (pull request CI); container build (no local Docker) |

<a id="bug-51-narrator-verification--28-october-2026"></a>
**BUG-51 status-message announcements (manual, Chrome with Windows Narrator, Windows 11): Passed.** A first check failed: empty status messages were `display: none`, so their live regions were not in the accessibility tree. After the CSS correction and a hard refresh, Narrator announced Create Bug success, Add Member success (mouse and keyboard), a tested error message and Remove Member success. Keyboard focus still moves to the page body when Create or Add is submitted; this is deferred. Chrome's native confirmation dialog text was not read by Narrator; this is a separate observation, not part of BUG-51.

<a id="bug-53-ac-0115-limit-feedback--28-october-2026"></a>
**BUG-53 and AC-011.5 length-limit feedback (manual, project owner): Passed.** New Bug: a 256-character title was rejected and its error appeared beside Create without scrolling. Edit Bug: a 256-character title was rejected, the error was visible beside Save, and the original title was unchanged after refreshing. The 255/256-character boundary is also automated: API create and edit (TC-478), New Bug error placement and messages (TC-494), and Chromium (TC-496: 256 rejected beside Create, 255 created). Local targeted runs on `fix/bug-53-new-bug-error-placement`: frontend JavaScript 138 passed; Playwright Bug and AI Assist modules 15 passed. TC-497 then verified, in a disposable test database, that a stored over-limit value is kept while another field is edited and validated only when that field is changed (`test_input_limits.py`: 17 passed), so AC-011.5 is now Covered.

<a id="ac-0096-leave-project--28-october-2026"></a>
**AC-009.6 Leave Project (manual, non-owner project member, disposable test project): Passed.** Signed in as a project member (QA Analyst/Developer), opened the project, chose Leave Project and confirmed; the browser returned to My Projects with a success message, the project no longer appeared in the list, and direct access through the previous project URL was denied. Automated coverage: TC-486 (API), TC-487 and TC-488 (frontend), TC-331 (Chromium).

<a id="bug-52-light-theme-flash--28-october-2026"></a>
**BUG-52 light-theme flash (manual, built-in Chromium browser of the development environment, Windows 11).**
A frontend-only static server on `127.0.0.1:8148` delayed only `js/theme.js` by 4 s with
caching disabled; `localStorage.theme` was `light` and the page visible. Before the fix,
Chromium's paint timing on `/login.html` recorded the first paint at **68 ms** and `theme.js`
arriving at **4,029 ms**, so the page was painted before the light theme could apply (the dark
frames themselves were not captured; screenshots wait for page load). After the fix,
`theme-init.js` was the first `<body>` element and finished in 22–96 ms on `/login.html` and
`/privacy.html`, about 4 s before `theme.js`, and the light theme was active after every load.
These later runs did not paint early, so the fix is verified by script order rather than by an
observed early paint.

### Data retention and account deletion — 29 October 2026

Focused local runs against disposable test databases during the change, followed by the
full local regression recorded in [regression history](#regression-history).

| Area | Result |
| --- | --- |
| BUG-54 reproduction | TC-498 against the unchanged code: **3 failed, 1 passed**. Adding another Demo's teammate or an ordinary account to a Demo project, and a Demo account to an ordinary project, returned 201 instead of 404 |
| Backend modules affected by the change (16 modules) | **222 passed**, 0 failed |
| Frontend JavaScript (`try-demo`, `ai-disclosure`) | **14 passed**, 0 failed; `try-demo` **4 passed** again after the final Login notice wording |
| Five-account safeguard (TC-509) | Before it, both variants failed. An extra account record let cleanup delete an ordinary account and its project with the Demo. A missing record deleted nothing, because the unrecorded teammate's membership already blocked cleanup; that variant failed only because the logged reason was not the account count. After it, `test_demo_retention.py` **11 passed** |
| Not run locally | JMeter (pull request CI); the operator commands in Render Shell on a deployment |

### Authorization race fixes — 29 October 2026

An independent pre-release review of Try Demo found two authorization race conditions
after the full local regression above; both were fixed and verified with targeted runs
against disposable databases and the offline AI provider (no real OpenAI calls).

| Area | Result |
| --- | --- |
| Bug update responses (TC-510) | Edit Bug and Update Status read their response after commit, so a project deleted and recreated with the same id returned another user's report (HTTP 200). The response is now read inside the write transaction. TC-510 **2 failed** before the fix, **2 passed** after |
| AI Assist context (TC-511) | Authorization and context reads used separate connections, so a recreated project's reports and members reached the offline provider. They now share one read transaction, closed before the provider call; assignee validation after generation accepts only members of that snapshot. TC-511 **2 failed** before the fix, **2 passed** after |
| Updated technical cases (TC-139, TC-140) | Now verify that the response is captured before commit, and that a project deleted right after a successful update still gets the retained response (200) while a later GET returns 404 |
| New and updated tests | `test_bug_id_reuse_races.py` and `test_bug_update_readback.py`: **12 passed**; the four new cases also passed three repeated runs |
| Related modules (22: all AI, bug and project backend modules, fix version, input limits, Demo seed, offline AI evaluation) | **694 passed**, 0 failed, in 9 min 0 s. The backend suite now collects 764 tests |
| Not run after the fixes | Full backend, frontend, Playwright + BDD and Postman suites (no frontend change; pull request CI runs all suites) |

### AI context data minimisation and Privacy Policy — 29 October 2026

AI Assist now sends eligible members' user IDs and roles to the provider, without their email
addresses; assignee validation still uses the same IDs. Oxanium is self-hosted, so pages make no
Google Fonts requests. Runs used disposable databases and the offline AI provider.

| Area | Result |
| --- | --- |
| Member emails not sent (TC-512) | **2 failed** with the previous serialization, **2 passed** after |
| AI backend modules (`test_ai_*.py`), `test_bug_id_reuse_races.py`, `test_privacy.py`, offline AI evaluation | First run: **401 passed**, 4 failed (evaluation tests still expected fixture emails on the wire); after updating those assertions, offline AI evaluation **63 passed** |
| Frontend JavaScript (`base-typography`, `ai-disclosure`, `ai-assist`) | **34 passed**, 0 failed |
| Self-hosted Oxanium | Static server on 127.0.0.1:8148 (no backend or database): 400 and 700 load from `/assets/fonts/oxanium/`; Project, Bug and Privacy pages make no external requests |
| Not run | Full backend, Playwright + BDD, Postman and JMeter suites (pull request CI) |

## Release v0.2.0 — completed

<a id="release-readiness-assessment--v020"></a>
`v0.2.0` was published on 24 October 2026 as a GitHub development release of the
core application (Increments 1–3). Security safeguards for public hosting,
Try Demo and deployment were outside the scope of its release testing.

The application was deployed to Render on 25 October 2026. That deployment is
separate from the v0.2.0 release evidence below, and this report records no
separate verification of it.

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
| 10 Sep 2026 | Member-removal timestamp fix | 148 | — | — |
| 7–8 Oct 2026 | Project-local bug numbers | 510 | 76 | — |
| 7–8 Oct 2026 | Fix Version lifecycle correction | 544 | 77 | — |
| 13 Oct 2026 | Frontend theme and control review | 544 | 80 | — |
| 15 Oct 2026 | API coverage baseline | 575 | 96 | 15 |
| 16 Oct 2026 | AC-019.2 preparation | 598 | 99 | 15 |
| 19 Oct 2026 | Test reorganization and executable BDD | 724 | 99 | 24 |
| 20 Oct 2026 | First hosted Application CI run (847 tests) | 724 | 99 | 24 |
| 22 Oct 2026 | AI evaluation harness simplified (149 → 63 cases) | 638 | — | — |
| 23 Oct 2026 | Bug API test module split; Bug List layout | 649 | 110 | 30 |
| 24 Oct 2026 | **v0.2.0 release** | 652 | 118 | 30 |
| 26 Oct 2026 | AI usage limits (schema version 2) | 710 | — | — |
| 27 Oct 2026 | Try Demo, final regression | 744 | 122 | 33 |
| 29 Oct 2026 | Data retention and account deletion | 823 | 138 | 34 |
| 30 Oct 2026 | **v1.0.0-rc.1 release candidate** | 829 | 138 | Passed |

All results are passes with no failures. A dash means the suite was not rerun
for that milestone; the 30 October Playwright + BDD count was not recorded.
Python counts up to 15 October predate the offline AI evaluation harness, which the default Python run includes from 16 October (23
cases that day), so earlier and later Python counts are not directly comparable.
The Python count fell on 22 October because the offline harness stopped
multiplying unchanged checks across request configurations.
On 29 October the suites ran separately: backend pytest 760 passed in 11 min 42 s,
offline AI evaluation 63 in 7.4 s, frontend 138 in about 0.5 s and Playwright + BDD 34
in 1 min 42 s, with no skips or warnings. Each suite used its own disposable databases
(or none), provider credentials were removed, and no real OpenAI calls were made; the
genuine local database was not accessed.
The 10 September pytest run took 114.52 seconds; the 38 temporary frontend
validation-message checks recorded then were not a maintained suite and are not counted.
During the 24 October E2E server ownership audit, one of seven consecutive
Playwright runs had a single failure (29 passed, 1 failed) that could not be
identified or reproduced; the other six runs passed.

**Earlier regression detection (7–8 October 2026):** introducing project-local
bug numbers first failed 18 Python and 16 frontend tests (one Python failure was
a test-stub error; once corrected, that case failed on the intended global-ID
routing assertion); focused API verification then passed 293 cases.
The Fix Version lifecycle correction failed 11 focused tests before the change
and passed 54 afterwards. Numbering and migration tests, on disposable databases,
verify legacy-field preservation, deterministic per-project backfill, rollback
before replacement and before commit, unchanged repeated startup, and no number
consumption after a failed creation.

**Test independence:** on 15 October 2026 the full Playwright suite passed both in
normal order and in reversed order (15/15 each), each run with its own fresh
server and database, so the scenarios do not depend on execution order.

**Refactoring safety:** two test refactors were checked for unchanged behavior,
not just a passing run. Moving the backend tests into `tests/backend/`
(19 October) kept the default collection count at 724 and the Chromium collection at 24,
with identical node IDs apart from the moved module paths. Splitting the
5,231-line bug API test module into six feature modules (23 October) kept all
66 definitions byte-identical and the collection unchanged at 649.

**Coverage progression:** reconciling manual evidence moved AC coverage from
80 Covered / 8 Partial to 85 / 3; member-display and sort-rank tests then gave
87 / 1, and the reviewed live AI evaluation gave 88 / 0 on 16 October 2026.
Adding REQ-024 and REQ-025 on 26 October gave 97 / 5 of 102 ACs; the Try Demo
work reached 102 / 0 on 27 October, with TC-463 completing AC-025.5. The v1.0.0
hardening added AC-009.6 and AC-011.5, both Covered on 28 October, for 104 / 0.
Data retention and account deletion added AC-024.9, AC-025.7 and AC-026.1–AC-026.3,
all Covered on 29 October, for 109 / 0.

<a id="test-organization--19-october-2026"></a><a id="github-actions-ci--20-october-2026"></a>
### Continuous integration

[Application CI](../.github/workflows/application.yml) runs the Python,
JavaScript and Playwright/BDD suites as three jobs on pull requests and pushes
to `main`. With the Postman and JMeter workflows, they are the five required
status checks in the repository's `main` ruleset (checked 28 October 2026). The first hosted run passed 724 + 99 + 24 = 847 tests on
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
| Native Collection Runner, earlier 57-assertion suite (20 Oct 2026, manual) | **57/57 passed**, about 5 s; a rerun and a run after a server restart also passed |
| Native Collection Runner, simplified suite (20 Oct 2026, manual) | **50/50 passed**; traceback-free Ctrl+C shutdown |
| AI-assisted compatibility runs, two disposable servers (20 Oct 2026) | **50/50 passed** in each of four runs; the old environment was rejected after a restart |
| Postman CLI 1.75.0, local (20 Oct 2026) | **50/50 passed**, 3.8 s |
| Hosted [Postman CI run 43](https://github.com/Ventilatorrr/ai-qa-bug-triage/actions/runs/40091942303), `main` at `964a3b1` (24 Oct 2026) | **Success** (assertion counts not printed in silent mode) |
| Postman CLI 1.75.0, local, data retention work (29 Oct 2026) | **50/50 passed**, 25 requests, 3.8 s; the server was stopped by its owned PID and its run directory removed |

The safety checks also confirmed that the launcher refuses an occupied port and
that the collection refuses unsafe targets, stale IDs and live AI configuration.
Git Bash simulations of the CI run step on Windows (syntax check and 7/7 exit-path
simulations) validated its shell control flow, not Linux execution; hosted CI covers that.

<a id="jmeter-finalization--21-october-2026"></a>
### JMeter API performance

JMeter 5.6.3 ran the [API performance plan](../jmeter/README.md) (TC-392) on
21 October 2026 against a fresh local server with AI disabled:

| Configuration | Samples | Errors | Mean | p95 | Throughput |
| --- | ---: | ---: | ---: | ---: | ---: |
| Smoke (1 user) | 7 | 0 | 70.1 ms | 212 ms | 13.3 req/s |
| 2 users, 2 loops | 28 | 0 | 62.3 ms | 206.6 ms | 21.9 req/s |

Earlier manual measurements (JMeter 5.6.3, Java 21, fresh SQLite, port 8150)
were recorded with the plan on 21 October 2026 (`a9f6271`). Exact run dates were
not recorded, and these runs were not independently re-run:

| Users / ramp-up / loops or duration | Samples | Errors | Mean | Throughput |
| --- | ---: | ---: | ---: | ---: |
| 1 / default / 1 loop | 7 | 0 | 66 ms | 11.6 req/s |
| 5 / 5 s / 2 loops | 70 | 0 | 57 ms | 14.5 req/s |
| 5 / 1 s / 10 loops | 350 | 0 | 60 ms | 69.0 req/s |
| 10 / 2 s / 30 loops | 2100 | 0 | 61 ms | 142.3 req/s |
| 15 / 5 s / 120 s | 23112 | 0 | 76 ms | 192.3 req/s |

The 120-second run reported an overall p95/p99 of approximately 254/313 ms.

All these local runs created fictional data without think time. They show that the
workflow runs without errors; they are not production-capacity benchmarks and set
no performance target.

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
  [defect summary](defect-summary.md) lists them.
- **AI review smoke test (5 October 2026):** a disposable app with mocked AI
  output, as Project Owner and QA Analyst. New and Edit Bug covered Use,
  individual and bulk Dismiss, manual editing afterwards, repeat requests, safe
  failure and empty results. Nothing was saved before Create or Save, Edit Cancel
  restored stored values, blank-title validation stayed active after Use All,
  pending Edit review was discarded on reload, and script-like suggestions
  displayed as literal text. A later check with delayed Create and Save
  responses, after Cancel and reopen, found that the late result did not
  overwrite the newer form's values, review or feedback; the older submission
  still saved and refreshed the surrounding data. This is workflow evidence, not
  real-model quality.
- **Frontend diagnostics (6–9 October 2026):** temporary DOM-substitute checks,
  not maintained tests, exercised Bug List sorting, 13 pagination groups, 9
  clickable-row groups and 13 lifecycle-visibility cases; BUG-20 form feedback
  was also observed in the browser. They established no native layout or browser
  behaviour; M02–M04 later covered that manually.
- **Frontend theme and control review (12–13 October 2026):** both themes in the
  development environment's built-in Chromium browser, on static previews with
  the real renderers and deterministic AI responses and on earlier disposable
  FastAPI pages. It covered Login/Register, projects and members, Bug List,
  New/Edit Bug, read-only Details, AI suggestion cards and About. Keyboard row
  focus matched hover, links kept visible 2 px outlines, and validation focus
  showed no double outline. AI cards kept separate values and accessible names,
  and pending review disabled AI Assist. Lifecycle dropdowns kept their empty
  prompt until an option was chosen. Delete states and the native confirmation
  were observed; cancelling preserved the report, but accepting it was not
  browser-verified. At 390 × 844 px, inputs and AI cards did not overflow. The
  standalone browser fixtures passed 9 divider, 4 destructive-state and 12
  native-input variants.
- **Mobile layout and AI data-sharing notice (14 October 2026):** narrow and
  desktop widths in both themes, including mobile sorting and pagination. With a
  verified temporary database and mocked provider, the New/Edit notice was
  checked for placement, keyboard dismissal, removal from the accessible
  description, and persistence across reloads and between forms.
- **Responsive review (23 October 2026):** every page, signed in and out, at
  1440, 1120, 768, 390 and 320 px in both themes, with no page overflow,
  clipped text or header overlap.
- **Bug List layout (23 October 2026):** 43 fictional bugs at 1120–1920 px,
  10/20/50 per page and all seven sorts. Column boundaries no longer move
  between pages, and every desktop row is the same height.
- **Manual release smoke test (29 October 2026):** manual smoke testing,
  separate from the automated regression. It covered:
  - Try Demo creation (seeded projects, members and bugs), plus BUG-54 isolation across
    Demos and between Demo and ordinary accounts, including valid same-Demo memberships.
  - Demo logout, after which a new Demo could not access earlier work.
  - Ordinary project, member and bug creation, editing and lifecycle.
  - AI Assist suggestions across different impact descriptions, and suggestion handling.
  - The Login notice, UI layout and error messages.
  - The `status` command and an account-deletion dry run.

  All checks passed, with no new defects. Confirmed account deletion, automatic
  retention and other destructive administrative operations were not tested manually.

<a id="contrast-measurements--13-october-2026"></a>
### Contrast measurements

A targeted contrast assessment on 13 October 2026, at the end of the 12–13 October
frontend review. Severity and priority values are 16 px text (weight 700 in rows
and Details, 400 in selects and AI cards), so none counts as large text and the
[WCAG 2.2 SC 1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
AA threshold for normal text, 4.5:1, applies. Worst measured ratio per value
across Bug List rows, Details, Create/Edit fields and AI cards, including hover
and focus:

| Severity / priority | Dark theme | Light theme |
| --- | ---: | ---: |
| Blocker / Urgent | 4.66:1 | 5.95:1 |
| Major / High | 5.46:1 | 5.00:1 |
| Moderate / Medium | 7.75:1 | 4.77:1 |
| Minor / Low | 6.48:1 | 5.33:1 |

Ratios came from the browser's computed foreground, font and background styles,
with ancestor transparency layers and the Details gradients composited onto the
background (the gradient base bounds the worst case). Hover and pressed states
were measured by substituting test-only selectors with transitions disabled, and
settled keyboard focus was exercised directly. Pass or fail used unrounded ratios,
and disabled controls were treated as inactive rather than counted as passes.
Every context passed AA, though not all reach the 7:1 AAA target. These results
supported the BUG-31 remediation (dark-theme Blocker/Urgent contrast failure).
Dark Create hover text measured 4.51:1.

Non-text contrast falls under
[SC 1.4.11](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html),
with a 3:1 threshold. Input borders measured at least 3.35:1 (dark) and 3.92:1
(light) against their fills. In the light theme, control borders measured 3.74:1
against the Bug panel and 3.29:1 against the header, and the teal focus indicator
measured 4.74:1 and 4.16:1. These measurements apply to the 13 October palette.
They are not a complete WCAG accessibility audit; see the known limitations.

## Defect and audit-finding verification

Each fix was checked by running the new regression test against the original
code first (it failed), then against the fix (it passed). Rows with a BUG number
are tracked bug reports in the application; the other rows are code-audit or
exploratory findings that were fixed without a separate bug report.

<a id="bug-28-ai-urgent-suggestion-backplate--13-october-2026"></a><a id="bug-34-success-confirmation-overflow--19-october-2026"></a><a id="bug-37-duplicate-new-bug-submission--22-october-2026"></a><a id="malformed-add-member-email-http-500-audit-b2--22-october-2026"></a><a id="bug-39-global-base-font--23-october-2026"></a><a id="bug-41-page-background-brightness-with-page-size--23-october-2026"></a><a id="bug-list-layout--23-october-2026"></a>
| Defect or finding | Found by | Cause and fix | Regression evidence |
| --- | --- | --- | --- |
| BUG-28 — black bar behind the AI Priority suggestion "Urgent" | Tracked bug report | The suggestion value had an opaque dark background (`rgb(7, 13, 22)`); made transparent with the text colour unchanged | Reproduced in a rendered preview, then rechecked without the bar during the 12–13 October review; no permanent test, because the check is visual |
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
| Incomplete Assignee divider and missing explicit Delete focus outline | Frontend theme and control review | Divider and focus-outline styles corrected | Standalone browser fixtures failed before the correction and passed after it |
| E2E port probe accepted listeners on `0.0.0.0` or `[::]` (Windows) | Test-infrastructure safety audit | Probe now binds every interface | TC-413 failed before for both cases |
| BUG-43 — authorization race allowed access to or changes to another user's project | Code review | Owner check ran before the write, so a concurrent Delete Project and reused project ID redirected the change; Update, Delete, Add Member and Remove Member now hold `BEGIN IMMEDIATE` from the check through the write | 27 October, disposable database: a pending Add Member left an orphaned membership that gave access to the next user's project and bug, and restarting the app in-process on that database failed its startup integrity check. TC-464 failed before for Add Member, Rename and Delete; it checks the resulting data and `PRAGMA foreign_key_check`, not a restart. Remove Member is not covered by TC-464. |
| BUG-54 — Add Member accepted accounts across Demo boundaries | Test-first reproduction during the privacy and retention review | Add Member accepted any registered email; it now accepts only accounts from the owner's Demo, or ordinary accounts for ordinary projects, and otherwise answers like an unknown email | TC-498 failed before for all three cross-boundary cases (201 instead of 404) |

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

- **Browser coverage:** Automation is Chromium-only. Firefox, WebKit and real
  mobile devices have not been tested.
- **Accessibility:** There is no full accessibility audit. Screen-reader use is
  limited to the BUG-51 Narrator check; zoom/reflow and focus obscuration were
  not tested, and contrast was last measured on 13 October 2026.
- **AI quality:** Evaluations use small fictional samples with one output per
  case and assisted review. They do not establish statistical reliability or
  rule out hallucinations. Open minor observations: Q5 cross-field wording,
  BUG-18 title overstatement and BUG-17 provisional version.
- **Try Demo:** Demos are deleted by the first hourly cleanup after they are
  seven days old. Tests pass the time in rather than waiting seven days. Deletion of
  an expired Demo has not been observed on a deployment; the 30 October staging check
  only confirmed that no Demo was past retention. Demo creation is subject to usage and
  capacity limits.
- **Concurrency:** Simultaneous changes to the same data may result in
  conflicting updates. High write contention may cause requests to fail.
- **Bug List:** A partial final page moves the pagination controls up.
- **Known limitations:** The pre-release reviews identified additional
  limitations and issues that were evaluated and deliberately deferred based
  on their potential impact and the scope of v1.0.0. Detailed assessments
  are maintained privately.

## Pending release verification

Still outstanding for v1.0.0 after the
[release-candidate verification](#v100-release-candidate-verification--30-october-2026);
results will be recorded here when available. The [release runbook](release-runbook.md)
defines the steps.

- Assessment of the deferred review findings for release impact.
- Sign-off of the privacy and data-handling review.
- Tracker reconciliation and an updated defect snapshot at the release candidate.
- Final Go/No-Go decision.
- Production deployment of the same digest, production smoke checklist and confirmation
  that production matches the hosting statements; then the GitHub Release.
