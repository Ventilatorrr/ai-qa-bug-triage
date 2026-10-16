# QA test execution report

Reporting date: **16 October 2026**. The [test catalogue](test-cases.md) defines
cases; the [RTM](traceability-matrix.md) owns overall AC coverage. Results below
were obtained at the stated milestones. Executed cases, collection counts and
planned evaluations are distinct.

Current assessment: **88 Covered / 0 Partial / 0 Not Covered**, following the
[AC-019.2 final evaluation review](#ac-0192-final-evaluation-review).

## Automated regression milestones

Counts are runner cases, not conceptual TCs. Suites ran serially with fictional
records and disposable SQLite databases. Python used the project virtual environment;
frontend Node tests used DOM/API/storage substitutes rather than a browser.

| Date | Scope | Result | Revision / provenance |
| --- | --- | --- | --- |
| 15 October 2026 | Full default backend; E2E excluded | **575 passed in 539.08s**, no failures/skips | API coverage pass recorded in `ec567dd`; historical baseline |
| 15 October 2026 | Full frontend JavaScript suite | **96 passed in 272.4076ms**, no failures/skips | Scenario 14/15 extension in `40e7f70`; historical baseline |
| 15 October 2026 | Full Chromium Playwright suite, normal order | **15 passed in 56.65s**, no failures/skips/teardown errors | Recorded in the former RTM at `ec567dd` |
| 15 October 2026 | Full Chromium Playwright suite, reversed order | **15 passed in 56.61s**, no failures/skips/teardown errors | Same browser baseline; independent fresh server/database |
| 16 October 2026 | Full frontend JavaScript suite | **99 passed in 313.0891ms**, no failures/skips/cancellations | `27c46ac` plus deterministic coverage additions, subsequently committed in `4ddb56c` |
| 16 October 2026 | Full Chromium Playwright suite | **15 passed in 57.44s**, no failures/skips/teardown errors | Same deterministic coverage milestone |
| 16 October 2026 | Final branch regression: full default backend; E2E excluded | **598 passed in 418.46s**, 0 failed/errors/skipped | `061fcef` plus uncommitted AC-019.2 preparation/prompt/documentation changes; includes 23 offline harness variants |
| 16 October 2026 | Final branch regression: full frontend JavaScript suite | **99 passed in 448.5421ms**, 0 failed/skipped/cancelled | Same working tree; serial execution after backend |
| 16 October 2026 | Final branch regression: full Chromium suite | **15 passed in 60.59s**, 0 failed/errors/skipped | Same working tree; normal order, separate isolated server; cleanup passed |

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

### Final branch regression verification

The latest runs used fresh pytest temporary/output paths below ignored
`test-results/final-regression-1792161271051/`, with inherited provider credentials
and live opt-in removed. A disposable bootstrap `DATABASE_NAME` was configured
before pytest; existing fixtures replaced it with fresh per-test paths and rebound
cached configuration before lifespan startup. Neither bootstrap database was created.
Executed commands (path variable expanded in the actual pytest arguments):

```powershell
$verificationRoot = 'D:\Portfolio\ai-qa-bug-triage\test-results\final-regression-1792161271051'
.\.venv\Scripts\python.exe -m pytest -q --basetemp "$verificationRoot\backend-temp" --output "$verificationRoot\backend-output" --junitxml "$verificationRoot\backend.xml"
node --test tests/frontend/*.test.cjs
.\.venv\Scripts\python.exe -m pytest tests/e2e --e2e --e2e-port 8148 --browser chromium -q --basetemp "$verificationRoot\e2e-temp" --output "$verificationRoot\e2e-output" --junitxml "$verificationRoot\e2e.xml" --tracing retain-on-failure --screenshot only-on-failure
```

Two preliminary backend attempts were blocked by a sandbox-generated temporary
path: the first ended with `PermissionError` before a final summary; the second
reported **116 passed / 482 setup errors / 0 failed / 0 skipped** in 11.08s because
the base temporary path was unavailable. The fresh repository-local directory
resolved the environment issue; no application/test code was changed. The completed
598-test run and JUnit report contain zero errors.

Port 8148 was free before startup. Runtime process inspection confirmed the owned
`tests.e2e.server` with a newly generated temporary database; fixture assertions
verified its effective configuration and mocked provider. Afterward the process
exited, its temporary directory was removed and the port was released; pre-existing
temporary entries were untouched. Explicit `--output` paths confined plugin cleanup.
SHA256 comparison confirmed all **seven** preserved AI evidence files were unchanged.
No real application database or live provider was accessed. Only this execution
report was updated; `git diff --check` passed. Existing AC coverage remains **88/88**.

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
| Overall AC coverage at Stage B1 | **87 Covered / 1 Partial / 0 Not Covered**; AC-019.2 was Partial |

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

The original Stage B1 offline artifact is no longer present at its recorded
location; these are retained historical execution results. Subsequent preserved
offline artifacts are identified below, without treating them as that original run.
Stage B1 checks confirmed `offline_fixture_only`, all dimensions `Not assessed`,
`live_model_evaluated=false` and `database_created=false`. Synthetic usage is not
billable usage or real-model evidence.

Safety verification covered explicit live opt-in, pytest/CI rejection, six-attempt
limits, zero automatic retries, credential-safe failure records and cleanup.
The runner configured a fresh temporary database path before imports, rebound
cached configuration and blocked SQLite connections without creating a database.
Existing unit tests used disposable pytest databases and mocked transports.
No production AI behavior changed; no real database, genuine records, real-model
request, application server or browser was used during Stage B1. **The full backend
suite was not executed during Stage B1.** Subsequent live baselines are recorded
below; they are separate from these offline results.

## AC-019.2 live evaluation evolution — 16 October 2026

**30 live-model evaluations: 12 original-prompt, 12 historical-context
clarification and six final formatting-correction requests.** Each invocation
completed A–F once, serially, using `gpt-6-luna`, SDK 3.23.0, the same fictional
dataset v1 and unchanged rubric. All 30 attempts completed; no provider/parse
failures, validator exclusions, unrun cases or automatic retries were recorded.

| Prompt stage / UTC start | Preserved evidence under `ai-evaluation-results/` | Finding |
| --- | --- | --- |
| Original, 13:03:06 | `20261016T130306Z-a7300483/run.json` | D rewrote Description/Steps; no distinctive historical values |
| Original, 13:19:19 | `20261016T131919Z-625454ca/run.json` | D rewrote Title/Description; no distinctive historical values |
| Historical clarification, 14:05:04 | `20261016T140504Z-74dde20f/run.json` | D proposed all five supported historical values with clean formatting |
| Historical clarification, 14:06:54 | `20261016T140654Z-c75c9086/run.json` | D proposed all five values, but appended provenance to Environment/Affected Version |
| Final formatting correction, 14:20:02 | `20261016T142002Z-84033391/run.json` | D proposed all five values without embedded explanations; final A–F review below |

Original runs record `aa6977b` plus local recorder changes; later runs record
`061fcef` with tracked changes. Request snapshots distinguish the three prompt
versions; revision alone does not. All share dataset SHA256
`f7ad0ba5cd12a4a612fe73f65ebd8821b19ffbadab09e156b63c84680376bbcc`.
The original protocol is preserved at `aa6977b` and in baseline snapshots
(SHA256 `21b83707749ef6f6918bd80bd8505a4b7035a6ac18d5ab370086bb65bd8afc1d`).
Later snapshots include procedural updates; the dataset and scoring rubric are unchanged.

Across all runs, A abstained; B/C produced grounded, nonempty rewrites; C did not
replace current observations with conflicting history 401; E omitted unknown
causes or supplied only supported actions/expected behavior; F did not import
unrelated history 601/602. No critical semantic failure was identified in this
review. Original D outputs were valid but did not exercise historical-value use,
so coverage remained Partial at that checkpoint. The clarification demonstrated
that capability twice. The second clarified D response had a field-formatting
quality issue, not unsupported historical facts; its raw output remains preserved.
The final prompt retained historical proposals while correcting that formatting.

Pass 1's original file was later missing; the exact deletion event was not proven.
Investigation established that pytest-playwright clears its default `test-results/`
root. Preserved baseline copies now reside at the paths above. The runner writes
new evidence to ignored `ai-evaluation-results/`, outside that cleanup root; it
does not migrate, overwrite or delete previous runs. Raw evidence was not edited
during this documentation review.

**Post-baseline offline verification — 16 October 2026:** the evaluation harness,
prompt-contract and SDK-adapter suites passed **56 tests in 2.64s**. Command scope:
`.\.venv\Scripts\python.exe -m pytest tests/test_ai_evaluation.py tests/test_ai_generation.py tests/test_ai_openai.py -q`.
Execution used absolute test paths from a disposable working directory, with
`--rootdir` pointing to the repository and `--basetemp` to a new owned temporary
directory. Global verification guards blocked SQLite and socket connections;
the pure test fixtures no longer start an unused TestClient.

Six post-change synthetic evaluations completed. Their artifact survived that
ordinary pytest session byte-for-byte while pytest-playwright deleted a marker
inside the disposable working directory's default `test-results/` root. All six
recorded requests contained the new instruction. Original evidence, dataset,
adapter/validator and the separate JWT edit retained their prior hashes.
Generated evidence is Git-ignored at
`ai-evaluation-results/offline-verification-9997dcf8d29d4fed89fd44ac92e73980/run.json`.
The sandboxed verification attempt stopped with a `PermissionError`; the approved
outside-sandbox execution produced the completed results above. No live requests,
database connections, full backend suite or browser suite were run for these fixes.
At this offline checkpoint, follow-up model quality was unverified and AC-019.2
remained **Partial**; the subsequent live results are assessed below.

**Value-only prompt verification — 16 October 2026:** focused generation and SDK
adapter tests passed **33 in 1.32s** (`tests/test_ai_generation.py` and
`tests/test_ai_openai.py`, project interpreter, `-m pytest -q`). TC-021 and TC-024
now assert the field-value-only instruction and its transmission in the production
request. Tests ran from a disposable working directory with SQLite/socket guards;
no live requests or database connections occurred. Existing evidence, scenarios,
rubric, schema and validator were unchanged. This offline check alone did not
verify model compliance; the subsequent 14:20 UTC run supplies that evidence.

## AC-019.2 final evaluation review

Evidence: `ai-evaluation-results/20261016T142002Z-84033391/run.json`, started
**16 October 2026, 14:20:02 UTC**. Reviewer: **Codex, user-directed assisted review**;
coverage closure is recorded at the user's direction. This is an inspection of
preserved outputs, not a new model execution or an independently witnessed human
test. The original `pending_human_review` templates remain untouched in raw JSON;
the following table records this review separately against the frozen rubric.

P = Pass; NE = Not exercised. Empty output can pass grounding/abstention/schema
without demonstrating rewriting or historical use.

| Case / TC | Factual grounding | Current-form primacy | History use | Uncertainty | Schema | Rationale from actual response |
| --- | --- | --- | --- | --- | --- | --- |
| EVAL-A / TC-351 | P | NE | NE | P | P | Empty suggestions for only “Export fails”; no invented steps, environment, version or observed error. No conflicting context supplied. |
| EVAL-B / TC-352 | P | P | NE | P | P | Title becomes “Filtered CSV export contains only the header”, supported by the current Actual Result. No new factual claims; supplied reproduction/environment/version are not contradicted. No history supplied. |
| EVAL-C / TC-353 | P | P | P | P | P | Header-only title and three ordered steps retain State=Ready and seven rows. Does not substitute history 401's no-download outcome, 0.5.0 or older browser for the unsaved retest. |
| EVAL-D / TC-354 | P | P | P | P | P | Five proposals match relevant reports 502/501: Affected Version `0.8.2`, Environment `TestOS 4 / Aster Browser 12`, Severity `Moderate`, Priority `Medium`, Assignee `12` (eligible Developer). No claim of current verification or invented expertise. |
| EVAL-E / TC-355 | P | P | NE | P | P | “1. Click Preview.” derives from Actual Result; “The preview is displayed.” is an expected outcome, not a claim of observed success. Omits suspected timeout, logs, cause and unknown impact. No history supplied. |
| EVAL-F / TC-356 | P | P | P | P | P | Header-only title is grounded in current Actual Result. No LegacyPrintOS 9, 0.2.0, avatar/timezone facts or unsupported assignee inference from unrelated reports 602/601. |

**EVAL-D returned all five historically supported values with correct field-only
formatting.** Environment and Affected Version contain only their respective
values, with no parentheses, source references or uncertainty prose. The current
build/browser remain unverified; historical support justifies proposals for empty
fields without making them authoritative. C exercises conflicting-history primacy;
D exercises relevant-history use; F exercises rejection of unrelated history.

Raw `output_text` parses to the recorded decoded responses; all six use the
expected structured schema and match validated usable output, with **zero
validator exclusions**. A correctly yields `no_usable_suggestions`; B–F yield
suggestions. All mechanical checks pass, with unchanged contexts, recorded usage,
matching model and `database_created=false`. These checks support the semantic
review; absence of a review flag alone is not treated as a pass.

**Assessment: AC-019.2 Covered; 88 Covered / 0 Partial / 0 Not Covered.** The
collective evidence combines existing deterministic API/context/prompt tests with
the reviewed real-model cases: grounded rewriting, current-form primacy, supported
same-project proposals, uncertainty and irrelevant-history rejection. Both
six-case clarification runs exercise historical support; the formatting correction
has **one** final six-case run, not two repeats of the final configuration. This
bounded, user-authorized closure does not establish statistical reliability,
zero hallucinations, independent human scoring, other models/datasets or release
readiness. Frozen expectations have not been relaxed and earlier observations
have not been reclassified as blanket passes.

Only documentation consistency and evidence-integrity checks were run for this
closure. **No full regression, new tests, live requests, servers or database
access occurred.** Historical automated results above remain the latest recorded
executions for their respective scopes.

Documentation verification used an inline standard-library Python script with
the project interpreter (`.\.venv\Scripts\python.exe -B -`): **363 unique TC IDs**,
next **TC-364**, **406 reciprocal mappings**, **88 exact AC IDs/titles**, and
**88 Covered / 0 Partial / 0 Not Covered**. All referenced documentation files
resolve; obsolete evaluation paths are removed. SHA256 checks preserve all seven
local `run.json` artifacts and existing non-documentation changes; dataset/rubric
comparisons pass, and all seven artifacts remain Git-ignored. `git diff --check`
passed with no whitespace errors. These are consistency checks, not test-suite results.

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
**87 / 1**. Stage B1 did not close the remaining real-model gap; the reviewed live
evaluation now supports **88 / 0** with the limitations above. The 17 BDD scenarios
remain specifications without executable bindings and contribute no passing tests.

Exploratory notes are session evidence, not retrospective formal cases or current
defect statuses; consult the [defect summary](defect-summary.md). Coverage does not
establish release completion: broader browser/accessibility checks and the
[Definition of Done](definition-of-done.md) remain separate assessments.
