from httpx import AsyncClient
import pytest


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    user_data = {"email": "newuser@example.com", "password": "newpassword123"}

    response = await client.post("/users/", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["is_active"] is True
    assert "id" in data


@pytest.mark.asyncio
async def test_create_user_duplicate_email(client: AsyncClient):
    user_data = {"email": "duplicate@example.com", "password": "password123"}

    # Create first user
    response = await client.post("/users/", json=user_data)
    assert response.status_code == 200

    # Try to create second user with same email
    response = await client.post("/users/", json=user_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_user(client: AsyncClient):
    # Create user first
    user_data = {"email": "getuser@example.com", "password": "password123"}

    create_response = await client.post("/users/", json=user_data)
    user_id = create_response.json()["id"]

    # Get user
    response = await client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "getuser@example.com"


@pytest.mark.asyncio
async def test_get_nonexistent_user(client: AsyncClient):
    response = await client.get("/users/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_user(client: AsyncClient):
    # Create user first
    user_data = {"email": "updateuser@example.com", "password": "password123"}

    create_response = await client.post("/users/", json=user_data)
    user_id = create_response.json()["id"]

    # Update user
    update_data = {"email": "updated@example.com", "is_active": False}

    response = await client.put(f"/users/{user_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "updated@example.com"
    assert data["is_active"] is False


@pytest.mark.asyncio
async def test_delete_user(client: AsyncClient):
    # Create user first
    user_data = {"email": "deleteuser@example.com", "password": "password123"}

    create_response = await client.post("/users/", json=user_data)
    user_id = create_response.json()["id"]

    # Delete user
    response = await client.delete(f"/users/{user_id}")
    assert response.status_code == 200

    # Verify user is deleted
    response = await client.get(f"/users/{user_id}")
    assert response.status_code == 404
