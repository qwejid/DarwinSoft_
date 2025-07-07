from sqlalchemy import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import User, Task, TaskPermission
from .schemas import (
    TaskPermissionUpdate,
    TaskUpdate,
    UserCreate,
    TaskCreate,
    TaskPermissionCreate,
)
from app.utils.security import get_password_hash
from fastapi import HTTPException


async def get_user_by_username(session: AsyncSession, username: str):
    result = await session.execute(select(User).filter(User.username == username))
    return result.scalars().first()

async def get_users(session: AsyncSession):
    result = await session.execute(select(User))
    return result.scalars().all()

async def create_user(session: AsyncSession, user_data: UserCreate):
    hashed_password = get_password_hash(user_data.password)
    new_user = User(username=user_data.username, hashed_password=hashed_password)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


async def create_task(session: AsyncSession, task: TaskCreate, user_id: int):
    new_task = Task(**task.model_dump(), owner_id=user_id)
    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)
    return new_task


async def get_tasks(session: AsyncSession, user_id: int):
    stmt = (
        select(Task)
        .filter(
            or_(
                Task.owner_id == user_id,
                Task.id.in_(
                    select(TaskPermission.task_id)
                    .filter(
                        TaskPermission.user_id == user_id,
                        TaskPermission.can_read == True
                    )
                )
            )
        )
        .order_by(Task.id)
    )
    result: Result = await session.execute(stmt)
    return result.scalars().all()


async def get_task(session: AsyncSession, task_id: int):
    result = await session.execute(select(Task).filter(Task.id == task_id))
    return result.scalars().first()


async def check_permissions_and_update_task(
    session: AsyncSession,
    task_id: int,
    task_data: TaskCreate | TaskUpdate,
    current_user: User,
    is_partial_update: bool = False,
):
    db_task = await session.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    if db_task.owner_id != current_user.id:
        permission = await get_user_task_permissions(
            session=session, task_id=task_id, user_id=current_user.id
        )
        if not permission or not permission.can_update:
            raise HTTPException(status_code=403, detail="Not enough permissions")

    return await update_task(
        session=session, task_id=task_id, task=task_data, partial=is_partial_update
    )


async def update_task(
    session: AsyncSession,
    task_id: int,
    task: TaskCreate | TaskUpdate,
    partial: bool = False,
):
    task_db = await session.get(Task, task_id)
    if not task_db:
        raise HTTPException(status_code=404, detail="Task not found")
    if not partial:
        task_db.title = task.title
        task_db.description = task.description
    else:
        if task.title is not None:
            task_db.title = task.title
        if task.description is not None:
            task_db.description = task.description
    await session.commit()
    await session.refresh(task_db)
    return task_db


async def delete_task(
    session: AsyncSession,
    task_id: int,
):
    db_task = await session.get(Task, task_id)
    if db_task:
        await session.delete(db_task)
        await session.commit()
    return None


async def create_task_permission(
    session: AsyncSession,
    permission: TaskPermissionCreate,
    task_id: int,
):
    existing_permission = await session.execute(
        select(TaskPermission)
        .where(TaskPermission.task_id == task_id)
        .where(TaskPermission.user_id == permission.user_id)
    )
    existing_permission = existing_permission.scalars().first()
    if existing_permission:
        raise HTTPException(
            status_code=400, detail="Permission already exists for this user and task."
        )
    db_permission = TaskPermission(**permission.model_dump(), task_id=task_id)
    session.add(db_permission)
    await session.commit()
    await session.refresh(db_permission)
    return db_permission


async def get_task_permissions(
    session: AsyncSession,
    task_id: int,
) -> list[TaskPermission]:
    result = await session.execute(
        select(TaskPermission).filter(TaskPermission.task_id == task_id)
    )
    permissions = result.scalars().all()
    
    if not permissions:
        raise HTTPException(status_code=404, detail="No permissions found for this task.")
    
    return permissions


async def get_user_task_permissions(
    session: AsyncSession,
    task_id: int,
    user_id: int,
) -> TaskPermission:
    result = await session.execute(
        select(TaskPermission).filter(
            TaskPermission.task_id == task_id, TaskPermission.user_id == user_id
        )
    )
    return result.scalars().first()


async def update_task_permission(
    session: AsyncSession,
    task_id: int,
    user_id: int,
    permission_update: TaskPermissionUpdate,
):
    db_permission = await get_user_task_permissions(session, task_id, user_id)
    if not db_permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    if permission_update.can_read is not None:
        db_permission.can_read = permission_update.can_read
    if permission_update.can_update is not None:
        db_permission.can_update = permission_update.can_update
    session.add(db_permission)
    await session.commit()
    await session.refresh(db_permission)
    return db_permission


async def delete_task_permission(
    session: AsyncSession,
    task_id: int,
    user_id: int,
):
    result = await session.execute(
        select(TaskPermission).filter(
            TaskPermission.task_id == task_id, TaskPermission.user_id == user_id
        )
    )
    db_permission = result.scalars().first()
    if db_permission:
        await session.delete(db_permission)
        await session.commit()
    return None
