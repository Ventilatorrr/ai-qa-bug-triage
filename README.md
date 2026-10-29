# AI QA Bug Triage

A bug-tracking application with AI-assisted triage, built as a QA Automation and
AI QA portfolio project. Teams record bug reports, move them from Triage to
Closed and can ask AI Assist for suggested improvements, which a person
reviews before anything is saved. The application also tracked its own genuine
development defects.

The project demonstrates:

- requirements-based testing with traceability from every acceptance criterion
  to its test cases;
- automated API, frontend and browser testing with pytest, Node's test runner,
  Playwright and pytest-bdd, plus Postman API regression and JMeter smoke tests,
  all running in GitHub Actions;
- testing an AI feature: deterministic tests with a mocked provider, and
  separately approved real-model evaluations scored against fixed rubrics;
- defect management, manual and exploratory testing, and documented limitations.

It is built with FastAPI, SQLite and a plain HTML/CSS/JavaScript frontend.

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
| [Release runbook](docs/release-runbook.md) | Release candidate, staging and production steps |

## Features

- **Accounts:** registration with automatic login, login and logout; passwords
  are stored as hashes and sessions use signed access tokens.
- **Projects and roles:** project creation, renaming and deletion; members with
  Project Owner, QA Analyst and Developer roles and role-based permissions;
  QA Analysts and Developers can leave a project.
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
  development defects (a reviewed snapshot with account emails redacted).

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
| `DEMO_TOTAL_LIMIT` | Maximum number of stored Demos (default 1,000; maximum 2,000; `0` switches Try Demo off). Deleting expired Demos frees capacity. An invalid value makes Try Demo unavailable |
| `READ_ONLY_MODE` | `1` refuses every request except GET and HEAD with HTTP 503; used while deleting an account. Off by default |
| `DATABASE_NAME` | SQLite database path (default `bugtriage.db` in the working directory; use an absolute path on persistent storage when deployed) |

AI Assist sends the current form, up to five recently updated reports from the
same project and eligible assignee information to OpenAI (`gpt-6-luna`, Medium
reasoning, Fast service tier, `store=false`). Each form field sent to AI Assist
is limited to 5,000 characters, historical text is shortened to 1,000 characters,
and output is limited to 8,000 tokens. Requests over a daily limit return HTTP 429 without
calling the provider. Provider failures return a generic HTTP 502 message and
leave the form unchanged.

`POST /demo` creates a Demo in one database transaction: five normal accounts
with random, undisclosed passwords and name-like `@example.com` addresses, and
the two seeded projects from `app/demo_data/`. It returns the Project Owner's
token, and nothing is kept if any step fails. Demo creation is limited to 20
starts per hour and to `DEMO_TOTAL_LIMIT` stored Demos.

A cleanup at startup and then hourly deletes each Demo once it is seven days old
(its accounts, their projects, bugs and memberships, and their AI usage records),
one transaction per Demo, and deletes AI usage records from earlier UTC days. Operator
commands run in Render Shell: `python -m app.admin delete-account EMAIL` (a dry run;
`--confirm` requires `READ_ONLY_MODE=1`) deletes an ordinary account on request,
`status` lists Demos past the retention period and `run-retention` runs the cleanup
now. See the [release runbook](docs/release-runbook.md#4-rules).

Public endpoints are bounded: request bodies over 1 MiB are rejected; project
names and bug titles are limited to 255 characters, Affected and Fix Version to
50, and other bug text fields to 5,000; and at most two password hashes run at once
(further register, login or Try Demo requests get HTTP 503 and can retry).

## Running tests

Tests use fictional data and mocked AI responses; no API key is needed. Backend
tests use a fresh temporary SQLite database for each test, and each browser-test
run uses its own server and temporary database (see below). Keep suites serial
and never point tests at a real application database.

```powershell
Remove-Item Env:OPENAI_API_KEY -ErrorAction SilentlyContinue
.\.venv\Scripts\python.exe -m pytest
```

The default run includes `tests/backend/` (API, database, security and mocked
AI) and the offline AI evaluation harness in `tests/ai_evaluation/`.

Frontend JavaScript tests need Node.js 24. They use DOM substitutes, with no
server or database, and Node's built-in runner:

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

[Application CI](.github/workflows/application.yml) runs three jobs on pull
requests to `main` and pushes to `main`: the Python suite, the JavaScript suite
and the Playwright/BDD suite with Chromium. CI uses no OpenAI
credentials and does not run live AI evaluations. Test reports are uploaded as
workflow artifacts for seven days.

Separate workflows run the [Postman API regression suite](.github/workflows/postman.yml)
with Postman CLI 1.75.0 ([details](postman/README.md#github-actions)) and a short
[JMeter smoke test](.github/workflows/jmeter.yml). The repository's `main` ruleset
requires pull requests and lists all five jobs as required status checks.

## Deployment

Starting with v1.0.0, the release process builds a Docker image from an approved
commit with the manually triggered [Release image](.github/workflows/release-image.yml)
workflow and deploys it by digest to Render staging, then production. Settings,
rules and the smoke checklist are in the [release runbook](docs/release-runbook.md).

## Versioning

The project follows Semantic Versioning. `APP_VERSION` in `app/version.py` is the
source of truth for FastAPI metadata, `/version` and the About page.

Published releases:

| Version | Date | Release |
| --- | --- | --- |
| `0.1.0` | 21 September 2026 | Git tag and GitHub Release `v0.1.0` |
| `0.2.0` | 24 October 2026 | Core application GitHub development release `v0.2.0` |

Between releases, `APP_VERSION` carries a `-dev` label for the next version (for
example `1.0.0-dev`). A release candidate sets `APP_VERSION` to the release
version (for example `1.0.0`) and is identified by its Git tag and image tag
(for example `v1.0.0-rc.1` and `1.0.0-rc.1`). Development labels such as
`0.1.0-dev` and `0.2.0-dev` are not releases or Git tags; they and release-candidate
labels may appear as Affected Version.

Git tags and GitHub Releases record published versions. Affected Version is the
version in which a bug was observed; Fix Version is the release that includes, or
is planned to include, the fix.
