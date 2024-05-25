from uuid import UUID, uuid4
from typing import List

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, status, HTTPException

from app.api.resources import CreateTaskRequestBody, StandardResponse, TaskResource
from app.containers import Container
from app.domain.task_managers import CreateTask, TaskManager

router = APIRouter()


@router.post(
    "",
    response_model=StandardResponse[TaskResource],
    status_code=status.HTTP_201_CREATED,
)
@inject
def create_task(
    create_task_request_body: CreateTaskRequestBody,
    task_manager: TaskManager = Depends(Provide[Container.task_manager]),
    user_id: UUID = uuid4(),
) -> StandardResponse[TaskResource]:
    created_task = task_manager.create_task(
        CreateTask(**create_task_request_body.model_dump(), user_id=user_id)
    )
    response = StandardResponse[TaskResource](data=created_task.model_dump())
    return response


@router.get(
    "",
    response_model=StandardResponse[List[TaskResource]],
    status_code=status.HTTP_200_OK,
)
@inject
def get_tasks(
    user_id: UUID,
    task_manager: TaskManager = Depends(Provide[Container.task_manager]),
) -> StandardResponse[List[TaskResource]]:
    tasks = task_manager.get_tasks(user_id)
    return StandardResponse[List[TaskResource]](
        data=[TaskResource(**task.model_dump()) for task in tasks]
    )


@router.get(
    "/{task_id}",
    response_model=StandardResponse[TaskResource],
    status_code=status.HTTP_200_OK,
)
@inject
def get_task(
    task_id: UUID,
    user_id: UUID,
    task_manager: TaskManager = Depends(Provide[Container.task_manager]),
) -> StandardResponse[TaskResource]:
    task = task_manager.get_task(task_id, user_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"key": "task_not_found", "message": "task not found"},
        )
    return StandardResponse[TaskResource](data=task.model_dump())
