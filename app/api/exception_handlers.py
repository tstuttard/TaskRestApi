from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.domain.errors import TaskAlreadyExists


def task_already_exists_exception_handler(
    request: Request, exc: TaskAlreadyExists
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": {"key": "task_already_exists", "message": "task already exists"}
        },
    )
