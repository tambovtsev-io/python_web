import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from http import HTTPStatus

from demo_service.api.main import create_app
from demo_service.api.contracts import RegisterUserRequest, UserResponse, UserAuthRequest
from demo_service.core.users import UserRole

app = create_app()
client = TestClient(app)


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


def test_register_user(user_data):
    """Test user registration"""
    response = client.post("/user-register", json=user_data)
    assert response.status_code == HTTPStatus.OK
    user = UserResponse(**response.json())
    assert user.username == user_data["username"]
    assert user.name == user_data["name"]
    assert user.role == UserRole.USER


@pytest.mark.parametrize(
    "invalid_data, expected_error",
    [
        (
            {"username": "testuser", "name": "Test User", "birthdate": "2000-01-01"},
            "1 validation error for RegisterUserRequest",
        ),
        (
            {
                "username": "testuser",
                "name": "Test User",
                "birthdate": "2000-01-01",
                "password": "short",
            },
            "invalid password",
        ),
    ],
)
def test_register_user_invalid_data(invalid_data, expected_error):
    """Test user registration with invalid data"""
    response = client.post("/user-register", json=invalid_data)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert expected_error in response.text


def test_get_user_by_id(user_data, admin_credentials):
    """Test getting user by ID"""
    # Register a user first
    register_response = client.post("/user-register", json=user_data)
    user_id = register_response.json()["uid"]

    # Get user by ID
    response = client.post(
        "/user-get",
        params={"id": user_id},
        auth=(admin_credentials["username"], admin_credentials["password"]),
    )
    assert response.status_code == HTTPStatus.OK
    user = UserResponse(**response.json())
    assert user.uid == user_id
    assert user.username == user_data["username"]


def test_get_user_by_username(user_data, admin_credentials):
    """Test getting user by username"""
    # Register a user first
    client.post("/user-register", json=user_data)

    # Get user by username
    response = client.post(
        "/user-get",
        params={"username": user_data["username"]},
        auth=(admin_credentials["username"], admin_credentials["password"]),
    )
    assert response.status_code == HTTPStatus.OK
    user = UserResponse(**response.json())
    assert user.username == user_data["username"]


def test_get_user_unauthorized():
    """Test getting user without authentication"""
    response = client.post("/user-get", params={"id": 1})
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_promote_user(user_data, admin_credentials):
    """Test promoting a user to admin"""
    # Register a user first
    register_response = client.post("/user-register", json=user_data)
    user_id = register_response.json()["uid"]

    # Promote user to admin
    response = client.post(
        "/user-promote",
        params={"id": user_id},
        auth=(admin_credentials["username"], admin_credentials["password"]),
    )
    assert response.status_code == HTTPStatus.OK

    # Verify user role
    get_user_response = client.post(
        "/user-get",
        params={"id": user_id},
        auth=(admin_credentials["username"], admin_credentials["password"]),
    )
    promoted_user = UserResponse(**get_user_response.json())
    assert promoted_user.role == UserRole.ADMIN


def test_promote_user_unauthorized(user_data):
    """Test promoting a user without admin credentials"""
    # Register a user first
    register_response = client.post("/user-register", json=user_data)
    user_id = register_response.json()["uid"]

    # Attempt to promote user without admin credentials
    response = client.post(
        "/user-promote",
        params={"id": user_id},
        auth=(user_data["username"], user_data["password"]),
    )
    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.parametrize(
    "query_params, expected_status",
    [
        ({"id": 1, "username": "testuser"}, HTTPStatus.BAD_REQUEST),
        ({}, HTTPStatus.BAD_REQUEST),
        ({"id": 9999}, HTTPStatus.NOT_FOUND),
        ({"username": "nonexistent"}, HTTPStatus.NOT_FOUND),
    ],
)
def test_get_user_edge_cases(query_params, expected_status, admin_credentials):
    """Test edge cases for getting user"""
    response = client.post(
        "/user-get",
        params=query_params,
        auth=(admin_credentials["username"], admin_credentials["password"]),
    )
    assert response.status_code == expected_status


def test_register_duplicate_username(user_data):
    """Test registering a user with an existing username"""
    # Register a user
    client.post("/user-register", json=user_data)

    # Attempt to register another user with the same username
    response = client.post("/user-register", json=user_data)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "username is already taken" in response.text


def test_promote_nonexistent_user(admin_credentials):
    """Test promoting a non-existent user"""
    response = client.post(
        "/user-promote",
        params={"id": 9999},
        auth=(admin_credentials["username"], admin_credentials["password"]),
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "user not found" in response.text
