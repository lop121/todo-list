from typing import List

import httpx
import uuid
from fastapi import APIRouter, Depends, HTTPException
from . import schemas, security

router = APIRouter(prefix="/tasks", tags=["Tasks"])

AUTH_SERVICE_URL = "http://auth_service:8000"

tasks_db = []


@router.post("/new_task", response_model=schemas.Task)
async def create_task(
        task_data: schemas.TaskCreate,
        token_payload: security.TokenData = Depends(security.get_current_user)
):
    author_id = uuid.UUID(token_payload.sub)

    new_task = schemas.TaskInDB(
        **task_data.model_dump(),
        author_id=author_id
    )

    tasks_db.append(new_task)

    print(f"Новая задача создана: {new_task.title}, Автор ID: {new_task.author_id}")

    return new_task


@router.get("/me", response_model=List[schemas.TaskWithAuthorUsername])
async def get_my_tasks(current_author_id: uuid.UUID = Depends(security.get_current_author_id)):
    my_tasks = [task for task in tasks_db if task.author_id == current_author_id]

    if not my_tasks:
        return []

    author_username = "Неизвестный пользователь"
    try:
        async with httpx.AsyncClient() as client:
            print(current_author_id)
            response = await client.get(f"{AUTH_SERVICE_URL}/auth/users/{current_author_id}")

            response.raise_for_status()

            user_data = response.json()
            author_username = user_data.get("username", "Неизвестный пользователь")

    except httpx.HTTPStatusError as e:
        print(f"Ошибка при запросе к Auth Service: статус {e.response.status_code}")
    except httpx.RequestError as e:
        print(f"Не удалось подключиться к Auth Service: {e}")

    enriched_tasks = []
    for task in my_tasks:
        enriched_task = schemas.TaskWithAuthorUsername(
            **task.model_dump(),
            author_username=author_username
        )
        enriched_tasks.append(enriched_task)

    return enriched_tasks


@router.delete("/{user_task_id}")
async def delete_task(
        user_task_id: uuid.UUID,
        token_payload: security.TokenData = Depends(security.get_current_author_id)
):
    task_to_delete = None
    delete_index = -1

    for i, task in enumerate(tasks_db):
        if task.id == user_task_id and task.author_id == token_payload:
            task_to_delete = task
            delete_index = i
            break

    if delete_index != -1:
        tasks_db.pop(delete_index)
        return {'status': 'Задача успешно удалена!', 'task': task_to_delete}
    else:
        raise HTTPException(status_code=404, detail="Задача не найдена или у вас нет прав на её удаление")


@router.patch("/{task_id}", response_model=schemas.Task)
async def edit_task(
        task_id: uuid.UUID,
        task_update_data: schemas.TaskUpdate,
        token_payload: security.TokenData = Depends(security.get_current_author_id)
):
    task_to_edit = None
    task_index = -1

    for i, task in enumerate(tasks_db):
        if task.id == task_id and task.author_id == token_payload:
            task_to_edit = task
            task_index = i
            break

    if task_to_edit is None:
        raise HTTPException(
            status_code=404,
            detail="Задача не найдена или у вас нет прав на её редактирование"
        )

    update_data = task_update_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(task_to_edit, key, value)

    tasks_db[task_index] = task_to_edit

    return task_to_edit
