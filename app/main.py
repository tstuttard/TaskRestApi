import os

from fastapi import FastAPI

from app.api.exception_handlers import task_already_exists_exception_handler
from app.api.main import api_router
from app.containers import Container
from app.domain.errors import TaskAlreadyExists

APP_DIR = os.path.dirname(os.path.abspath(__file__))


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(api_router)
    container = Container()
    container.config.from_dict(
        {
            "task_manager": {
                "sqlite": {},
                "in_memory": {},
            },
            # The amount slashes in the database url are important. For absolute paths, 4 slashes are needed.
            # APP_DIR has a leading /
            "db": {"url": f"sqlite:///{APP_DIR}/task.db"},
        }
    )

    container.config.task_manager.type.from_env(
        "TASK_MANAGER_TYPE", default="in_memory"
    )
    app.container = container
    app.add_exception_handler(TaskAlreadyExists, task_already_exists_exception_handler)
    return app


app = create_app()
