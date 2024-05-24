from dependency_injector import providers
from fastapi import FastAPI

from app.api.main import api_router
from app.containers import Container
from app.domain.task_managers import InMemoryTaskManager


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(api_router)
    container = Container()
    container.task_manager.override(providers.Singleton(InMemoryTaskManager))
    app.container = container
    return app


app = create_app()
