from httpx import AsyncClient
import pytest


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    # First create a user
    user_data = {"email": "test@example.com", "password": "testpassword123"}

    # Create user
    response = await client.post("/users/", json=user_data)
    assert response.status_code == 200

    # Login
    login_data = {"email": "test@example.com", "password": "testpassword123"}

    response = await client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    login_data = {"email": "nonexistent@example.com", "password": "wrongpassword"}

    response = await client.post("/auth/login", json=login_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient):
    # Create and login user
    user_data = {"email": "test2@example.com", "password": "testpassword123"}

    # Create user
    response = await client.post("/users/", json=user_data)
    assert response.status_code == 200

    # Login
    login_response = await client.post("/auth/login", json=user_data)
    token = login_response.json()["access_token"]

    # Get current user info
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test2@example.com"
