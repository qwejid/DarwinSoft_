import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_task_permissions(client: AsyncClient, create_users_and_get_token: str):
    token = create_users_and_get_token
        
    task_data = {
        "title": "Это тест",
        "description": "Тестовая задача",
    }
    response = await client.post(
        "/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    task_id = response.json()["id"]

    permission_data = {
        "user_id": 2, 
        "can_read": True,
        "can_update": True
    }
    response = await client.post(
        f"/tasks/{task_id}/permissions",
        json=permission_data,
        headers={"Authorization": f"Bearer {token}"})



    response = await client.get(
        f"/tasks/{task_id}/permissions",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    permissions = response.json()
    assert isinstance(permissions, list)

@pytest.mark.asyncio
async def test_create_task_permission(client: AsyncClient, create_users_and_get_token: str):
    token = create_users_and_get_token
        
    task_data = {
        "title": "Это тест",
        "description": "Тестовая задача",
    }
    response = await client.post(
        "/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    task_id = response.json()["id"]

    permission_data = {
        "user_id": 2, 
        "can_read": True,
        "can_update": True
    }
    response = await client.post(
        f"/tasks/{task_id}/permissions",
        json=permission_data,
        headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == permission_data["user_id"]
    assert data["can_read"] == permission_data["can_read"]
    assert data["can_update"] == permission_data["can_update"]

@pytest.mark.asyncio
async def test_update_task_permission(client: AsyncClient, create_users_and_get_token: str):
    token = create_users_and_get_token
        
    task_data = {
        "title": "Это тест",
        "description": "Тестовая задача",
    }
    response = await client.post(
        "/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    task_id = response.json()["id"]

    permission_data = {
        "user_id": 2, 
        "can_read": True,
        "can_update": True
    }
    response = await client.post(
        f"/tasks/{task_id}/permissions",
        json=permission_data,
        headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 201

    updated_permission_data = {
        "can_read": False,
        "can_update": True
    }

    response = await client.patch(
        f"/tasks/{task_id}/permissions/2",
        json=updated_permission_data,
        headers={"Authorization": f"Bearer {token}"}
    )
   

    assert response.status_code == 200
    data = response.json() 
    print(data)
    assert data["can_read"] == updated_permission_data["can_read"]
    assert data["can_update"] == updated_permission_data["can_update"]

@pytest.mark.asyncio
async def test_delete_task_permission(client: AsyncClient, create_users_and_get_token: str):
    token = create_users_and_get_token
        
    task_data = {
        "title": "Это тест",
        "description": "Тестовая задача",
    }
    response = await client.post(
        "/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    task_id = response.json()["id"]

    permission_data = {
        "user_id": 2, 
        "can_read": True,
        "can_update": True
    }
    response = await client.post(
        f"/tasks/{task_id}/permissions",
        json=permission_data,
        headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 201

    response = await client.delete(
        f"/tasks/{task_id}/permissions/2",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 204

    response = await client.get(
        f"/tasks/{task_id}/permissions",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
