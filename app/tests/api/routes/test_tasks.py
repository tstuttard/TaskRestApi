import pytest
from starlette.testclient import TestClient
from fastapi import status
from main import app


@pytest.fixture
def client():
    yield TestClient(app)


def test_create_task(client: TestClient) -> None:
    _id = 123
    create_task_request_body = {
        "name": "Dishes",
    }
    create_task_response = client.post(f"/tasks", json=create_task_request_body)

    create_task_payload = create_task_response.json()
    expected_task_payload = {
        "data": {
            "id": create_task_payload["data"]["id"],  # id is generated from server
            "name": create_task_request_body["name"],
            "status": "pending",
            "due_date": None,
            "sub_tasks": [],
        }
    }
    assert create_task_payload == expected_task_payload
    assert create_task_response.status_code == status.HTTP_201_CREATED

    get_task_response = client.get(f"/tasks/{create_task_payload['data']['id']}")

    get_task_response_json = get_task_response.json()
    assert get_task_response_json == expected_task_payload
    assert get_task_response.status_code == status.HTTP_200_OK
