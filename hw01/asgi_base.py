import json
from http import HTTPStatus
from typing import Callable, Awaitable, Any

class ASGIServerBase:
    async def __call__(
        self,
        scope: dict[str, Any],
        receive: Callable[[], Awaitable[dict[str, Any]]],
        send: Callable[[dict[str, Any]], Awaitable[None]]
    ) -> None:
        if scope['type'] == 'http':
            await self.handle_request(scope, receive, send)
        else:
            await self.default_response(send)

    async def handle_request(
        self,
        scope: dict[str, Any],
        receive: Callable[[], Awaitable[dict[str, Any]]],
        send: Callable[[dict[str, Any]], Awaitable[None]]
    ) -> None:
        """Override this method in the inherited class to define route-specific logic."""
        raise NotImplementedError("Subclasses must implement this method.")

    async def receive_body(
        self,
        send,
        receive: Callable[[], Awaitable[dict[str, Any]]]
    ) -> dict[str, Any]:
        """Handles receiving the body from an incoming request."""
        body: bytes = b""
        more_body: bool = True
        while more_body:
            message: dict[str, Any] = await receive()
            body += message.get("body", b"")
            more_body = message.get("more_body", False)
        try:
            body = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            return self.send_error(send, HTTPStatus.BAD_REQUEST, "Invalid JSON payload.")
        return body

    async def send_json(
        self,
        send: Callable[[dict[str, Any]], Awaitable[None]],
        data: dict[str, Any],
        status: HTTPStatus = HTTPStatus.OK
    ) -> None:
        """Send JSON response to the client."""
        body: bytes = json.dumps(data).encode('utf-8')
        await send({
            "type": "http.response.start",
            "status": status.value,
            "headers": [
                [b"content-type", b"application/json"]
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body
        })

    async def send_error(
        self,
        send: Callable[[dict[str, Any]], Awaitable[None]],
        status: HTTPStatus,
        message: str
    ) -> None:
        """Send an error response with a custom message."""
        await self.send_json(send, {"error": message}, status=status)

    async def default_response(
        self,
        send: Callable[[dict[str, Any]], Awaitable[None]]
    ) -> None:
        """Send default 404 response for undefined routes."""
        await self.send_json(send, {"error": "Not found"}, status=HTTPStatus.NOT_FOUND)
