import json
import os
from pathlib import Path
from queue import Empty, Queue
import subprocess
import sys
import tempfile
from threading import Thread
from urllib.parse import urlsplit
from urllib.request import urlopen
from uuid import uuid4

import jwt
import pytest

from tests.e2e.helpers import api_call, unique_name
from tests.e2e.server import probe_port


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session")
def e2e_base_url(pytestconfig):
    port = pytestconfig.getoption("--e2e-port")
    origin = f"http://127.0.0.1:{port}"
    # Binding checks availability without contacting an unknown server.
    try:
        probe_port(port)
    except OSError as exc:
        pytest.fail(
            f"Port {port} is unavailable. Identify its owner/configuration; "
            f"no server was reused. {exc}"
        )

    with tempfile.TemporaryDirectory(prefix="ai-qa-e2e-") as directory:
        database_path = (Path(directory) / "e2e.db").resolve()
        identity = uuid4().hex
        env = os.environ.copy()
        env.update(DATABASE_NAME=str(database_path), JWT_SECRET_KEY=f"e2e-test-{uuid4().hex}")
        for name in ("OPENAI_API_KEY", "OPENAI_BASE_URL", "OPENAI_ORG_ID", "OPENAI_PROJECT_ID"):
            env.pop(name, None)

        with (Path(directory) / "server.log").open("w+", encoding="utf-8") as log:
            server = subprocess.Popen(
                [
                    sys.executable, "-m", "tests.e2e.server", "--port", str(port),
                    "--database", str(database_path), "--identity", identity,
                ],
                cwd=PROJECT_ROOT, env=env,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=log, text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )
            ready = Queue()
            # A reader thread allows a startup deadline for the Windows stdout pipe.
            reader = Thread(target=lambda: ready.put(server.stdout.readline()), daemon=True)
            reader.start()
            try:
                try:
                    line = ready.get(timeout=15)
                except Empty:
                    pytest.fail("E2E server did not signal readiness within 15 seconds.")
                if not line:
                    log.seek(0)
                    pytest.fail(f"E2E server exited before readiness: {log.read()}")
                report = json.loads(line)
                # Windows venv launchers spawn the interpreter as a direct child.
                if report["pid"] != server.pid and report["parent_pid"] != server.pid:
                    raise RuntimeError("Readiness report came from an unexpected process.")
                expected = {
                    "database": str(database_path),
                    "port": port,
                    "identity": identity,
                    "provider": "mock",
                }
                if any(report[key] != value for key, value in expected.items()):
                    raise RuntimeError(f"E2E server configuration mismatch: {report}")
                if server.poll() is not None:
                    raise RuntimeError("E2E server exited after reporting readiness.")

                # Verify config, bound socket and child PID before contacting the origin.
                with urlopen(f"{origin}/version", timeout=5) as response:
                    if (
                        response.status != 200
                        or response.headers.get("X-E2E-Identity") != identity
                    ):
                        raise RuntimeError("HTTP response did not identify the expected E2E server.")

                yield origin

                if server.poll() is not None:
                    raise RuntimeError("E2E server exited during testing.")
            finally:
                forced = False
                if server.poll() is None:
                    server.stdin.write("stop\n")
                    server.stdin.flush()
                    server.stdin.close()
                    try:
                        server.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        if sys.platform == "win32":
                            subprocess.run(
                                ["taskkill", "/PID", str(server.pid), "/T", "/F"],
                                check=True, capture_output=True,
                            )
                        else:
                            server.kill()
                        server.wait(timeout=5)
                        forced = True
                else:
                    server.stdin.close()
                server.stdout.close()
                reader.join(timeout=5)
                if reader.is_alive():
                    raise RuntimeError("Server readiness reader did not stop.")
                if forced:
                    log.seek(0)
                    raise RuntimeError(f"E2E server required forced shutdown: {log.read()}")


@pytest.fixture(scope="session")
def base_url(e2e_base_url):
    return e2e_base_url


@pytest.fixture(autouse=True)
def local_browser_only(context, e2e_base_url):
    origin = urlsplit(e2e_base_url)

    def local_route(route):
        target = urlsplit(route.request.url)
        if (target.scheme, target.netloc) == (origin.scheme, origin.netloc):
            route.continue_()
        else:
            route.abort()

    context.route("**/*", local_route)


@pytest.fixture
def e2e_api(playwright, e2e_base_url):
    api = playwright.request.new_context(base_url=e2e_base_url)
    try:
        yield api
    finally:
        api.dispose()


@pytest.fixture
def account_factory(e2e_api):
    def create():
        account = {"email": f"{unique_name('e2e')}@example.com", "password": "TestPassword123!"}
        api_call(e2e_api, "POST", "/register", expected=201, data=account)
        token = api_call(e2e_api, "POST", "/login", data=account)["access_token"]
        user_id = jwt.decode(token, options={"verify_signature": False})["user_id"]
        return account | {"token": token, "id": user_id}

    return create


@pytest.fixture
def workspace(e2e_api, account_factory):
    owner, developer, qa = (account_factory() for _ in range(3))
    project = api_call(
        e2e_api, "POST", "/projects", owner, expected=201,
        data={"name": unique_name("E2E Project")},
    )
    for account, role in ((developer, "Developer"), (qa, "QA Analyst")):
        api_call(
            e2e_api, "POST", f"/projects/{project['id']}/members", owner, expected=201,
            data={"email": account["email"], "role": role},
        )
    return {"owner": owner, "developer": developer, "qa": qa, "project": project}
