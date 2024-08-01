import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_task(client: AsyncClient, create_user_and_get_token: str):
    token = create_user_and_get_token

    task_data = {"title": "Тест", "description": "Тест."}

    response = await client.post(
        "/tasks/", json=task_data, headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == task_data["title"]
    assert data["description"] == task_data["description"]


@pytest.mark.asyncio
async def test_get_tasks(client: AsyncClient, create_user_and_get_token: str):

    token = create_user_and_get_token

    response = await client.get("/tasks/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    tasks = response.json()
    assert isinstance(tasks, list)


@pytest.mark.asyncio
async def test_get_task_by_id(client: AsyncClient, create_user_and_get_token: str):
    token = create_user_and_get_token

    task_data = {"title": "Это тест", "description": "Тестовая задача"}
    response = await client.post(
        "/tasks/", json=task_data, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    task_id = response.json()["id"]

    response = await client.get(
        f"/tasks/{task_id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == task_data["title"]
    assert data["description"] == task_data["description"]


@pytest.mark.asyncio
async def test_update_task(client: AsyncClient, create_user_and_get_token: str):
    token = create_user_and_get_token

    task_data = {"title": "Это тест", "description": "Тестовая задача"}
    response = await client.post(
        "/tasks/", json=task_data, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    task_id = response.json()["id"]

    updated_task_data = {
        "title": "Обновили заголовок",
        "description": "Обновили описание.",
    }
    response = await client.put(
        f"/tasks/{task_id}",
        json=updated_task_data,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == updated_task_data["title"]
    assert data["description"] == updated_task_data["description"]


@pytest.mark.asyncio
async def test_delete_task(client: AsyncClient, create_user_and_get_token: str):
    token = create_user_and_get_token

    task_data = {"title": "Это тест", "description": "Тестовая задача"}
    response = await client.post(
        "/tasks/", json=task_data, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    task_id = response.json()["id"]

    response = await client.delete(
        f"/tasks/{task_id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 204

    response = await client.get(
        f"/tasks/{task_id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404
