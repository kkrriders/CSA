"""
Tests for authentication endpoints and security.
"""
import pytest
from fastapi import status


@pytest.mark.asyncio
@pytest.mark.integration
async def test_register_user(async_client):
    """Test user registration."""
    response = await async_client.post(
        "/api/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepassword123",
            "full_name": "New User"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "password" not in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
@pytest.mark.integration
async def test_register_duplicate_user(async_client, test_user):
    """Test registration with duplicate username."""
    response = await async_client.post(
        "/api/auth/register",
        json={
            "username": test_user["username"],
            "email": "different@example.com",
            "password": "password123",
            "full_name": "Duplicate User"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
@pytest.mark.integration
async def test_login_success(async_client, test_user):
    """Test successful login."""
    response = await async_client.post(
        "/api/auth/login",
        data={
            "username": test_user["username"],
            "password": "testpassword123"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_login_wrong_password(async_client, test_user):
    """Test login with wrong password."""
    response = await async_client.post(
        "/api/auth/login",
        data={
            "username": test_user["username"],
            "password": "wrongpassword"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_current_user(async_client, test_user, auth_headers):
    """Test getting current user info."""
    response = await async_client.get(
        "/api/auth/me",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_current_user_unauthorized(async_client):
    """Test getting current user without auth."""
    response = await async_client.get("/api/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
