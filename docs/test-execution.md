# Test execution record

This record separates actual execution from source inspection. The [catalogue](test-cases.md)
defines cases; the [RTM](traceability-matrix.md) owns current overall AC coverage.
No automated test body, application server, browser session or AI provider was run
for the 16 October 2026 catalogue/comment-only redesign.

## Recorded automated baselines

Results below were executed previously, not rerun during this documentation pass.
Source: the former RTM at commit `ec567dd` and its dated execution narratives.
Backend and frontend counts are runner cases, not conceptual TC counts.

| Date | Scope / environment | Recorded result | Provenance and limits |
| --- | --- | --- | --- |
| 15 October 2026 | Default backend; project virtual environment; serial disposable SQLite databases | **575 passed in 539.08s**; no failures/skips | Targeted API coverage pass recorded in `ec567dd`; E2E excluded by default collection. |
| 15 October 2026 | All frontend Node tests; DOM/request/storage substitutes | **96 passed in 272.4076ms**; no failures/skips | Scenario 14/15 extension in `40e7f70`; later `ec567dd` changed Python tests and traceability only. Includes stale-request ordering assertions. |
| 15 October 2026 | Playwright 1.64.0; matching Chromium/headless-shell revision 1248; headless; normal order | **15 passed in 56.65s**; no failures/skips/teardown errors | Fresh verified owned server/database on agent port 8148; mocked provider transport. |
| 15 October 2026 | Same browser setup; every collected node ID reversed | **15 passed in 56.61s**; no failures/skips/teardown errors | Fresh server/database; cleanup checks found no new remaining E2E directories and port 8148 was released. |
| 13 October 2026 | Manually launched native browser fixtures | **9 divider + 4 destructive-state + 12 native-input variants passed** | Separate from Node/PW counts; real markup/styles/native controls, not full application E2E. See [frontend verification](ui-refinements-verification.md). |

