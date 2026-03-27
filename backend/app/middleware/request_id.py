from uuid import uuid4

from starlette.types import ASGIApp, Receive, Scope, Send


class RequestIdMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        request_id = str(uuid4())

        # Starlette 0.52+ stores scope["state"] as a plain dict;
        # Request.state wraps it in a State object on first access.
        scope.setdefault("state", {})
        scope["state"]["request_id"] = request_id

        async def send_wrapper(message: dict) -> None:
            if message.get("type") == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((b"x-request-id", request_id.encode("ascii")))
                message = {**message, "headers": headers}
            await send(message)

        # Exceptions propagate naturally so Sentry and FastAPI error handlers
        # see unhandled failures (unlike the previous except/swallow approach).
        await self.app(scope, receive, send_wrapper)
