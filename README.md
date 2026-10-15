# ai-qa-bug-triage
Bug triage application built as a QA portfolio project with FastAPI, SQLite, and a plain HTML/CSS/JavaScript frontend.

Authentication, project/member management, and bug-management APIs through REQ-017 are implemented. The frontend supports bug creation, viewing, editing, deletion, lifecycle actions, sorting, and pagination. Increment 3 AI Assist is implemented with explicit suggestion review and normal Create/Save persistence. Broader browser verification and increment completion remain outstanding; see traceability for evidence and gaps.

Current automated coverage uses pytest/FastAPI TestClient, database integration tests, mocked AI provider tests, and dependency-free frontend JavaScript tests. BDD feature files are specification examples, not executable tests. Playwright E2E automation, Postman, real-model evaluation, and CI/CD remain planned work.

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
