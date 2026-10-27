# ai-qa-bug-triage

Bug triage application built as a QA portfolio project with FastAPI, SQLite and a
plain HTML/CSS/JavaScript frontend. It is used to demonstrate requirements-based
testing, traceability, API, frontend and browser automation, and evaluation of an
AI-assisted feature with a real model.

## Features

- **Accounts:** registration with automatic login, login and logout; passwords
  are stored as hashes and sessions use signed access tokens.
- **Projects and roles:** project creation, renaming and deletion; members with
  Project Owner, QA Analyst and Developer roles and role-based permissions.
- **Bug reports:** creation, editing, deletion, assignment, severity and
  priority, and a Triage → Open → Development → Testing → Closed lifecycle with
  resolutions and Fix Version.
- **Bug List:** sorting by every column, pagination and remembered page size.
- **AI Assist:** on request, a Project Owner or QA Analyst receives validated
  suggestions from OpenAI for the current New Bug or Triage Edit Bug form. Each
  suggestion is reviewed with `Use`, `Dismiss`, `Use All` or `Dismiss All`;
  nothing is saved until the user chooses `Create` or `Save`. Daily request
  limits bound usage.
- **Try Demo:** visitors can start a Demo from the Login page without
  registering. Each Demo gets its own generated team and two seeded projects:
  20 fictional E-Commerce bug reports and copies of this project's genuine
  development defects.

## QA artifacts

| Document | Contents |
| --- | --- |
| [Requirements](docs/requirements.md) | REQ, user story and acceptance-criteria specification |
| [Traceability matrix](docs/traceability-matrix.md) | Coverage assessment for every acceptance criterion |
| [Test cases](docs/test-cases.md) | Catalogue of TC IDs with implementation references |
| [Test execution](docs/test-execution.md) | Results, manual and real-AI testing, limitations |
| [Defect summary](docs/defect-summary.md) | Tracked defects and their resolutions |
| [QA strategy](docs/qa-strategy.md) and [AI testing strategy](docs/ai-testing-strategy.md) | Test approach and AI evaluation protocol |
| [Definition of Done](docs/definition-of-done.md) | Increment completion criteria |
| [Postman suite](postman/README.md) and [JMeter plan](jmeter/README.md) | API regression and performance checks |

## Setup

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

Open http://127.0.0.1:8000/login.html. If `py` is unavailable, use the path to
your Python 3.14 executable.

- `requirements.txt` contains the runtime dependencies, `requirements-ai.txt`
  adds the optional OpenAI SDK, and `requirements-dev.txt` includes both plus
  the Python test tools. SQLite is included with Python.
- `JWT_SECRET_KEY` is required and must not be blank. Use a long random value
  and keep it out of the repository. Changing it signs out all users.

### Configuration

| Variable | Purpose |
| --- | --- |
| `OPENAI_API_KEY` | Enables AI Assist. Without it, AI Assist returns HTTP 503 `AI assistance is not configured yet.` and the rest of the application works normally |
| `AI_DAILY_USER_LIMIT`, `AI_DAILY_GLOBAL_LIMIT` | Daily AI Assist limits per account and across all accounts, per UTC day (defaults 50 and 500; `0` disables AI Assist). An invalid value returns HTTP 503 for AI Assist only |

AI Assist sends the current form, up to five recently updated reports from the
same project and eligible assignee information to OpenAI (`gpt-6-luna`, Medium
reasoning, Fast service tier, `store=false`). Form text fields are limited to
5,000 characters, historical text is shortened to 1,000 characters, and output
is limited to 8,000 tokens. Requests over a daily limit return HTTP 429 without
calling the provider. Provider failures return a generic HTTP 502 message and
leave the form unchanged.

`POST /demo` creates a Demo in one database transaction: five normal accounts
with random, undisclosed passwords and name-like `@example.com` addresses, and
the two seeded projects from `app/demo_data/`. It returns the Project Owner's
token, and nothing is kept if any step fails. Demo creation is limited to 20
starts per hour and 1,000 stored Demos.

## Running tests

Tests use fictional data, a fresh temporary SQLite database for each test, and
mocked AI responses; no API key is needed. Keep suites serial and never point
tests at a real application database.

```powershell
Remove-Item Env:OPENAI_API_KEY -ErrorAction SilentlyContinue
.\.venv\Scripts\python.exe -m pytest
```

The default run includes `tests/backend/` (API, database, security and mocked
AI) and the offline AI evaluation harness in `tests/ai_evaluation/`.

Frontend JavaScript tests use DOM substitutes and Node's built-in runner:

```powershell
node --test tests/frontend/*.test.cjs
```

Optional native browser fixtures for form controls and styles are served by
`node tests/frontend/native-input-server.cjs` at `http://127.0.0.1:8148/`. The
server is static and has no database or API access.

## Python Playwright E2E tests

Install the optional E2E dependencies and check the browser binaries:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-e2e.txt
.\.venv\Scripts\python.exe -m playwright install --list
```

Install Chromium only if a compatible version is not listed:
`.\.venv\Scripts\python.exe -m playwright install chromium`.

Browser tests require explicit opt-in. Port 8148 is used for automated runs and
8151 for manual runs:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/e2e --e2e --e2e-port 8148 --browser chromium
# Headed manual run on the default port 8151
.\.venv\Scripts\python.exe -m pytest tests/e2e --e2e --browser chromium --headed
```

Each run starts its own FastAPI server with a new temporary database and
fictional JWT secret, and verifies the server's database path and identity
before any browser interaction. The fixture refuses a port that is already in
use. The OpenAI SDK transport is replaced with a deterministic mock, so the real
authorization, context, validation and review code runs without external calls.
For failure artifacts, add `--tracing retain-on-failure --screenshot only-on-failure`.

The tests use a small Page Object Model (`tests/e2e/pages.py`). They cover
authentication, project and member management, authorization, bug creation,
editing and lifecycle, Bug List sorting and pagination, AI suggestion review and
failure handling, and Try Demo. Coverage is Chromium-only.

Five executable [pytest-bdd](tests/e2e/bdd/test_workflows.py) scenarios cover
registration, project creation, non-owner protection, the bug lifecycle and AI
suggestion review:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/e2e/bdd --e2e --e2e-port 8148 --browser chromium -q
```

## Continuous integration

[Application CI](.github/workflows/application.yml) runs three required checks
on pull requests to `main` and pushes to `main`: the Python suite, the
JavaScript suite and the Playwright/BDD suite with Chromium. CI uses no OpenAI
credentials and does not run live AI evaluations. Test reports are uploaded as
workflow artifacts for seven days.

Separate workflows run the [Postman API regression suite](.github/workflows/postman.yml)
with Postman CLI 1.75.0 ([details](postman/README.md#github-actions)) and a short
[JMeter smoke test](.github/workflows/jmeter.yml).

## Versioning

The project follows Semantic Versioning. `APP_VERSION` in `app/version.py` is the
source of truth for FastAPI metadata, `/version` and the About page.

| Version | Meaning |
| --- | --- |
| `0.1.0-dev`, `0.2.0-dev` | Development-phase labels used for Affected Version; not releases or Git tags |
| `0.1.0` | Previous published release: GitHub Release and Git tag `v0.1.0` |
| `0.2.0` | Latest published release: core application GitHub development release `v0.2.0` |
| `1.0.0-dev` | Current version: development toward the first production release |
| `1.0.0-rc.1` | Planned production release candidate |
| `1.0.0` | Planned first production release with Try Demo, `v1.0.0` |

Git tags and GitHub Releases record published versions. Affected Version is the
version in which a bug was observed; Fix Version is the release that includes, or
is planned to include, the fix.
