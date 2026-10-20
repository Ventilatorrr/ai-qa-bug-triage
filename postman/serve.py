"""Own a disposable Postman server; never accept a caller-supplied database."""

import asyncio
import json
import os
from pathlib import Path
import secrets
import socket
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
PORT = 8148


def event_loop():
    return asyncio.SelectorEventLoop() if sys.platform == "win32" else asyncio.new_event_loop()


def main():
    if len(sys.argv) != 1:
        raise SystemExit("Usage: python postman/serve.py (no options)")

    # Reserve the approved origin before imports, database startup or HTTP.
    # A busy port is a hard stop: never probe, reuse or terminate its process.
    listener = socket.socket()
    try:
        listener.bind(("127.0.0.1", PORT))
    except OSError:
        listener.close()
        raise SystemExit("Port 8148 is unavailable. Preserve the existing process and stop here.")
    listener.listen(128)
    runtime = ROOT / "postman/.runtime"
    runtime.mkdir(exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix="run-", dir=runtime) as directory:
            run_dir = Path(directory).resolve()
            database_path = run_dir / "disposable.sqlite3"
            assert not database_path.exists()
            run_id = secrets.token_hex(16)
            run_key = secrets.token_hex(32)
            os.environ["DATABASE_NAME"] = str(database_path)
            os.environ["JWT_SECRET_KEY"] = secrets.token_urlsafe(48)
            os.environ.pop("OPENAI_API_KEY", None)
            os.environ["OPENAI_BASE_URL"] = "http://127.0.0.1:9/v1"
            os.environ["AI_EVALUATION_ALLOW_LIVE"] = "0"

            def audit(event, values):
                if event == "sqlite3.connect" and str(values[0]) not in (str(database_path), ":memory:"):
                    raise RuntimeError("Postman server refused a non-test database.")
                if event == "socket.connect" and (
                    not isinstance(values[1], tuple) or values[1][0] not in ("127.0.0.1", "::1")
                ):
                    raise RuntimeError("Outgoing connections are disabled in the Postman server.")

            sys.addaudithook(audit)
            sys.path.insert(0, str(ROOT))
            os.chdir(ROOT)
            from app import database
            from app.main import app
            import uvicorn

            if database.DATABASE_NAME != str(database_path) or database_path.exists():
                raise RuntimeError("Fresh disposable database configuration could not be verified.")

            # Test-only ASGI wrapper. Production application code is unchanged.
            async def isolated(scope, receive, send):
                if scope["type"] != "http":
                    return await app(scope, receive, send)
                headers = dict(scope["headers"])
                valid = secrets.compare_digest(headers.get(b"x-postman-run", b""), run_key.encode())
                if not valid:
                    status, body = 403, {"detail": "Disposable server run key required."}
                elif scope["path"] == "/__postman__/identity":
                    status, body = 200, {"run_id": run_id, "database": "disposable", "ai": "disabled"}
                else:
                    return await app(scope, receive, send)
                await send({"type": "http.response.start", "status": status,
                            "headers": [(b"content-type", b"application/json")]})
                await send({"type": "http.response.body", "body": json.dumps(body).encode()})

            environment = json.loads((ROOT / "postman/Isolated.postman_environment.json").read_text())
            environment["name"] = f"Disposable Postman {run_id[:8]}"
            for entry in environment["values"]:
                if entry["key"] in ("run_id", "run_key"):
                    entry["value"] = {"run_id": run_id, "run_key": run_key}[entry["key"]]
            environment_path = run_dir / "Isolated.postman_environment.json"
            environment_path.write_text(json.dumps(environment, indent=2) + "\n", encoding="utf-8")
            server = uvicorn.Server(uvicorn.Config(
                isolated, host="127.0.0.1", port=PORT, loop=event_loop,
                log_level="warning", access_log=False,
            ))

            print(f"Owned disposable server: PID {os.getpid()}, http://127.0.0.1:{PORT}", flush=True)
            print(f"Verified new database: {database_path}", flush=True)
            print(f"Import this generated environment: {environment_path}", flush=True)
            print("External connections blocked; AI unconfigured. Ctrl+C stops and disposes this run.", flush=True)
            try:
                server.run(sockets=[listener])
            except KeyboardInterrupt:
                # Uvicorn re-raises Ctrl+C after its normal shutdown on Python 3.14.
                pass
        if run_dir.exists():
            raise RuntimeError("Disposable run directory was not removed.")
        print("Disposable run directory, credentials and SQLite database removed.", flush=True)
        return 0
    finally:
        listener.close()


if __name__ == "__main__":
    raise SystemExit(main())
