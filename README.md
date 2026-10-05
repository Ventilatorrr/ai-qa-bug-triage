# ai-qa-bug-triage
Bug triage application built as a QA portfolio project with FastAPI, SQLite, and a plain HTML/CSS/JavaScript frontend.

Authentication, project/member management, and bug-management APIs through REQ-017 are implemented. The project page supports bug creation, listing, and interactive sorting by all seven columns; browser verification of sorting remains outstanding. Individual bug management in the browser and Increment 3 AI-assisted triage remain pending.

Current automated coverage uses pytest and FastAPI TestClient. BDD feature files are specification examples, not executable tests. Playwright, Postman, AI testing, and CI/CD are planned portfolio work; they are not established coverage in this repository.

See [requirements](docs/requirements.md), [traceability](docs/traceability-matrix.md), and the [QA strategy](docs/qa-strategy.md) for current behavior and verification gaps. Historical working notes and requirements_old.md are not the current specification.

For the existing configured Windows environment, run from the repository root:

```powershell
$env:JWT_SECRET_KEY = "your-secure-random-secret"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

`JWT_SECRET_KEY` is required and must not be empty or whitespace-only. The
application will refuse to sign or verify tokens without a nonblank value.
Use a long, random value and do not commit it to the repository. Changing the
secret invalidates all existing tokens; users must log in again.

Open http://127.0.0.1:8000/login.html. A reproducible dependency manifest and clean-machine setup instructions remain outstanding; the command above assumes the existing virtual environment. Tests use a fixed disposable test_bugtriage.db filename and must not run concurrently. Formal versioning has not started.

The AI Assist backend uses OpenAI GPT-6 Luna only when `OPENAI_API_KEY` is set in
the server environment. Install its optional SDK dependency with
`.\.venv\Scripts\python.exe -m pip install -r requirements-ai.txt`. No key or a
blank key retains HTTP 503: `AI assistance is not configured yet.` Configuration
is checked per request; no provider-switching variable or dotenv loader is used.
Keep keys outside repository files. Provider failures return a fixed HTTP 502
message without SDK details; clients are closed after use and automatic SDK
retries are disabled. Full REQ-023 recovery remains pending.

Configured requests return `{"outcome": "suggestions", "suggestions": {"title": "..."}}`
or `{"outcome": "no_usable_suggestions", "suggestions": {}}` after application
validation. They never save a bug. New Bug and eligible Edit Bug forms display
pending values in an `AI Suggestions` area, with current-value comparisons and
`Use`, `Dismiss`, `Use All`, and `Dismiss All` actions. Form values change only
when a suggestion is used; normal `Create`/`Save` actions persist them. Resolve
all pending suggestions before requesting AI Assist again. Cancelling, leaving,
or reloading discards pending suggestions, and late results cannot populate a
later form session. Empty successful outcomes provide feedback and permit retry.

Run the dependency-free frontend unit tests with
`node --test tests/frontend/ai-assist.test.cjs tests/frontend/form-session.test.cjs`.
These use DOM substitutes, including CR/LF sanitization for text inputs, and
execute the actual page event handlers. Run `node tests/frontend/native-input-server.cjs`,
open `http://127.0.0.1:8128/`, and choose **Run native input regressions** to verify
the actual form markup and native controls (12 New/Edit, Use/Use All, LF/CR/CRLF
cases). This static test server uses no application database or provider and
does not automate complete page workflows. Backend tests mock provider calls and require no
real API key. See traceability for the REQ-020 browser checks and remaining gaps.
