from uuid import uuid4

import pytest
from fastapi import FastAPI

from app.domain.task_managers import TaskManager
from app.main import create_app


@pytest.fixture
def user_id_1():
    return uuid4()


@pytest.fixture
def user_id_2():
    return uuid4()


@pytest.fixture
def app() -> FastAPI:
    app = create_app()
    yield app
    # TODO figure out how to type hint container
    app.container.unwire()


@pytest.fixture
def task_manager(app: FastAPI) -> TaskManager:
    return app.container.task_manager()
