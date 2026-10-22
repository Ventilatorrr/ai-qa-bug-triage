# ai-qa-bug-triage
Bug triage application built as a QA portfolio project with FastAPI, SQLite, and a plain HTML/CSS/JavaScript frontend.

Authentication, project/member management, and bug-management APIs through REQ-017 are implemented. The frontend supports bug creation, viewing, editing, deletion, lifecycle actions, sorting, and pagination. Increment 3 AI Assist is implemented with explicit suggestion review and normal Create/Save persistence. Broader browser verification and increment completion remain outstanding; see traceability for evidence and gaps.

Current automated coverage uses pytest/FastAPI TestClient, database integration tests, mocked AI provider tests, dependency-free frontend JavaScript tests, and a focused Python Playwright E2E suite including five executable pytest-bdd scenarios across four feature files. All five BDD scenarios are executable; see the [catalogue](docs/test-cases.md#executable-bdd--testse2ebddtest_workflowspy). Real-model AI evaluation has been completed and reviewed; see the [execution record](docs/test-execution.md#ac-0192-final-evaluation-review). The latest user-confirmed GitHub Actions milestone passed 724 Python, 99 JavaScript and 24 Playwright/BDD tests (847 total), with three required checks protecting `main`. [AI QA Bug Triage – API Regression Test Suite](postman/README.md) provides 25 isolated API requests and 50 named assertions; the user confirmed all 50 passed in native Postman against `1.0.0-dev`. The suite is reusable across compatible releases, with each execution recording its actual application version. A separate Postman CLI workflow is configured; hosted Postman execution remains unverified.

See [requirements](docs/requirements.md), [traceability](docs/traceability-matrix.md), and the [QA strategy](docs/qa-strategy.md) for current behavior and verification gaps. Historical working notes and requirements_old.md are not the current specification.

For a fresh Windows PowerShell setup, install Python 3.14 and Git, then run:

```powershell
git clone https://github.com/Ventilatorrr/ai-qa-bug-triage.git
cd ai-qa-bug-triage
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pip check
$env:JWT_SECRET_KEY = python -c "import secrets; print(secrets.token_urlsafe(48))"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

If `py` is unavailable, replace `py -3.14` with the path to your Python 3.14
executable.

`requirements.txt` contains the core runtime dependencies. For a runtime-only
installation, use `python -m pip install -r requirements.txt` instead.
`requirements-ai.txt` adds the optional OpenAI SDK; install it with
`python -m pip install -r requirements-ai.txt` if you want live AI Assist.
`requirements-dev.txt` includes both manifests, pytest, and httpx2 for the full
Python test suite. The SDK is required by mocked provider tests even without an
API key. Direct dependencies are pinned; transitive dependencies are resolved by
pip. SQLite is included with Python.

`JWT_SECRET_KEY` is required and must not be empty or whitespace-only. The
application will refuse to sign or verify tokens without a nonblank value.
Use a long, random value and do not commit it to the repository. Changing the
secret invalidates all existing tokens; users must log in again. The command
above generates a new secret for the current shell session; preserve your local
secret securely outside the repository if you need tokens to survive restarts.

Open http://127.0.0.1:8000/login.html. Stop Uvicorn with Ctrl+C, then run the
backend pytest suite from the repository root using the project virtual environment:

```powershell
Remove-Item Env:OPENAI_API_KEY -ErrorAction SilentlyContinue
.\.venv\Scripts\python.exe -m pytest
```

Tests configure their own temporary JWT secret, mock provider calls, and require
no real API key. Each API test uses a fresh absolute SQLite path under pytest's
`tmp_path`. The fixture sets the environment before application import, rebinds
cached database configuration before lifespan startup, and removes its database
after the client closes. Migration and subprocess tests use their own temporary
paths. Keep test suites serial; never point tests at a real application database.

Tests are grouped in `tests/backend/` (API, database, security and mocked AI),
`tests/frontend/` (JavaScript and standalone browser fixtures), `tests/e2e/`
(Playwright, including `bdd/`), and `tests/ai_evaluation/` (evaluation harness,
scenarios and offline regression tests). Shared fixtures remain in
`tests/conftest.py`. The default pytest command includes backend and offline
evaluation tests; E2E still requires the explicit opt-in below.

Formal versioning follows Semantic Versioning. `APP_VERSION` in `app/version.py`
is the source of truth for FastAPI metadata, `/version`, and the About page.

| Version | Meaning |
| --- | --- |
| `0.1.0-dev` | Retrospective label for development before `v0.1.0`; no release or Git tag existed for this label |
| `0.1.0` | First stable release, published as GitHub Release and annotated Git tag `v0.1.0` |
| `1.0.0-dev` | Current development application version |
| `1.0.0-rc.1` | Planned first release candidate |
| `1.0.0` | Next planned stable release, `v1.0.0` |

`v0.1.0` remains the published release. No release candidate or new Git tag has
been created yet. Affected Version may identify an observed development build,
such as `1.0.0-dev`; it is not populated automatically. Fix Version identifies
the released version containing a fix and remains blank while the fix is unreleased.

Python dependency installation does not install Node; the separate frontend
test commands below require it.

The AI Assist backend uses OpenAI GPT-6 Luna only when `OPENAI_API_KEY` is set in
the server environment and the optional SDK is installed. For real AI Assist,
optionally set `$env:OPENAI_API_KEY = "<your-api-key>"` in the same shell before
starting Uvicorn. No key or a blank key retains HTTP 503:
`AI assistance is not configured yet.` Configuration
is checked per request; no provider-switching variable or dotenv loader is used.
Keep keys outside repository files. Provider failures return a fixed HTTP 502
message without SDK details; clients are closed after use and automatic SDK
retries are disabled. Failed requests and outcomes with no usable suggestions
preserve form values and permit manual Create/Save and explicit AI Assist retry.
See traceability for REQ-023 evidence and remaining verification limits.

Configured requests return `{"outcome": "suggestions", "suggestions": {"title": "..."}}`
or `{"outcome": "no_usable_suggestions", "suggestions": {}}` after application
validation. They never save a bug. New Bug and eligible Edit Bug forms display
pending values in an `AI Suggestions` area, with current-value comparisons and
`Use`, `Dismiss`, `Use All`, and `Dismiss All` actions. Form values change only
when a suggestion is used; normal `Create`/`Save` actions persist them. Resolve
all pending suggestions before requesting AI Assist again. Cancelling, leaving,
or reloading discards pending suggestions, and late results cannot populate a
later form session. Empty successful outcomes provide feedback and permit retry.

Run all dependency-free frontend JavaScript tests separately:

```powershell
node --test tests/frontend/*.test.cjs
```

These use DOM substitutes, including CR/LF sanitization for text inputs, and
execute the actual page event handlers; they do not establish browser E2E coverage.

For the optional native browser fixtures, first check for a listener on port 8148
(for example, `Get-NetTCPConnection -State Listen -LocalPort 8148`). If occupied,
identify the owning process and configuration; do not reuse or terminate an
unidentified server. Once available, run
`node tests/frontend/native-input-server.cjs`, open
`http://127.0.0.1:8148/`, and choose **Run native input regressions** to verify
the actual form markup and native controls (12 New/Edit, Use/Use All, LF/CR/CRLF
cases). `/ui-style.test.html` provides the separate native style fixtures.
This server binds only to loopback and serves an explicit static route allowlist,
with no application database, application API, or provider access. Stop only the
fixture server you started, using Ctrl+C. It does not automate complete page
workflows. Backend tests mock provider calls and require no real API key. See
traceability for the REQ-020 browser checks and remaining gaps.

## Continuous integration

[CI](.github/workflows/ci.yml) runs on pull requests targeting `main`, pushes to
`main`, and manual `workflow_dispatch` runs from GitHub's **Actions** tab (once
the workflow is on the default branch). Three independent Ubuntu 24.04 jobs run:

- Python 3.14: the complete default pytest suite (currently 638 tests), including
  offline evaluation-harness regression tests, with a JUnit XML report.
- Node.js 24: all 99 JavaScript tests using Node's built-in test runner; no npm
  installation is needed.
- Python 3.14 and Chromium: all 24 opt-in Playwright tests, including the five
  executable BDD scenarios, on port 8148.

Jobs can run concurrently; tests within each Python job remain serial. Existing
fixtures create disposable SQLite databases and temporary directories. CI supplies
no OpenAI credentials, disables live evaluation opt-in and points any unmocked
SDK client at an unused loopback endpoint. Provider responses are mocked; CI does
not run live AI evaluations, use historical evaluation evidence or deploy.

Open **Actions → CI → a run** to inspect each job and its step logs. The run
summary provides `python-test-report` and `e2e-test-results` artifacts, including
JUnit XML even after test failures. E2E failures retain Playwright traces and
screenshots; frontend failures upload `frontend-failure-log`. Artifacts expire
after seven days; cancelled jobs or failures before report creation may have no
artifacts. The latest user-confirmed hosted milestone is **847 passing tests**
(724 Python + 99 JavaScript + 24 Playwright/BDD), with all three required checks
protecting `main`. Local evidence and the dated hosted confirmation are recorded in
[test execution](docs/test-execution.md#github-actions-ci--20-october-2026).

The separate [Postman API regression workflow](.github/workflows/postman.yml)
uses official Postman CLI **1.75.0** on the same PR/push triggers. It runs the
local collection against a fresh server from `postman/serve.py`, waits for HTTP
readiness and cleans up the owned server/runtime on exit. The collection validates
run identity before each request. No Postman API key or
cloud login is used. [Setup and cleanup details](postman/README.md#github-actions)
explain the workflow. The user-confirmed local CLI run passed **50/50 assertions**
with exit 0; **hosted Postman CI remains unverified** and is excluded from the
847-test milestone above.

## Python Playwright E2E tests

Install the optional E2E dependencies into the project virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-e2e.txt
.\.venv\Scripts\python.exe -m playwright install --list
```

The browser revision must match the installed Playwright package. If compatible
Chromium and headless-shell binaries are already listed, reuse them. Install
missing/incompatible binaries only when needed with
`.\.venv\Scripts\python.exe -m playwright install chromium`.

Normal `.\.venv\Scripts\python.exe -m pytest` runs collect the existing backend
suite and exclude `tests/e2e/`. Browser tests require explicit opt-in. For the
user's manual workflow on reserved port 8151:

```powershell
# Headless Chromium
.\.venv\Scripts\python.exe -m pytest tests/e2e --e2e --browser chromium
# Headed Chromium
.\.venv\Scripts\python.exe -m pytest tests/e2e --e2e --browser chromium --headed
```

Agent-driven runs must explicitly use approved port 8148:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/e2e --e2e --e2e-port 8148 --browser chromium
```

Browser tests use a deliberately small Page Object Model in `tests/e2e/pages.py`:
`BugForm` (New/Edit Bug fields, Create/Save/Cancel and AI suggestion review) and
`BugList` (project bug table, sorting, page size and pagination). Page objects
expose locators and user actions only; scenarios and assertions stay in the test
files. Less-reused pages use direct Playwright calls, and shared setup such as
`login`, `open_bug` and `detail` remains in `tests/e2e/helpers.py`.

The optional E2E dependencies include `pytest-bdd==8.1.0`. Exactly five scenarios
are explicitly bound in `tests/e2e/bdd/test_workflows.py`: successful registration,
project creation, non-owner project protection, QA/Developer bug lifecycle, and
AI suggestion review/save. Run or collect just these scenarios with:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/e2e/bdd --e2e --e2e-port 8148 --browser chromium --collect-only -q
.\.venv\Scripts\python.exe -m pytest tests/e2e/bdd --e2e --e2e-port 8148 --browser chromium -q
```

The four feature files contain **five scenarios total, all executable**:
`authentication.feature` (registration), `project_management.feature` (creation
and non-owner protection), `bug_lifecycle.feature`, and `ai_review.feature`.
There are no specifications-only BDD scenarios.
BDD uses the same fixtures, server and provider mock described below. It covers
representative workflows, not every AC variant or real-model quality. Results and
limitations are in the [cleanup execution record](docs/test-execution.md#bdd-feature-cleanup--19-october-2026).

Run suites serially. The fixture refuses an occupied port without contacting or
terminating its listener. Identify any existing owner/configuration before
continuing; the fixture never attaches to an existing application server. Ports
8148 and 8151 are the only supported choices. Do not run the static fixture server
at the same time on the selected port.

Each E2E invocation creates a new temporary directory/database, a dedicated FastAPI
process, and a fictional JWT secret. Before HTTP interaction, the parent verifies
the child's startup report: interpreter/launcher ownership, effective database
path, bound loopback socket, and a per-run identity also checked in the first
response. Windows uses a selector event loop in this test server to avoid the
observed Proactor reset-connection shutdown leak. Shutdown is explicit; forced
shutdown or temporary-directory cleanup failures fail the run.
Safety checks use runtime exceptions, so Python's optimized mode cannot disable
database configuration, server identity, or shutdown checks.

Tests use fresh browser contexts and unique fictional accounts/projects. API
requests seed prerequisites and verify persisted results through the same test
server; the journeys themselves exercise real pages and browser controls. External
browser requests are blocked. Inherited OpenAI credentials/configuration are
removed, and the server replaces only the SDK client's transport with an
in-memory deterministic mock. Actual authorization, context construction,
generation input, response validation, form review, and normal persistence still
run. No paid/external AI call occurs; outgoing server connections are blocked
after startup. Synthetic descriptions containing `E2E:failure` or `E2E:empty`
select provider-error or empty-result fixtures; these switches exist only in the
test server, never the application.

The initial scenarios cover authentication and logout protection, project
creation/rename/deletion, membership removal and unauthorized access, bug
creation/edit/assignment/deletion, Developer/QA lifecycle handoff with Pass/Fail
and reopening, sorting/pagination/navigation/page-size persistence, and AI
Use/Dismiss/bulk review, cancellation, persistence, failure, and retry. Exhaustive
validation and permission combinations remain in API/unit tests. No filtering
scenario is added because the application has no filtering feature. Chromium
coverage does not establish cross-browser, full accessibility, visual/theme,
real-model quality, or increment completion.

The suite now contains 15 scenarios, including Fix Version eligibility and form
reset across lifecycle states, and page-size preferences across projects and
users through navigation, reload, and logout/login. Focused JavaScript tests
cover invalid/blocked preference storage without changing browser permissions.

For failure artifacts, append `--tracing retain-on-failure --screenshot only-on-failure`.
Artifacts go to ignored `test-results/`; they contain fictional test data only.
