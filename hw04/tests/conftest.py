import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from datetime import datetime
from http import HTTPStatus
from pathlib import Path

from demo_service.api.main import create_app
from demo_service.api.contracts import RegisterUserRequest, UserResponse, UserAuthRequest
from demo_service.core.users import UserRole, UserService, UserInfo, password_is_longer_than_8
from demo_service.api.utils import initialize

## Uncomment this to turn-on `stable` test support
## pytest -m stable
# from .pytest_stable_files import *

@pytest.fixture()
def anyio_backend():  # specify the asynchronous backend
    return "asyncio"

@pytest.fixture()
async def app() -> FastAPI:
    app = create_app()
    async with initialize(app):
        # Add an additional user after initialization
        user_service = app.state.user_service
        user_service.register(
            UserInfo(
                username="existing_user",
                name="Existing User",
                birthdate="2000-01-01",
                password="existingUserPassword123"
            )
        )
        yield app

@pytest.fixture()
async def async_client(app: FastAPI):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest.fixture
def admin_credentials():
    return {"username": "admin", "password": "superSecretAdminPassword123"}

@pytest.fixture
def user_data():
    return {
        "username": "testuser",
        "name": "Test User",
        "birthdate": datetime.now().isoformat(),
        "password": "testPassword123",
    }
