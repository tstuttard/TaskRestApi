from uuid import UUID, uuid4
from typing import Any

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, status

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
) -> StandardResponse[TaskResource]:
    created_task = task_manager.create_task(
        CreateTask(**create_task_request_body.model_dump(), user_id=uuid4())
    )
    response = StandardResponse[TaskResource](data=created_task.model_dump())
    return response


@router.get(
    "/{task_id}",
    response_model=StandardResponse[TaskResource],
    status_code=status.HTTP_200_OK,
)
@inject
def get_task(
    task_id: UUID, task_manager: TaskManager = Depends(Provide[Container.task_manager])
) -> Any:
    task = task_manager.get_task(task_id)
    return StandardResponse[TaskResource](data=task.model_dump())
