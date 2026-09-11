# ai-qa-bug-triage
Bug triage application built as a QA portfolio project with FastAPI, SQLite, and a plain HTML/CSS/JavaScript frontend.

Authentication, project/member management, and bug-management APIs through REQ-017 are implemented. The project page supports bug creation, listing, and interactive sorting by all seven columns; browser verification of sorting remains outstanding. Individual bug management in the browser and Increment 3 AI-assisted triage remain pending.

Current automated coverage uses pytest and FastAPI TestClient. BDD feature files are specification examples, not executable tests. Playwright, Postman, AI testing, and CI/CD are planned portfolio work; they are not established coverage in this repository.

See [requirements](docs/requirements.md), [traceability](docs/traceability-matrix.md), and the [QA strategy](docs/qa-strategy.md) for current behavior and verification gaps. Historical working notes and requirements_old.md are not the current specification.

For the existing configured Windows environment, run from the repository root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000/login.html. A reproducible dependency manifest and clean-machine setup instructions remain outstanding; the command above assumes the existing virtual environment. Tests use a fixed disposable test_bugtriage.db filename and must not run concurrently. Formal versioning has not started.
