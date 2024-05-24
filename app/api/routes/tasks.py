from uuid import UUID, uuid4
from typing import Any

from fastapi import APIRouter, status

from app.api.resources import StandardResponse, TaskResource, TaskStatus

router = APIRouter()


@router.post(
    "",
    response_model=StandardResponse[TaskResource],
    status_code=status.HTTP_201_CREATED,
)
def create_task() -> StandardResponse[TaskResource]:

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
