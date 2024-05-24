from uuid import UUID

import pytest
from httpx import QueryParams
from starlette.testclient import TestClient
from fastapi import status
from app.main import app
from tests.conftest import user_id_1


@pytest.fixture
def client():
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
