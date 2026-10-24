# AI QA Bug Triage – API Regression Test Suite

**25 ordered requests / 50 named assertions**, in seven folders, reusable across
`0.2.0`, `1.0.0` and later compatible releases. The suite covers fictional user
setup, project membership, bug
CRUD/validation, authorization, unavailable AI, and the full lifecycle through
Closed/Fixed, reopening and deletion. Broader role/state combinations remain in pytest.

## Start, import and run

From the repository root:

```powershell
.\.venv\Scripts\python.exe postman/serve.py
```

1. The launcher must reserve **http://127.0.0.1:8148** and print its PID, new
   database path and generated environment path. If the port is busy, stop;
   preserve the existing process and do not select another port.
2. Import `AI QA Bug Triage.postman_collection.json` from this directory. Its
   display name is **AI QA Bug Triage – API Regression Test Suite**.
3. Import and select the generated environment at the exact printed path:
   `postman/.runtime/run-*/Isolated.postman_environment.json`. Its unique name
   starts with `Disposable Postman`. Do not overwrite the user's Local environment.
   The checked-in sanitized templates have no run credentials and cannot authorize a run.
4. Run all **25 requests in saved order**, **one iteration**, no data file,
   with automatic redirects disabled. Expect **50 passing assertions**; the
   deliberate 422, 503, 401, 403 and final 404 responses are successful negative tests.
5. Rerun the entire collection against the same server to generate fresh users,
   project and bug data. Never resume a partial or failed workflow with saved IDs.
6. Press **Ctrl+C** in the server terminal. Normal shutdown removes only that
   launcher's run directory and prints confirmation after removal. Port 8148 is
   released when the process exits. Forced termination may leave an ignored run
   directory; never delete unrelated runtime or historical test-results directories.

After restarting the server, import/select its **newly generated environment**:
its run identity, key and JWT signing secret differ, so the old environment is rejected.
Avoid persisting/exporting credential-bearing login responses. No runner installation,
Newman integration or background-process options are provided by this launcher.

## Authentication and failure handling

Registration, Login and request 16 use **No Auth**. Login automatically saves
`owner_token`, `dev_token` or `qa_token` in run-local variables. The collection's
built-in Bearer authorization defaults to `{{qa_token}}`; requests 07–10, 19 and 22
explicitly use `{{owner_token}}`, and 17/20 use `{{dev_token}}`. Other authenticated
requests inherit QA authorization. There are no role-switching pre-request scripts.

A shared post-response script checks HTTP status and calls
`pm.execution.setNextRequest(null)` on an unexpected status. Each request uses one
ordinary `pm.test` for its response/business checks. IDs, JWTs and the one necessary
bug snapshot are saved only after those assertions and the expected status pass.
Only then is the next numbered step enabled. The shared pre-request guard rejects
out-of-order or failed prerequisites with **both** `skipRequest()` (no current HTTP
request) and `setNextRequest(null)` (end the Runner iteration). Script/transport
errors also leave the next step disabled. `skipRequest()` alone does not stop a run.

## Isolation and AI safety

The launcher runs the checked-out application code for the release under test;
it never targets a live production database. It accepts no database/origin override
and owns a fresh absolute SQLite
path under ignored `postman/.runtime/`, verifies configuration before application
startup, and rejects SQLite connections to other disk paths. Development/demo
records and the user's Postman QA Sandbox are never used. Nothing under
`test-results/` is swept or removed by the launcher.

Each collection request verifies the test-only server identity using its random
run key, which the wrapper also requires on every API request. New run-local IDs
shadow saved values; missing IDs and unresolved variables are rejected. The
project name is only a label. Provider credentials are removed and external socket
connections are blocked; request 15 expects the genuine unconfigured-provider 503.
No production application code or paid AI service is involved.

## GitHub Actions

[Postman API regression](../.github/workflows/postman.yml) runs separately on pull
requests targeting `main` and pushes to `main`. It preserves the existing CI
workflow and its three required checks. The job uses Ubuntu 24.04, Python 3.14,
the application's pinned `requirements.txt` runtime dependencies and a
**10-minute** job timeout.

