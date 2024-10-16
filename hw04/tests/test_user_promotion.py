import pytest
from http import HTTPStatus
from demo_service.api.contracts import UserResponse
from demo_service.core.users import UserRole


@pytest.mark.anyio
async def test_promote_user(async_client, user_data, admin_credentials):
    """Test promoting a user to admin"""
    # Register a user first
    register_response = await async_client.post("/user-register", json=user_data)
    user_id = register_response.json()["uid"]

    # Promote user to admin
    response = await async_client.post(
        "/user-promote",
        params={"id": user_id},
        auth=(admin_credentials["username"], admin_credentials["password"]),
    )
    assert response.status_code == HTTPStatus.OK

    # Verify user role
    get_user_response = await async_client.post(
        "/user-get",
        params={"id": user_id},
        auth=(admin_credentials["username"], admin_credentials["password"]),
    )
    promoted_user = UserResponse(**get_user_response.json())
    assert promoted_user.role == UserRole.ADMIN


@pytest.mark.anyio
async def test_promote_user_unauthorized(async_client, user_data):
    """Test promoting a user without admin credentials"""
    # Register a user first
    register_response = await async_client.post("/user-register", json=user_data)
    user_id = register_response.json()["uid"]

    # Attempt to promote user without admin credentials
    response = await async_client.post(
        "/user-promote",
        params={"id": user_id},
        auth=(user_data["username"], user_data["password"]),
    )
    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.anyio
async def test_promote_nonexistent_user(async_client, admin_credentials):
    """Test promoting a non-existent user"""
    response = await async_client.post(
        "/user-promote",
        params={"id": 9999},
        auth=(admin_credentials["username"], admin_credentials["password"]),
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "user not found" in response.text
