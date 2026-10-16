# QA test execution report

Reporting date: **16 October 2026**. The [test catalogue](test-cases.md) defines
cases; the [RTM](traceability-matrix.md) owns overall AC coverage. Results below
were obtained at the stated milestones. No suites were rerun for this documentation
cleanup. Executed cases, collection counts and planned evaluations are distinct.

## Automated regression milestones

Counts are runner cases, not conceptual TCs. Suites ran serially with fictional
records and disposable SQLite databases. Python used the project virtual environment;
frontend Node tests used DOM/API/storage substitutes rather than a browser.

| Date | Scope | Result | Revision / provenance |
| --- | --- | --- | --- |
| 15 October 2026 | Full default backend; E2E excluded | **575 passed in 539.08s**, no failures/skips | API coverage pass recorded in `ec567dd`; latest full backend result |
| 15 October 2026 | Full frontend JavaScript suite | **96 passed in 272.4076ms**, no failures/skips | Scenario 14/15 extension in `40e7f70`; historical baseline |
| 15 October 2026 | Full Chromium Playwright suite, normal order | **15 passed in 56.65s**, no failures/skips/teardown errors | Recorded in the former RTM at `ec567dd` |
| 15 October 2026 | Full Chromium Playwright suite, reversed order | **15 passed in 56.61s**, no failures/skips/teardown errors | Same browser baseline; independent fresh server/database |
| 16 October 2026 | Full frontend JavaScript suite | **99 passed in 313.0891ms**, no failures/skips/cancellations | `27c46ac` plus deterministic coverage additions, subsequently committed in `4ddb56c` |
| 16 October 2026 | Full Chromium Playwright suite | **15 passed in 57.44s**, no failures/skips/teardown errors | Same deterministic coverage milestone |

The 16 October additions verify rendered member emails/roles and ordering
(AC-009.5 / TC-331), plus complete Severity, Priority and Status rank ordering in
both directions (AC-012.4 / TC-348–TC-350). Final suite results supersede the
intermediate focused implementation runs.

Browser environment: **Playwright 1.64.0**, matching Chromium/headless-shell
**revision 1248**, headless Windows execution at **127.0.0.1:8148**. The dedicated
server verified process identity, bound address and fresh temporary database
configuration before interaction. AI responses were mocked; external connections
were blocked. Cleanup checks confirmed temporary E2E directories were removed and
port 8148 released. Unrelated processes were preserved.

