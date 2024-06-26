import datetime
from uuid import UUID, uuid4

import pytest
from httpx import QueryParams
from starlette.testclient import TestClient
from fastapi import status, FastAPI
from app.domain.task_managers import TaskManager
from app.domain.models import CreateTask, TaskStatus


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    yield TestClient(app)


def test_create_task(client: TestClient, user_id_1: UUID) -> None:
    today = datetime.date.today().strftime("%Y-%m-%d")
    create_task_request_body = {
        "name": "Dishes",
        "due_date": today,
        "labels": ["kitchen", "daily"],
    }
    create_task_response = client.post(
        "/tasks", params=QueryParams(user_id=user_id_1), json=create_task_request_body
    )

    create_task_payload = create_task_response.json()
    task_id = create_task_payload["data"]["id"]
    expected_task_payload = {
        "data": {
            "id": task_id,
            "name": create_task_request_body["name"],
            "status": "Pending",
            "due_date": today,
            "labels": {"kitchen", "daily"},
            "sub_tasks": [],
        }
    }
    assert_task_payload_match(create_task_payload, expected_task_payload)
    assert create_task_response.status_code == status.HTTP_201_CREATED

    assert_task_exists(client, task_id, user_id_1, expected_task_payload)


def test_task_not_found(client: TestClient, user_id_1: UUID, user_id_2: UUID) -> None:
    create_task_request_body = {
        "name": "Dishes",
    }
    create_task_response = client.post(
        "/tasks", params=QueryParams(user_id=user_id_1), json=create_task_request_body
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

    get_tasks_response = client.get("/tasks", params=QueryParams(user_id=user_id_1))
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


def test_delete_task(
    client: TestClient, task_manager: TaskManager, user_id_1: UUID
) -> None:
    task = task_manager.create_task(CreateTask(name="Dishes", user_id=user_id_1))

    delete_tasks_response = client.delete(
        f"/tasks/{task.id}",
        params=QueryParams(user_id=user_id_1),
    )

    assert delete_tasks_response.status_code == status.HTTP_204_NO_CONTENT
    assert delete_tasks_response.content == b""


def test_delete_task_not_found(
    client: TestClient, task_manager: TaskManager, user_id_1: UUID, user_id_2
) -> None:
    task = task_manager.create_task(CreateTask(name="Dishes", user_id=user_id_1))

    delete_task_response = client.delete(
        f"/tasks/{task.id}",
        params=QueryParams(user_id=user_id_2),
    )
    delete_task_payload = delete_task_response.json()
    assert delete_task_payload == {
        "detail": {"key": "task_not_found", "message": "task not found"}
    }
    assert delete_task_response.status_code == status.HTTP_404_NOT_FOUND


def test_restore_task(
    client: TestClient, task_manager: TaskManager, user_id_1: UUID
) -> None:
    task = task_manager.create_task(
        CreateTask(name="Dishes", user_id=user_id_1, status=TaskStatus.DONE)
    )
    task_manager.delete_task(task.id, user_id_1)

    restore_task_response = client.post(
        f"/tasks/{task.id}/restore", params=QueryParams(user_id=user_id_1)
    )

    restore_task_payload = restore_task_response.json()

    expected_task_payload = {
        "data": {
            "id": str(task.id),  # id is generated from server
            "name": task.name,
            "status": "Done",
            "due_date": None,
            "labels": set(),
            "sub_tasks": [],
        }
    }
    assert_task_payload_match(restore_task_payload, expected_task_payload)

    assert_task_exists(client, task.id, user_id_1, expected_task_payload)


def test_restore_task_that_already_exists(
    client: TestClient, task_manager: TaskManager, user_id_1: UUID
) -> None:
    task = task_manager.create_task(
        CreateTask(name="Dishes", user_id=user_id_1, status=TaskStatus.DONE)
    )
    task_manager.delete_task(task.id, user_id_1)
    task_manager.restore_task(task.id, user_id_1)

    restore_task_response = client.post(
        f"/tasks/{task.id}/restore", params=QueryParams(user_id=user_id_1)
    )

    restore_task_payload = restore_task_response.json()

    assert restore_task_payload == {
        "detail": {"key": "task_already_exists", "message": "task already exists"}
    }
    assert restore_task_response.status_code == status.HTTP_400_BAD_REQUEST


def assert_task_exists(
    client: TestClient,
    task_id: UUID,
    user_id_1: UUID,
    expected_task_payload: dict,
):
    get_task_response = client.get(
        f"/tasks/{task_id}",
        params=QueryParams(user_id=user_id_1),
    )
    get_task_response_json = get_task_response.json()

    assert_task_payload_match(get_task_response_json, expected_task_payload)
    assert get_task_response.status_code == status.HTTP_200_OK


def assert_task_payload_match(actual_task_payload: dict, expected_task_payload: dict):
    assert {
        "data": {
            **expected_task_payload["data"],
            "labels": set(actual_task_payload["data"]["labels"]),
        },
    } == expected_task_payload
