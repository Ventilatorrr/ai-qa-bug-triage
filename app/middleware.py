import os

from fastapi import HTTPException
from starlette.responses import JSONResponse


# The largest valid request (a complete bug form) is about 110 KB of UTF-8.
MAX_REQUEST_BODY_BYTES = 1024 * 1024
TOO_LARGE_MESSAGE = "Request body is too large."


class RequestBodyTooLarge(HTTPException):
    # An HTTPException, so FastAPI's body parsing re-raises it as a 413 instead of a generic 400.
    def __init__(self):
        super().__init__(status_code=413, detail=TOO_LARGE_MESSAGE)


class RequestBodyLimit:
    """Reject oversized bodies before FastAPI reads them, including before authentication."""

    def __init__(self, app, limit=MAX_REQUEST_BODY_BYTES):
        self.app = app
        self.limit = limit

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        declared = dict(scope["headers"]).get(b"content-length")
        if declared is not None and declared.isdigit() and int(declared) > self.limit:
            await self._reject(scope, receive, send)
            return

        received = 0
        response_started = False

        # Bodies without a declared length are counted as they stream in.
        async def limited_receive():
            nonlocal received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > self.limit:
                    raise RequestBodyTooLarge
            return message

        async def tracked_send(message):
            nonlocal response_started
            response_started = response_started or message["type"] == "http.response.start"
            await send(message)

        try:
            await self.app(scope, limited_receive, tracked_send)
        except RequestBodyTooLarge:
            if response_started:
                raise
            await self._reject(scope, receive, send)

    @staticmethod
    async def _reject(scope, receive, send):
        response = JSONResponse({"detail": TOO_LARGE_MESSAGE}, status_code=413)
        await response(scope, receive, send)


READ_ONLY_MESSAGE = "The application is temporarily read-only for maintenance. Please try again shortly."


def read_only_mode():
    # Read per request, like the AI limits; only "1" turns it on.
    return (os.getenv("READ_ONLY_MODE") or "").strip() == "1"


class ReadOnlyMode:
    """While READ_ONLY_MODE=1, refuse every request that could write, before any handler runs.

    Manual account deletion runs only in this mode, so no request can write concurrently (AC-026.3).
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope["method"] not in ("GET", "HEAD") and read_only_mode():
            response = JSONResponse({"detail": READ_ONLY_MESSAGE}, status_code=503)
            await response(scope, receive, send)
            return
        await self.app(scope, receive, send)


SECURITY_HEADERS = [
    (b"x-content-type-options", b"nosniff"),
    (b"x-frame-options", b"DENY"),
    (b"content-security-policy", b"frame-ancestors 'none'"),
    (b"referrer-policy", b"same-origin"),
]


class SecurityHeaders:
    """Add a minimal set of browser security headers to every HTTP response."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                names = {name.lower() for name, _ in message.get("headers", [])}
                message["headers"] = [
                    *message.get("headers", []),
                    *(header for header in SECURITY_HEADERS if header[0] not in names),
                ]
            await send(message)

        await self.app(scope, receive, send_with_headers)