The official [`postmanlabs/postman-cli-action@v1`](https://github.com/postmanlabs/postman-cli-action/blob/v1/action.yml)
installs **Postman CLI 1.75.0** and runs `--version`, without an API key or login.
The collection then runs in one Bash step with the background launcher and an
exit trap. This keeps process ownership and `wait` in the same shell and correctly
quotes the collection filename, which the action's command splitting does not do.

The launcher reserves port **8148** before creating data and refuses a busy port.
Readiness makes at most **30 attempts**, with a one-second HTTP timeout and
one-second pause between unsuccessful attempts. It checks that the launcher is
still running, reads the generated environment path from this launcher's freshly
overwritten log, checks that file exists and waits for an HTTP response. The
unkeyed identity endpoint returns **403** from the test wrapper without calling
the application; its body is discarded. Database isolation stays in `serve.py`,
and authenticated identity validation stays in the collection's per-request
guard. No environment JSON is parsed by the workflow, and it never searches
historical runtime directories or selects the Local template. The command is:

```bash
postman collection run "postman/AI QA Bug Triage.postman_collection.json" \
  --environment "$environment_file" --ignore-redirects --no-report-events --silent
```

`environment_file` is the path freshly reported by this launcher. Postman runs
all 25 requests in saved order, including their 25 additional identity checks and
50 named assertions. Readiness uses unkeyed availability probes. `--silent`
prevents assertion failure details from printing credentials; the CLI's exit code
still fails the step. No environment contents, response reports or runtime files
are printed or uploaded, and run-event reporting is disabled. The job prints a
generic success message only after Postman exits successfully.

The exit trap runs after success, startup failure, timeout or a failing CLI
command, and handles shell interruption/termination. It sends **SIGINT** to the
owned PID, waits for launcher exit and verifies removal of that launcher's runtime
directory, including its SQLite database and environment. GNU `env
--default-signal=INT` restores interrupt handling for the background Python
process. Uvicorn can re-raise SIGTERM after shutdown, bypassing Python directory
cleanup; SIGINT uses the launcher's existing KeyboardInterrupt handling instead.
No change to `serve.py` is needed. A server that fails to stop within 20 seconds
is killed by owned PID and the job fails; leftover owned data also fails the job.
There is no runtime-directory sweep. Abrupt runner loss or forced job termination
cannot guarantee normal cleanup; the hosted runner itself is disposable.

Inspect **Actions → Postman CI → a run** for the outcome. Hosted execution,
including Linux startup and the cleanup checks above, has passed; for example
[run 43](https://github.com/Ventilatorrr/ai-qa-bug-triage/actions/runs/40091942303)
(24 October 2026, `main` at `964a3b1`). The CLI runs with `--silent`, so the
hosted log reports success, not assertion counts. Local syntax and Bash workflow
simulations are recorded separately in the execution report.

## Requests and existing conceptual test cases

[The catalogue](../docs/test-cases.md) owns exact request selectors and the 27 reused
TC mappings. The workflow uses QA for bug creation/editing/Open, Owner for
Development/reopening, Developer for the Testing handoff, and assigned QA for Pass.
Identity, persisted state, timestamps, assignees and Fix Version remain asserted.
`postman-fixture` (Affected Version) and `0.0.0-postman-fixture` (Fix Version) are
synthetic bug data, not the application version or a claim about a release.
Request 23 verifies reopened persistence; it does not directly test AI failure.

## Safety verification procedure (TC-391)

1. Verify fresh effective database configuration, removed provider credentials,
   a new signing secret, and audit rejection of a different nonexistent SQLite
   path and an external socket before IO; never probe a real database.
2. Verify a second launcher refuses the occupied origin without creating data.
3. Verify wrong origin/proof, malformed proof, partial starts, missing IDs and
   failed prerequisites skip the current request and stop the iteration.
4. Run twice with stale saved IDs, then restart: the old environment must fail,
   and a new generated environment must permit a fresh full run.
5. Send Ctrl+C; verify no traceback, exit 0, actual owned-directory removal and
   port release. A genuine startup/runtime failure must still be reported.

## Execution evidence

On 20 October 2026, the user confirmed the simplified suite's native Runner
**25 requests / 50 of 50 assertions passed** against isolated `1.0.0-dev`, with no
reported failures and traceback-free Ctrl+C shutdown. The earlier 57/57 native run
and Codex's compatibility/cleanup checks remain separate historical evidence.

Record each execution's date, actual application version, suite, environment,
method, request/assertion counts, result and commit/tag when available in
[test execution](../docs/test-execution.md#postman-api-regression-suite--20-october-2026).
Version reporting is manual; `/version` may confirm it without adding a suite
request. Record a separate run when testing `0.2.0` or another release. The earlier
metadata/fixture cleanup did not execute a new native run.

Separately, on **20 October 2026**, the user confirmed the final collection with
**Postman CLI 1.75.0**: **25 application requests + 25 identity checks; 50/50 named
assertions passed; 0 failures; exit 0; 3.8 seconds; 29 ms average response time**,
against isolated `1.0.0-dev` launched by `serve.py`. This is local CLI evidence,
separate from native desktop Runner results and hosted CI runs.
