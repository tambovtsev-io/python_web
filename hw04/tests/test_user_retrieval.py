import pytest
from http import HTTPStatus
from demo_service.api.contracts import UserResponse

@pytest.mark.anyio
async def test_get_user_by_id(async_client, user_data, admin_credentials):
    """Test getting user by ID"""
    # Register a user first
    register_response = await async_client.post("/user-register", json=user_data)
    user_id = register_response.json()["uid"]

    # Get user by ID
    response = await async_client.post(
        "/user-get",
        params={"id": user_id},
        auth=(admin_credentials["username"], admin_credentials["password"]),
    )
    assert response.status_code == HTTPStatus.OK
    user = UserResponse(**response.json())
    assert user.uid == user_id
    assert user.username == user_data["username"]


@pytest.mark.anyio
async def test_get_user_by_username(async_client, user_data, admin_credentials):
    """Test getting user by username"""
    # Register a user first
    await async_client.post("/user-register", json=user_data)

    # Get user by username
    response = await async_client.post(
        "/user-get",
        params={"username": user_data["username"]},
        auth=(admin_credentials["username"], admin_credentials["password"]),
    )
    assert response.status_code == HTTPStatus.OK
    user = UserResponse(**response.json())
    assert user.username == user_data["username"]


@pytest.mark.anyio
async def test_get_user_unauthorized(async_client):
    """Test getting user without authentication"""
    response = await async_client.post("/user-get", params={"id": 1})
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.anyio
async def test_get_user_authentication(async_client, user_data):
    # Register a user
    await async_client.post("/user-register", json=user_data)

    # Test with correct credentials
    response = await async_client.post(
        "/user-get",
        params={"username": user_data["username"]},
        auth=(user_data["username"], user_data["password"])
    )
    assert response.status_code == HTTPStatus.OK

    # Test with incorrect password
    response = await async_client.post(
        "/user-get",
        params={"username": user_data["username"]},
        auth=(user_data["username"], "wrong_password")
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED

    # Test with non-existent user
    response = await async_client.post(
        "/user-get",
        params={"username": "non_existent_user"},
        auth=("non_existent_user", "some_password")
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED

@pytest.mark.anyio
@pytest.mark.parametrize(
    "query_params, expected_status",
    [
        ({"id": 1, "username": "testuser"}, HTTPStatus.BAD_REQUEST),
        ({}, HTTPStatus.BAD_REQUEST),
        ({"id": 100500}, HTTPStatus.NOT_FOUND),
        ({"username": "nonexistent"}, HTTPStatus.NOT_FOUND),
    ],
)
async def test_get_user_edge_cases(async_client, query_params, expected_status, admin_credentials):
    """Test edge cases for getting user"""
    response = await async_client.post(
        "/user-get",
        params=query_params,
        auth=(admin_credentials["username"], admin_credentials["password"]),
    )
    assert response.status_code == expected_status
