from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, schemas
from app.depenndencies import get_db, get_current_user
from typing import Annotated
from app.models import User

router = APIRouter(tags=["Permissions"], prefix="/tasks/{task_id}")


@router.get("/permissions", response_model=list[schemas.TaskPermission])
async def get_task_permissions(
    task_id: int, session: Annotated[AsyncSession, Depends(get_db)]
):
    permissions = await crud.get_task_permissions(session=session, task_id=task_id)
    return permissions


@router.post(
    "/permissions",
    response_model=schemas.TaskPermission,
    status_code=status.HTTP_201_CREATED,
)
async def create_task_permission(
    task_id: int,
    permission: schemas.TaskPermissionCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    db_task = await crud.get_task(session=session, task_id=task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if db_task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await crud.create_task_permission(
        session=session, permission=permission, task_id=task_id
    )


@router.patch("/permissions/{user_id}", response_model=schemas.TaskPermission)
async def update_task_permission(
    task_id: int,
    user_id: int,
    permission_update: schemas.TaskPermissionUpdate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    db_task = await crud.get_task(session=session, task_id=task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if db_task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    updated_permission = await crud.update_task_permission(
        session=session,
        task_id=task_id,
        user_id=user_id,
        permission_update=permission_update,
    )
    return updated_permission


@router.delete("/permissions/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_permission(
    task_id: int,
    user_id: int,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    db_task = await crud.get_task(session=session, task_id=task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if db_task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    await crud.delete_task_permission(session=session, task_id=task_id, user_id=user_id)
    return None
