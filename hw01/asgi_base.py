import json
from http import HTTPStatus
from typing import Callable, Awaitable, Any

class ASGIServerBase:
    """
    A base class for creating ASGI applications.

    Responsibilities:
    -----------------
    - Handles ASGI lifecycle by processing incoming HTTP requests.
    - Provides utility methods for handling JSON request bodies and sending JSON responses.
    """
    def __init__(self):
        self.scope: dict[str, Any] = None
        self.receive: Callable[[], Awaitable[dict[str, Any]]] = None
        self.send: Callable[[dict[str, Any]], Awaitable[None]] = None

    async def __call__(
        self,
        scope: dict[str, Any],
        receive: Callable[[], Awaitable[dict[str, Any]]],
        send: Callable[[dict[str, Any]], Awaitable[None]]
    ) -> None:
        self.scope = scope
        self.receive = receive
        self.send = send
        if scope['type'] == 'http':
            await self.handle_request()
        else:
            await self.default_response()

    async def handle_request(self) -> None:
        """Override this method to define route-specific logic."""
        raise NotImplementedError("Subclasses must implement this method.")

    async def receive_body(self) -> dict[str, Any] | None:
        """Handles receiving the body from an incoming request."""
        body: bytes = b""
        more_body: bool = True
        while more_body:
            message: dict[str, Any] = await self.receive()
            body += message.get("body", b"")
            more_body = message.get("more_body", False)

        try:
            body_json = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            return await self.send_error(HTTPStatus.UNPROCESSABLE_ENTITY, "Invalid JSON payload.")
        return body_json

    async def send_json(
        self,
        data: dict[str, Any],
        status: HTTPStatus = HTTPStatus.OK
    ) -> None:
        """Send JSON response to the client."""
        body: bytes = json.dumps(data).encode('utf-8')
        await self.send({
            "type": "http.response.start",
            "status": status.value,
            "headers": [
                [b"content-type", b"application/json"]
            ],
        })
        await self.send({
            "type": "http.response.body",
            "body": body
        })

    async def send_error(
        self,
        status: HTTPStatus,
        message: str
    ) -> None:
        """Send an error response with a custom message."""
        await self.send_json({"error": message}, status=status)

    async def default_response(self) -> None:
        """Send default 404 response for undefined routes."""
        await self.send_error(HTTPStatus.NOT_FOUND, "Not found")
