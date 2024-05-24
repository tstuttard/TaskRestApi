import uuid

import pytest

from app.domain.task_managers import CreateTask, InMemoryTaskManager, Task, TaskStatus


@pytest.fixture
def in_memory_task_manager() -> InMemoryTaskManager:
    return InMemoryTaskManager()


def test_create_task(in_memory_task_manager: InMemoryTaskManager) -> None:
    task_to_create_1 = CreateTask(name="Dishes", user_id=uuid.uuid4())
    task_to_create_2 = CreateTask(
        name="Wash Clothes", user_id=uuid.uuid4(), status=TaskStatus.DOING
    )
    created_task_1 = in_memory_task_manager.create_task(task_to_create_1)
    created_task_2 = in_memory_task_manager.create_task(task_to_create_2)

    expected_task_1 = Task(
        id=created_task_1.id,
        name=task_to_create_1.name,
        status=TaskStatus.PENDING,
        user_id=task_to_create_1.user_id,
    )
    expected_task_2 = Task(
        id=created_task_2.id,
        name=task_to_create_2.name,
        status=TaskStatus.DOING,
        user_id=task_to_create_2.user_id,
    )

    assert [created_task_1, created_task_2] == [
        expected_task_1,
        expected_task_2,
    ]

    expected_tasks = [
        in_memory_task_manager.get_task(created_task_1.id),
        in_memory_task_manager.get_task(created_task_2.id),
    ]

    assert [created_task_1, created_task_2] == expected_tasks
