import uvicorn
import math
from typing import Callable, Awaitable, Any
from http import HTTPStatus
from urllib.parse import parse_qs

from asgi_base import ASGIServerBase


class SimpleMathASGIServer(ASGIServerBase):
    """
    An ASGI-based math server providing simple mathematical operations via HTTP endpoints.

    Endpoints:
    ----------
    1. GET /factorial?n={number}
        - Returns the factorial of a non-negative integer `n`.
        - Errors: 400 (if `n` is negative), 422 (if `n` is missing or invalid).

    2. GET /fibonacci/{n}
        - Returns the `n`th Fibonacci number.
        - Errors: 400 (if `n` is negative), 422 (if `n` is invalid).

    3. GET /mean
        - Accepts a JSON array of floats and returns their mean.
        - Errors: 400 (if the array is empty), 422 (if the body is not a valid float array).
    """
    async def handle_request(self) -> None:
        path: str = self.scope["path"]

        method: str = self.scope["method"]
        if method != "GET":
            await self.send_error(
                HTTPStatus.NOT_FOUND, f"Method {method} not allowed."
            )
            return

        if path.startswith("/factorial"):
            await self.get_factorial()
        elif path.startswith("/fibonacci/"):
            await self.get_fibonacci()
        elif path == "/mean":
            await self.get_mean()
        else:
            await self.default_response()

    async def get_factorial(self) -> None:
        query_string = self.scope.get('query_string', b'').decode('utf-8')
        query_params = parse_qs(query_string)
        n_str = query_params.get('n', [None])[0]

        n = await self.handle_positive_integer(n_str)
        if n is None: # already sent error
            return

        result = math.factorial(n)
        await self.send_json({"result": result})

    async def get_fibonacci(self) -> None:
        path: str = self.scope["path"]
        n_str = path.split('/')[-1]

        n = await self.handle_positive_integer(n_str)
        if not isinstance(n, int):
            return

        result = self.fibonacci(n)
        await self.send_json({"result": result})

    async def get_mean(self) -> None:
        body = await self.receive_body()
        if body is None:
            return

        # Validate that body is a list of floats
        try:
            numbers = body if isinstance(body, list) else []
            numbers = [float(num) for num in numbers]
        except ValueError:
            return await self.send_error(HTTPStatus.UNPROCESSABLE_ENTITY, "Body must be an array of floats.")


        if len(numbers) == 0:
            await self.send_error(HTTPStatus.BAD_REQUEST, "Array of floats cannot be empty.")
        else:
            result = sum(numbers) / len(numbers)
            await self.send_json({"result": result})

    async def handle_positive_integer(self, value: str) -> int:
        """
        Helper function to validate if a given value is a non-negative integer.
        """
        msg = "Value must be a positive integer."
        try:
            value = int(value)
        except Exception as e:
            return await self.send_error(HTTPStatus.UNPROCESSABLE_ENTITY, msg)


        n = int(value)
        if n < 0:
            return await self.send_error(HTTPStatus.BAD_REQUEST, msg)
        return n

    def fibonacci(self, n: int) -> int:
        # https://en.wikipedia.org/wiki/Fibonacci_sequence#Binet's_formula
        # phi = ( 1 + sqrt(5) ) / 2
        # fib = floor (phi^n/sqrt(5) + 0.5)
        phi = (1 + math.sqrt(5)) / 2
        f = (phi**n) / math.sqrt(5)
        return int(f + 0.5)  # round to nearest integer


if __name__ == "__main__":
    uvicorn.run(SimpleMathASGIServer(), host="localhost", port=8000)
