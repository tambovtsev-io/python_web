import pytest
from http import HTTPStatus
from demo_service.api.contracts import UserResponse
from demo_service.core.users import UserRole


@pytest.mark.anyio
async def test_register_user(async_client, user_data, admin_credentials):
    """Test user registration"""
    # Register user
    response = await async_client.post("/user-register", json=user_data)
    assert response.status_code == HTTPStatus.OK
    user = UserResponse(**response.json())
    assert user.username == user_data["username"]
    assert user.name == user_data["name"]
    assert user.role == UserRole.USER

    # Verify user creation by retrieving the user
    get_user_response = await async_client.post(
        "/user-get",
        params={"username": user_data["username"]},
        auth=(admin_credentials["username"], admin_credentials["password"]),
    )
    assert get_user_response.status_code == HTTPStatus.OK
    retrieved_user = UserResponse(**get_user_response.json())

    # Compare retrieved user with registered user
    assert retrieved_user.uid == user.uid
    assert retrieved_user.username == user.username
    assert retrieved_user.name == user.name
    assert retrieved_user.role == user.role
    assert retrieved_user.birthdate == user.birthdate


@pytest.mark.anyio
@pytest.mark.parametrize(
    "invalid_password",
    [
        "short",  # Short password
        "longenoughbutnodigits",  # Password without digits
    ]
)
async def test_register_user_invalid_password(async_client, invalid_password):
    """Test user registration with invalid passwords"""
    user_data = {
        "username": "testuser",
        "name": "Test User",
        "birthdate": "2000-01-01",
        "password": invalid_password,
    }

    response = await async_client.post("/user-register", json=user_data)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "invalid password" in response.text

    # Verify that the user was not created
    get_user_response = await async_client.post(
        "/user-get",
        params={"username": user_data["username"]},
        auth=("admin", "superSecretAdminPassword123"),
    )
    assert get_user_response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.anyio
@pytest.mark.parametrize(
    "invalid_data, expected_error",
    [
        (
            {
                "username": "existing_user",
                "name": "Existing User",
                "birthdate": "2000-01-01",
                "password": "newvalidpassword123"
            },
            "username is already taken"
        ),
        (
            {
                "username": "short_password_user",
                "name": "Short Password User",
                "birthdate": "2000-01-01",
                "password": "short"
            },
            "invalid password"
        ),
    ]
)
async def test_register_user_bad_request(async_client, invalid_data, expected_error):
    """Test user registration with invalid data that should result in BAD_REQUEST"""
    response = await async_client.post("/user-register", json=invalid_data)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert expected_error in response.text


@pytest.mark.anyio
@pytest.mark.parametrize(
    "invalid_data, expected_error_msg",
    [
        (
            {
                "username": "no_password_user",
                "name": "No Password User",
                "birthdate": "2000-01-01"
            },
            "Field required"
        ),
        (
            {
                "username": "invalid_date_user",
                "name": "Invalid Date User",
                "birthdate": "invalid-date",
                "password": "validpassword123"
            },
            "invalid date format"
        ),
    ]
)
async def test_register_user_unprocessable_entity(async_client, invalid_data, expected_error_msg):
    """Test user registration with invalid data that should result in UNPROCESSABLE_ENTITY"""
    response = await async_client.post("/user-register", json=invalid_data)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert "msg" in response.text
