from uuid import UUID, uuid4
from typing import Any

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, status

from app.api.resources import StandardResponse, TaskResource, TaskStatus
from app.containers import Container
from domain.task_managers import TaskManager

router = APIRouter()


@router.post(
    "",
    response_model=StandardResponse[TaskResource],
    status_code=status.HTTP_201_CREATED,
)
@inject
def create_task(
    task_manager: TaskManager = Depends(Provide[Container.task_manager]),
) -> StandardResponse[TaskResource]:
    task_manager.create_task({})
    return StandardResponse[TaskResource](
        data={
            "id": uuid4(),
            "name": "Dishes",
            "status": TaskStatus.PENDING,
            "labels": [],
            "due_date": None,
            "sub_tasks": [],
        }
    )


@router.get(
    "/{task_id}",
    response_model=StandardResponse[TaskResource],
    status_code=status.HTTP_200_OK,
)
def get_task(task_id: UUID) -> Any:
    return StandardResponse[TaskResource](
        data={
            "id": task_id,
            "name": "Dishes",
            "status": TaskStatus.PENDING,
            "labels": [],
            "due_date": None,
            "sub_tasks": [],
        }
    )