Recorded suite commands, run separately and serially:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
node --test tests/frontend/*.test.cjs
.\.venv\Scripts\python.exe -m pytest tests/e2e --e2e --e2e-port 8148 --browser chromium -q --tracing retain-on-failure --screenshot only-on-failure

$e2eNodes = @(.\.venv\Scripts\python.exe -m pytest tests/e2e --e2e --e2e-port 8148 --collect-only -q | Where-Object { $_ -match '^tests/e2e/.*::test_' })
if ($e2eNodes.Count -ne 15) { throw "Expected 15 scenarios" }
[Array]::Reverse($e2eNodes)
.\.venv\Scripts\python.exe -m pytest @e2eNodes --e2e --e2e-port 8148 --browser chromium -q --tracing retain-on-failure --screenshot only-on-failure
```

AI verification uses deterministic mocked output, unavailable-service paths or
in-memory SDK transport. It verifies contracts, authorization, context isolation,
review/persistence boundaries and recovery; it does not evaluate actual model
grounding or factual quality. No real-model evaluation is recorded.

## Structured manual verification — 16 October 2026

Source: the user's Stage 2 instruction, confirming completion of M01–M05.
Environment: **1.0.0-dev, Windows 11, Chrome, FastAPI/Uvicorn**. The exact Chrome
build, source commit and individual measurements/screenshots were not supplied.
These are user-reported passes, not agent-observed executions. No detailed steps,
test data, measurements or additional observations are reconstructed.

The reported groups provide manual evidence for the named UI scopes; existing
API, frontend and recorded diagnostic evidence supplies complementary rules and
edge conditions. Their use in the RTM does not assert that every branch was
manually repeated. No repeat manual run is invented to fill an evidence field.

### M01

**[TC-343](test-cases.md#tc-343) — Bug list/details presentation: reported passed.**
Contributes to AC-012.1 and AC-012.2 alongside API field assertions, frontend
rendering/identity tests and earlier documented presentation checks.

### M02

**[TC-344](test-cases.md#tc-344) — Native browser interactions: reported passed.**
Contributes to AC-012.2 alongside ordinary row/link Playwright navigation,
recorded selection/interactive-control diagnostics and theme/focus observations.
No separate measurements or gesture-by-gesture log was supplied.

### M03

**[TC-345](test-cases.md#tc-345) — Pagination/responsive layout: reported passed.**
Contributes the remaining layout evidence for AC-012.5. Existing browser tests
cover page sizes/navigation; recorded diagnostics cover ranges, reset/clamping
and empty recovery. No viewport dimensions are inferred from this report.

### M04

**[TC-346](test-cases.md#tc-346) — Lifecycle scrolling: reported passed.**
Contributes native scrolling evidence for AC-017.1, alongside the recorded
visibility/exclusion diagnostics and feedback-placement checks. No measured
16px gap or particular viewport geometry is claimed as a newly recorded result.

### M05

**[TC-347](test-cases.md#tc-347) — Pending AI suggestion lifetime: manually
executable checks reported passed.** Contributes to AC-020.8.

The earlier-request-finishes-last race was **not manually reproducible**. Its
evidence is automated and distinct:

- [TC-246](test-cases.md#tc-246), `test_ai_late_success_or_error_cannot_populate_reopened_session`, protects a newer pending request from old success/error/rejection outcomes in both forms.
- [TC-247](test-cases.md#tc-247), `test_ai_late_json_cannot_replace_later_results`, completes an older request's delayed JSON after newer suggestions have rendered, then asserts the newer suggestions/feedback survive in both forms for success/error/rejection variants.
- Other catalogued form-session regressions cover stale Create/Save completions and feedback ownership.

Those assertions were source-reviewed on 16 October and are included in the
recorded 96-test frontend baseline. They were not rerun in this pass. M05 does
not claim manual reproduction of the race or actual-model behavior.

## Coverage reconciliation

The Stage 1 source audit was **80 Covered / 8 Partial / 0 Not Covered**. Combining
the newly reported manual scopes with existing evidence closes the remaining
presentation/native, pagination layout, scrolling and suggestion-lifetime gaps
under AC-012.1, AC-012.2, AC-012.5, AC-017.1 and AC-020.8: **85 / 3 / 0**.
AC-009.5, AC-012.4 and AC-019.2 retain explicit gaps in the RTM. Counts rely on the
user's reported completion of the named manual scopes, not invented detailed
observations. The manual source revision is unspecified; behavior is assessed
against the inspected `ec567dd` implementation. Release/DoD sign-off is separate.

## Exploratory and historical evidence

Exploratory observations remain session summaries, not retrospective formal cases.

| Session | Recorded scope / result | Evidence / limits |
| --- | --- | --- |
| 5 October 2026 AI review smoke | Isolated disposable app; mocked suggestions; New/Edit review, use/dismiss, explicit persistence, cancellation, reload/navigation and literal text observations | Retained in [selected historical evidence](qa-reports/historical-verification.md). No live-model evaluation. |
| 12–13 October 2026 frontend review | Both themes, native input/style fixtures, inline AI cards and control contrast/layout | [Existing verification report](ui-refinements-verification.md); narrower observations, not complete accessibility or cross-browser certification. |
| 14 October 2026 mobile/disclosure review | Recorded isolated mobile/layout and AI-notice dismissal/persistence observations | [Selected historical evidence](qa-reports/historical-verification.md); no new execution claimed. |

For future exploratory sessions, record only date/build/environment, areas explored,
significant findings, verified tracker links and limitations. Existing session
notes do not establish current tracker statuses; consult [defect summary](defect-summary.md).

## Catalogue redesign checks — 16 October 2026

Documentation and source comments only. A temporary read-only validator passed:
347 unique TC entries, 88 exact AC rows, reciprocal mappings, source/line links,
approved parameter selectors, all 575 statically expanded backend combinations
and 96 Node registrations. It executed no test bodies and was removed after use.

Python AST/compile checks passed for all 26 annotated Python test files against
`ec567dd`. Exact comment-only comparison passed for eight Node files and two HTML
fixtures. Node `vm.Script` syntax compilation passed for all eight Node files and
both inline fixture scripts, without executing them. The first syntax-check
helper attempted to read the helpers directory; filtering input filenames fixed
the checker and the complete syntax check then passed. This was not a test or
application failure. `git diff --check` passed. The 17 BDD scenario bodies remain
unchanged/specification-only and contribute no executed count. No full regression
suite was rerun for these documentation/comment changes.

## Deterministic AC closure — 16 October 2026

Baseline: `27c46ac` on `test/ac-coverage`, plus this test-only change. Production
code, fixtures, test server and dependencies are unchanged. The earlier execution
and manual records above remain historical; they are not relabelled as new runs.

- **AC-009.5 / TC-331:** extended the existing membership workflow. Four additional
  fictional accounts are inserted in descending email order with interleaved
  QA/Developer roles. A non-owner member reads the visible member panel; its full
  rendered text sequence must contain the Owner first, all QA Analysts next and
  all Developers last, with alphabetic email order within each role. Expected
  values come from setup inputs, not the member-list API response. Existing
  browser addition/removal and lost-access checks remain.
- **AC-012.4 / TC-348–TC-350:** three generated frontend cases exercise all four
  Severity/Priority ranks and all five Status ranks from deliberately unsorted
  input. Actual rendered cell values and report-number order are asserted in
  both directions. Existing column/preference/storage tests remain unchanged.

| Current command | Result |
| --- | --- |
| `node --test --test-name-pattern=test_bug_sort_complete_ tests/frontend/bug-sort-persistence.test.cjs` | **3 passed**, 0 failures/skips; 207.4846ms |
| `.\.venv\Scripts\python.exe -m pytest tests/e2e/test_authorization.py --e2e --e2e-port 8148 --browser chromium -q -k owner_manages_membership --tracing retain-on-failure --screenshot only-on-failure` | **1 passed, 1 deselected in 9.88s** |
| `node --test tests/frontend/*.test.cjs` | **99 passed**, 0 failures/skips/cancellations; 313.0891ms |
| `.\.venv\Scripts\python.exe -m pytest tests/e2e --e2e --e2e-port 8148 --browser chromium -q --tracing retain-on-failure --screenshot only-on-failure` | **15 passed in 57.44s**, no failures/skips/teardown errors |

The initial sandboxed focused pytest invocation produced no output or completed
result and was interrupted (exit 1). The same command then passed outside the
sandbox. No application defect was identified, and no assertions, delays or
retries were changed to address that invocation issue. Subsequent suites ran
serially; there were no concurrent pytest suites.

The project reports Playwright package **1.64.0**; `playwright install --list`
confirmed installed Chromium/headless-shell **revision 1248**, matching the
package's browsers.json manifest. No browser installation was required. Browser
execution was headless Chromium on the approved **127.0.0.1:8148** origin using
the existing dedicated test server. Its readiness handshake verifies PID,
identity, bound address, fresh absolute temporary SQLite path and cached database
configuration before browser/API interaction. AI transport remains mocked and
external connections blocked. No real database or genuine records were accessed.

Port checks found no listener before startup; the fixture also refuses occupied
ports. Before/after full-run directory inventories found no `ai-qa-e2e-*`
directories remaining, and an exclusive socket bind confirmed 8148 was released.
No unrelated process was terminated or reused.

The catalogue now has **350 TCs**; existing IDs are unchanged and next available
is TC-351. AC-009.5 and AC-012.4 are Covered using the new assertions plus their
existing complementary evidence. Overall coverage is **87 Covered / 1 Partial /
0 Not Covered**. AC-019.2 real-model grounding remains deferred. No unrelated
backend regression run, new manual observation, other-engine or visual/theme
verification is claimed for this pass.
