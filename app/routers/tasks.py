from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, schemas
from app.depenndencies import get_db, get_current_user
from app.models import User

router = APIRouter(tags=["Tasks"], prefix="/tasks")


@router.post("/", response_model=schemas.Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: schemas.TaskCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await crud.create_task(session=session, task=task, user_id=current_user.id)


@router.get("/", response_model=list[schemas.Task])
async def read_tasks(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await crud.get_tasks(session=session, user_id=current_user.id)


@router.get("/{task_id}", response_model=schemas.Task)
async def read_task(
    task_id: int,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    db_task = await crud.get_task(session=session, task_id=task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if db_task.owner_id != current_user.id:
        permission = await crud.get_user_task_permissions(
            session=session, task_id=task_id, user_id=current_user.id
        )
        if not permission or not permission.can_read:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    return db_task


@router.put("/{task_id}", response_model=schemas.Task)
async def update_task(
    task_id: int,
    task: schemas.TaskCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await crud.check_permissions_and_update_task(
        session=session,
        task_id=task_id,
        task_data=task,
        current_user=current_user,
        is_partial_update=False,
    )


@router.patch("/{task_id}", response_model=schemas.Task)
async def partial_update_task(
    task_id: int,
    task: schemas.TaskUpdate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await crud.check_permissions_and_update_task(
        session=session,
        task_id=task_id,
        task_data=task,
        current_user=current_user,
        is_partial_update=True,
    )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    db_task = await crud.get_task(session=session, task_id=task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if db_task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    await crud.delete_task(session=session, task_id=task_id)
    return None
