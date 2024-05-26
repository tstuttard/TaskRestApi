import os

from fastapi import FastAPI

from app.api.main import api_router
from app.containers import Container


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
            # TODO Fix unable to open database connection error, and remove hardcoded path
            #      This won't work if there are files in different directory structures accessing the database
            "db": {"url": f"sqlite:///../../task.db"},
        }
    )

    container.config.task_manager.type.from_env(
        "TASK_MANAGER_TYPE", default="in_memory"
    )
    app.container = container
    return app


app = create_app()
