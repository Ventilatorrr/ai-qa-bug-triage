"""Run the application with a temporary database and mocked AI responses."""

import argparse
import asyncio
import json
import os
from pathlib import Path
import socket
import sys
from threading import Thread


def event_loop():
    # The HTTP-only test server needs no Windows Proactor subprocess transports.
    # Selector transports avoid the observed reset-connection teardown leak.
    return asyncio.SelectorEventLoop() if sys.platform == "win32" else asyncio.new_event_loop()


def probe_port(port):
    """Raise OSError if any interface uses the port; never contacts a listener."""
    # Windows lets 127.0.0.1 coexist with 0.0.0.0 or [::] listeners, which would
    # then receive the origin's requests if the test server exited. Probe them all.
    family = socket.AF_INET6 if socket.has_dualstack_ipv6() else socket.AF_INET
    with socket.socket(family) as probe:
        if sys.platform == "win32":
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        if family == socket.AF_INET6:
            probe.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        probe.bind(("::" if family == socket.AF_INET6 else "0.0.0.0", port))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, choices=(8148, 8151), required=True)
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--identity", required=True)
    args = parser.parse_args()
    if not args.database.is_absolute():
        raise RuntimeError("E2E database path must be absolute.")
    path = args.database.resolve()
    if path.exists():
        raise RuntimeError("E2E database path must be new; existing databases cannot be used.")
    if os.environ.get("DATABASE_NAME") != str(path):
        raise RuntimeError("DATABASE_NAME must match the temporary E2E database path.")
    if not os.environ.get("JWT_SECRET_KEY", "").startswith("e2e-test-"):
        raise RuntimeError("E2E server requires a test-only JWT secret.")
    if "OPENAI_API_KEY" in os.environ:
        raise RuntimeError("Remove inherited provider credentials before starting the E2E server.")

    # Verify configuration before any application import or lifespan.
    from app import database, ai_triage
    from app.main import app
    import httpx2
    from openai import OpenAI
    import uvicorn

    if database.DATABASE_NAME != str(path):
        raise RuntimeError("Cached application configuration does not match the E2E database path.")

    def provider_response(request):
        body = json.loads(request.content)
        form = json.loads(body["input"][0]["content"])["current_form"]
        if "E2E:failure" in form["description"]:
            return httpx2.Response(500, json={"error": {"message": "Synthetic provider failure"}})
        if "E2E:empty" in form["description"]:
            suggestions = []
        else:
            suggestions = [
                {"field": "title", "value": f"Reviewed {form['title']}"},
                {"field": "description", "value": "Clear synthetic reproduction details"},
                {"field": "severity", "value": "Major"},
                {"field": "priority", "value": "High"},
            ]
        return httpx2.Response(
            200,
            json={
                "id": "resp_e2e", "object": "response", "created_at": 0,
                "model": "gpt-6-luna", "status": "completed",
                "output": [{
                    "id": "msg_e2e", "type": "message", "role": "assistant",
                    "status": "completed",
                    "content": [{
                        "type": "output_text",
                        "text": json.dumps({"suggestions": suggestions}),
                        "annotations": [],
                    }],
                }],
            },
        )

    def create_mock_client(key):
        return OpenAI(
            api_key="e2e-dummy-key", max_retries=0,
            http_client=httpx2.Client(transport=httpx2.MockTransport(provider_response)),
        )

    ai_triage.create_openai_client = create_mock_client
    os.environ["OPENAI_API_KEY"] = "e2e-dummy-key"

    def no_external_connection(*args, **kwargs):
        raise RuntimeError("External network access is disabled in the E2E server.")

    @app.middleware("http")
    async def identify_server(request, call_next):
        response = await call_next(request)
        response.headers["X-E2E-Identity"] = args.identity
        return response

    class E2EServer(uvicorn.Server):
        async def startup(self, sockets=None):
            await super().startup(sockets)
            if not self.started or not path.is_file():
                raise RuntimeError("E2E application did not start with its temporary database.")
            addresses = [
                sock.getsockname()[:2] for server in self.servers for sock in server.sockets
            ]
            if addresses != [("127.0.0.1", args.port)]:
                raise RuntimeError(f"E2E server bound unexpected addresses: {addresses}")
            # Windows creates a loopback socketpair while initializing asyncio.
            # Block outgoing connections after that, before announcing readiness.
            socket.socket.connect = no_external_connection
            socket.socket.connect_ex = no_external_connection
            print(json.dumps({
                "pid": os.getpid(), "parent_pid": os.getppid(),
                "database": database.DATABASE_NAME, "port": args.port,
                "identity": args.identity, "provider": "mock",
            }), flush=True)

    server = E2EServer(uvicorn.Config(
        app, host="127.0.0.1", port=args.port, loop="tests.e2e.server:event_loop",
        log_level="warning", access_log=False,
    ))

    def stop_on_parent_exit():
        sys.stdin.readline()
        server.should_exit = True

    Thread(target=stop_on_parent_exit, daemon=True).start()
    server.run()


if __name__ == "__main__":
    main()