Recorded commands, executed separately:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
node --test tests/frontend/*.test.cjs
.\.venv\Scripts\python.exe -m pytest tests/e2e --e2e --e2e-port 8148 --browser chromium -q --tracing retain-on-failure --screenshot only-on-failure
```

The reversed-order run used all 15 collected node IDs:

```powershell
$e2eNodes = @(.\.venv\Scripts\python.exe -m pytest tests/e2e --e2e --e2e-port 8148 --collect-only -q | Where-Object { $_ -match '^tests/e2e/.*::test_' })
if ($e2eNodes.Count -ne 15) { throw "Expected 15 scenarios" }
[Array]::Reverse($e2eNodes)
.\.venv\Scripts\python.exe -m pytest @e2eNodes --e2e --e2e-port 8148 --browser chromium -q --tracing retain-on-failure --screenshot only-on-failure
```

## Manual acceptance testing — 16 October 2026

M01–M05 are **user-reported passes**, not agent-observed executions. Environment:
**1.0.0-dev, Windows 11, Chrome, FastAPI/Uvicorn**. Exact Chrome build, source
revision, viewport dimensions, screenshots and individual measurements were not
supplied. These reports complement automated and historical evidence; they do not
imply every edge condition was manually repeated.

### M01

**[TC-343](test-cases.md#tc-343) — Bug list/details presentation: reported passed.**
Contributes to AC-012.1 and AC-012.2 alongside API field and frontend rendering checks.

### M02

**[TC-344](test-cases.md#tc-344) — Native browser interactions: reported passed.**
Contributes to AC-012.2 alongside Playwright navigation and native-control diagnostics.
No gesture-by-gesture execution log was supplied.

### M03

**[TC-345](test-cases.md#tc-345) — Pagination/responsive layout: reported passed.**
Contributes layout evidence for AC-012.5; automation and historical diagnostics
supply complementary page-size, navigation, range and recovery checks.

### M04

**[TC-346](test-cases.md#tc-346) — Lifecycle scrolling: reported passed.**
Contributes native scrolling evidence for AC-017.1. No measured 16px gap or specific
viewport geometry is claimed from this report.

### M05

**[TC-347](test-cases.md#tc-347) — Pending AI suggestion lifetime: manually executable
checks reported passed.** Contributes to AC-020.8.

The earlier-request-finishes-last race was **not manually reproducible**.
[TC-246](test-cases.md#tc-246) and [TC-247](test-cases.md#tc-247) provide distinct
frontend automation for stale success/error/rejection and delayed JSON outcomes
in both forms, preserving newer suggestions and feedback. Their assertions were
source-reviewed and included in the recorded frontend regressions. M05 does not
claim manual reproduction of the race or actual-model behavior.

## AC-019.2 Stage B1 — offline evaluation verification

Date: **16 October 2026**. Baseline: **`56d437a` on `test/ac-coverage`**, plus
uncommitted harness/documentation changes. The [AI evaluation protocol](ai-testing-strategy.md)
defines six fictional cases (TC-351–TC-356) and the rubric before live execution.
Relevant history may support Environment, Affected Version, Severity, Priority and
eligible Assignee proposals; proposed values differ from claims of current verification.

| Final verification | Result |
| --- | --- |
| Related AI pytest suites | **187 passed in 6.15s**, including **23 offline harness variants** across TC-357–TC-363 |
| Standalone offline evaluation | **Six synthetic evaluations completed**, exit 0; no semantic/model-quality pass claimed |
| Default pytest collection | **598 tests collected in 1.06s**; collection only, not a full backend run |
| Catalogue and RTM consistency | **363 unique TC IDs**, next **TC-364**; **406 reciprocal mappings**; 88 unique AC rows |
| Overall AC coverage | **87 Covered / 1 Partial / 0 Not Covered**; AC-019.2 remains Partial |

Commands for these final results:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_ai_evaluation.py tests/test_ai_generation.py tests/test_ai_openai.py tests/test_ai_response.py tests/test_ai_suggestions.py -q
.\.venv\Scripts\python.exe -m tests.ai_evaluation.run_evaluation --offline
.\.venv\Scripts\python.exe -m pytest --collect-only -q | Select-Object -Last 2
```

**Defect/retest:** simulated Ctrl+C during a provider attempt initially failed the
focused regression (**1 failed, 22 deselected in 2.09s**). Command:
`.\.venv\Scripts\python.exe -m pytest tests/test_ai_evaluation.py -q -k interrupt`.
The runner was corrected to record the interrupted attempt, close its client and
stop without retry. TC-360 includes this variant and verifies failure cleanup;
the final 187-test run passed. Missing reciprocal RTM links for TC-351–TC-356 were
also corrected and explicitly labelled live execution pending.

Local generated evidence, excluded from Git:
`test-results/ai-evaluation/20261016T123342Z-8befca5b/run.json`.
It retains input/protocol hashes and snapshots, production-generated requests,
synthetic raw/validated responses and usage/cost, and unassessed review templates.
Checks confirmed `offline_fixture_only`, all dimensions `Not assessed`,
`live_model_evaluated=false` and `database_created=false`. Synthetic usage is not
billable usage or real-model evidence.

Safety verification covered explicit live opt-in, pytest/CI rejection, six-attempt
limits, zero automatic retries, credential-safe failure records and cleanup.
The runner configured a fresh temporary database path before imports, rebound
cached configuration and blocked SQLite connections without creating a database.
Existing unit tests used disposable pytest databases and mocked transports.
No production AI behavior changed; no real database, genuine records, real-model
request, application server or browser was used during Stage B1. **The full backend
suite was not executed during Stage B1.** Live execution and human review remain
pending separate approval.

## Historical evidence and limitations

| Date / milestone | Evidence and limits |
| --- | --- |
| 7–8 October 2026 identity/persistence and Fix Version corrections | Failures before correction and successful focused/full retests are retained in [historical defect/retest evidence](qa-reports/historical-verification.md#public-identity-and-persistence-regressions--78-october-2026). Historical checkpoints, not current suite totals or tracker status. |
| 5 October 2026 AI review smoke | Disposable application with mocked suggestions: New/Edit review, use/dismiss, explicit persistence, cancellation, reload/navigation and literal text. See [historical verification](qa-reports/historical-verification.md#ai-review-and-form-safety--5-october-2026); no real-model evaluation. |
| 12–13 October 2026 frontend review | Themes, inline AI cards, native controls and layout/contrast observations. **9 divider + 4 destructive-state + 12 native-input variants passed**, separate from Node/Playwright counts. See [frontend verification](ui-refinements-verification.md); not comprehensive accessibility or cross-browser certification. |
| 14 October 2026 mobile/disclosure review | Isolated layout, AI-notice dismissal and persistence observations in [historical verification](qa-reports/historical-verification.md#mobile-layout-and-ai-disclosure--14-october-2026); no new execution claimed. |

Some sandboxed browser/offline CLI invocations did not complete, including an
offline CLI `PermissionError`; the same commands subsequently completed outside
the sandbox. No pass is attributed to blocked attempts. Final results above
supersede intermediate implementation runs, not unresolved failures.

Manual evidence reconciliation moved coverage from **80 Covered / 8 Partial** to
**85 / 3**; member-ordering and complete sorting-rank execution then supported
**87 / 1**. Stage B1 did not close the remaining real-model gap. The 17 BDD scenarios
remain specifications without executable bindings and contribute no passing tests.

Exploratory notes are session evidence, not retrospective formal cases or current
defect statuses; consult the [defect summary](defect-summary.md). Coverage does not
establish release completion: broader browser/accessibility checks and the
[Definition of Done](definition-of-done.md) remain separate assessments.
