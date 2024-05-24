from typing import Any

from fastapi import APIRouter, status

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_task() -> Any:
    return {
        "data": {
            "id": "123",
            "name": "Dishes",
            "status": "pending",
            "due_date": None,
            "sub_tasks": [],
        }
    }


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
def get_task() -> Any:
    return {
        "data": {
            "id": "123",
            "name": "Dishes",
            "status": "pending",
            "due_date": None,
            "sub_tasks": [],
        }
    }
