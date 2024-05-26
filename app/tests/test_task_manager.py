import json
from uuid import UUID, uuid4
import pytest

from app.domain.task_managers import (
    HistoryEntry,
    HistoryEntryType,
    HistoryEntryVersion,
    TaskManager,
)
from app.domain.models import CreateTask, Task, UpdateTask, TaskStatus


def test_create_task(task_manager: TaskManager, user_id_1: UUID) -> None:
    task_to_create_1 = CreateTask(name="Dishes", user_id=user_id_1)
    task_to_create_2 = CreateTask(
        name="Wash Clothes", user_id=user_id_1, status=TaskStatus.DOING
    )
    created_task_1 = task_manager.create_task(task_to_create_1)
    created_task_2 = task_manager.create_task(task_to_create_2)

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
        task_manager.get_task(created_task_1.id, user_id_1),
        task_manager.get_task(created_task_2.id, user_id_1),
    ]

    assert [created_task_1, created_task_2] == expected_tasks


def test_get_tasks(task_manager: TaskManager, user_id_1: UUID, user_id_2: UUID) -> None:

    created_task_1 = task_manager.create_task(
        CreateTask(name="Dishes", user_id=user_id_1)
    )
    created_task_2 = task_manager.create_task(
        CreateTask(name="Wash Clothes", user_id=user_id_1, status=TaskStatus.DOING)
    )
    created_task_3 = task_manager.create_task(
        CreateTask(name="Wash Clothes", user_id=user_id_2, status=TaskStatus.DONE)
    )

    tasks = task_manager.get_tasks(user_id_1)

    assert tasks == [created_task_1, created_task_2]


def test_get_task_returns_none(
    task_manager: TaskManager, user_id_1: UUID, user_id_2: UUID
) -> None:
    user_id_3 = uuid4()

    created_task_1 = task_manager.create_task(
        CreateTask(name="Dishes", user_id=user_id_1)
    )
    created_task_2 = task_manager.create_task(
        CreateTask(name="Wash Clothes", user_id=user_id_2, status=TaskStatus.DOING)
    )

    assert task_manager.get_task(task_id=created_task_1.id, user_id=user_id_3) is None
    assert task_manager.get_task(task_id=created_task_1.id, user_id=user_id_2) is None
    assert task_manager.get_task(task_id=None, user_id=user_id_1) is None


def test_update_tasks(
    task_manager: TaskManager, user_id_1: UUID, user_id_2: UUID
) -> None:

    created_task_1 = task_manager.create_task(
        CreateTask(name="Dishes", user_id=user_id_1)
    )

    fields_to_update = {
        "name": "Wash & Dry Dishes",
        "status": TaskStatus.DONE,
    }
    expected_task = created_task_1.model_copy(update=fields_to_update)

    updated_task = task_manager.update_task(
        UpdateTask(**{**created_task_1.model_dump(), **fields_to_update}),
        user_id_1,
    )

    assert updated_task == expected_task
    assert task_manager.get_task(created_task_1.id, user_id_1) == expected_task


def test_update_task_returns_none(
    task_manager: TaskManager, user_id_1: UUID, user_id_2: UUID
) -> None:
    user_id_3 = uuid4()

    created_task_1 = task_manager.create_task(
        CreateTask(name="Dishes", user_id=user_id_1)
    )
    created_task_2 = task_manager.create_task(
        CreateTask(name="Wash Clothes", user_id=user_id_2, status=TaskStatus.DOING)
    )

    assert (
        task_manager.update_task(
            UpdateTask(**created_task_1.model_dump()), user_id=user_id_3
        )
        is None
    )
    assert (
        task_manager.update_task(
            UpdateTask(**created_task_1.model_dump()), user_id=user_id_2
        )
        is None
    )


@pytest.mark.skip(
    reason="Skipping this temporarily so that InMemoryTaskManager can be refactored to in a separate commit"
)
def test_delete_task(
    task_manager: TaskManager, user_id_1: UUID, user_id_2: UUID
) -> None:

    task_to_be_deleted = task_manager.create_task(
        CreateTask(name="Dishes", user_id=user_id_1)
    )

    deleted_task = task_manager.delete_task(
        task_to_be_deleted.id,
        user_id_1,
    )

    assert deleted_task == task_to_be_deleted
    assert task_manager.get_task(task_to_be_deleted.id, user_id_1) is None
    task_deleted = task_manager.history.pop()

    assert task_deleted == HistoryEntry(
        id=task_deleted.id,
        type=HistoryEntryType.TASK_DELETED,
        version=HistoryEntryVersion.TASK,
        event=deleted_task.model_dump_json(),
    )

    task_deleted_event = json.loads(task_deleted.model_dump().get("event"))
    # TODO: figure out how to dynamically restore the HistoryEntry.event based on the version
    task_from_event = Task(**task_deleted_event)
    assert task_from_event == deleted_task


def test_delete_task_returns_none(
    task_manager: TaskManager, user_id_1: UUID, user_id_2: UUID
) -> None:
    user_id_3 = uuid4()

    created_task_1 = task_manager.create_task(
        CreateTask(name="Dishes", user_id=user_id_1)
    )
    created_task_2 = task_manager.create_task(
        CreateTask(name="Wash Clothes", user_id=user_id_2, status=TaskStatus.DOING)
    )

    assert task_manager.delete_task(created_task_1.id, user_id=user_id_3) is None
    assert task_manager.delete_task(created_task_1.id, user_id=user_id_2) is None
    assert task_manager.get_task(created_task_1.id, user_id_1) == created_task_1
