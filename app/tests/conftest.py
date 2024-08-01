import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.database import get_db
from app.models import Base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine
)


@pytest_asyncio.fixture(scope="function")
async def session():

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with TestSessionLocal() as session:
        yield session
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(session: AsyncSession):
    async def override_get_db():
        try:
            yield session
        finally:
            await session.close()

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture(scope="function")
async def create_user_and_get_token(client: AsyncClient):      
    
    user_data = {
        "username": "testuser",
        "password": "testpassword"
    }
    
    response = await client.post("/register", json=user_data)
    assert response.status_code == 201
        
        
    response = await client.post("/token", data=user_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    return token

import pytest_asyncio
from httpx import AsyncClient

@pytest_asyncio.fixture(scope="function")
async def create_users_and_get_token(client: AsyncClient):
        
    for i in range(1, 3):  # Создаем двух пользователей
        user_data = {
            "username": f"testuser{i}",
            "password": f"testpassword{i}"
        }
        
        response = await client.post("/register", json=user_data)
        assert response.status_code == 201
        
        if i == 1:
            response = await client.post("/token", data=user_data)
            assert response.status_code == 200
            token = response.json()["access_token"]
    
    return token

