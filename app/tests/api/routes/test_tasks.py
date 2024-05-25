from uuid import UUID, uuid4

import pytest
from httpx import QueryParams
from starlette.testclient import TestClient
from fastapi import status, FastAPI
from app.main import create_app
from app.domain.task_managers import CreateTask, TaskManager
from tests.conftest import user_id_1


@pytest.fixture
def app() -> FastAPI:
    app = create_app()
    yield app
    # TODO figure out how to type hint container
    app.container.unwire()


@pytest.fixture
def task_manager(app: FastAPI) -> TaskManager:
    return app.container.task_manager()


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    yield TestClient(app)


def test_create_task(client: TestClient, user_id_1: UUID) -> None:
    create_task_request_body = {
        "name": "Dishes",
    }
    create_task_response = client.post(
        f"/tasks", params=QueryParams(user_id=user_id_1), json=create_task_request_body
    )

    create_task_payload = create_task_response.json()
    expected_task_payload = {
        "data": {
            "id": create_task_payload["data"]["id"],  # id is generated from server
            "name": create_task_request_body["name"],
            "status": "Pending",
            "due_date": None,
            "labels": [],
            "sub_tasks": [],
        }
    }
    assert create_task_payload == expected_task_payload
    assert create_task_response.status_code == status.HTTP_201_CREATED

    get_task_response = client.get(
        f"/tasks/{create_task_payload['data']['id']}",
        params=QueryParams(user_id=user_id_1),
    )

    get_task_response_json = get_task_response.json()
    assert get_task_response_json == expected_task_payload
    assert get_task_response.status_code == status.HTTP_200_OK


def test_task_not_found(client: TestClient, user_id_1: UUID, user_id_2: UUID) -> None:
    create_task_request_body = {
        "name": "Dishes",
    }
    create_task_response = client.post(
        f"/tasks", params=QueryParams(user_id=user_id_1), json=create_task_request_body
    )

    create_task_payload = create_task_response.json()
    expected_task_payload = {
        "data": {
            "id": create_task_payload["data"]["id"],  # id is generated from server
            "name": create_task_request_body["name"],
            "status": "Pending",
            "due_date": None,
            "labels": [],
            "sub_tasks": [],
        }
    }

    assert create_task_payload == expected_task_payload
    assert create_task_response.status_code == status.HTTP_201_CREATED

    get_task_response = client.get(
        f"/tasks/{create_task_payload['data']['id']}",
        params=QueryParams(user_id=user_id_2),
    )

    get_task_response_json = get_task_response.json()
    assert get_task_response_json == {
        "detail": {"key": "task_not_found", "message": "task not found"}
    }
    assert get_task_response.status_code == status.HTTP_404_NOT_FOUND


def test_get_tasks(client: TestClient, task_manager: TaskManager, user_id_1: UUID):
    task1 = task_manager.create_task(CreateTask(name="Dishes", user_id=user_id_1))
    task2 = task_manager.create_task(CreateTask(name="Dishes", user_id=user_id_1))
    task3 = task_manager.create_task(CreateTask(name="Dishes", user_id=user_id_1))

    get_tasks_response = client.get(f"/tasks", params=QueryParams(user_id=user_id_1))
    get_tasks_payload = get_tasks_response.json()
    assert get_tasks_payload == {
        "data": [
            task1.model_dump(mode="json", exclude={"user_id"}),
            task2.model_dump(mode="json", exclude={"user_id"}),
            task3.model_dump(mode="json", exclude={"user_id"}),
        ]
    }

    assert get_tasks_response.status_code == status.HTTP_200_OK


def test_update_task(client: TestClient, task_manager: TaskManager, user_id_1: UUID):
    task = task_manager.create_task(CreateTask(name="Dishes", user_id=user_id_1))

    update_task_request_body = {
        "id": str(task.id),
        "name": "Wash & Dry Dishes",
        "status": "Done",
        "due_date": None,
        "labels": [],
        "sub_tasks": [],
    }
    update_tasks_response = client.put(
        f"/tasks/{task.id}",
        params=QueryParams(user_id=user_id_1),
        json=update_task_request_body,
    )
    update_task_payload = update_tasks_response.json()
    assert update_task_payload == {
        "data": {
            # Since a PUT endpoint is essentially replacing the resource, we can assume that
            # the response should match the request since a task has no dynamic properties
            **update_task_request_body
        }
    }

    assert update_tasks_response.status_code == status.HTTP_200_OK


def test_update_task_with_no_task_id(
    client: TestClient, task_manager: TaskManager, user_id_1: UUID
):
    task = task_manager.create_task(CreateTask(name="Dishes", user_id=user_id_1))

    update_task_request_body = {
        "name": "Wash & Dry Dishes",
        "status": "Done",
        "due_date": None,
        "labels": [],
        "sub_tasks": [],
    }
    update_tasks_response = client.put(
        f"/tasks/{task.id}",
        params=QueryParams(user_id=user_id_1),
        json=update_task_request_body,
    )
    update_task_payload = update_tasks_response.json()
    assert update_task_payload == {
        "data": {"id": str(task.id), **update_task_request_body}
    }

    assert update_tasks_response.status_code == status.HTTP_200_OK


def test_update_task_id_mismatch(
    client: TestClient, task_manager: TaskManager, user_id_1: UUID
) -> None:
    task = task_manager.create_task(CreateTask(name="Dishes", user_id=user_id_1))

    update_task_request_body = {
        "id": str(uuid4()),
        "name": "Wash & Dry Dishes",
        "status": "Done",
        "due_date": None,
        "labels": [],
        "sub_tasks": [],
    }
    update_tasks_response = client.put(
        f"/tasks/{task.id}",
        params=QueryParams(user_id=user_id_1),
        json=update_task_request_body,
    )
    update_task_payload = update_tasks_response.json()
    assert update_task_payload == {
        "detail": {
            "key": "task_id_mismatch",
            "message": "task is in request body does not match task id in URI",
        }
    }
    assert update_tasks_response.status_code == status.HTTP_400_BAD_REQUEST


def test_update_task_not_found(
    client: TestClient, task_manager: TaskManager, user_id_1: UUID, user_id_2
) -> None:
    task = task_manager.create_task(CreateTask(name="Dishes", user_id=user_id_1))

    update_task_request_body = {
        "id": str(task.id),
        "name": "Wash & Dry Dishes",
        "status": "Done",
        "due_date": None,
        "labels": [],
        "sub_tasks": [],
    }
    update_tasks_response = client.put(
        f"/tasks/{task.id}",
        params=QueryParams(user_id=user_id_2),
        json=update_task_request_body,
    )
    update_task_payload = update_tasks_response.json()
    assert update_task_payload == {
        "detail": {"key": "task_not_found", "message": "task not found"}
    }
    assert update_tasks_response.status_code == status.HTTP_404_NOT_FOUND
