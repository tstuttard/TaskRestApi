import json
from datetime import date
from uuid import UUID, uuid4

import pytest

from app.domain.task_managers import (
    TaskManager,
)
from app.domain.models import (
    CreateTask,
    Task,
    UpdateTask,
    TaskStatus,
    HistoryEntry,
    HistoryEntryType,
    HistoryEntryVersion,
)
from app.domain.errors import TaskAlreadyExists


def test_create_task(task_manager: TaskManager, user_id_1: UUID) -> None:
    today = date.today()
    task_to_create_1 = CreateTask(
        name="Dishes", user_id=user_id_1, due_date=today, labels=["kitchen", "daily"]
    )
    task_to_create_2 = CreateTask(
        name="Wash Clothes",
        user_id=user_id_1,
        status=TaskStatus.DOING,
        due_date=today,
    )
    created_task_1 = task_manager.create_task(task_to_create_1)
    created_task_2 = task_manager.create_task(task_to_create_2)

    expected_task_1 = Task(
        id=created_task_1.id,
        name=task_to_create_1.name,
        status=TaskStatus.PENDING,
        user_id=task_to_create_1.user_id,
        due_date=today,
        labels={"kitchen", "daily"},
    )
    expected_task_2 = Task(
        id=created_task_2.id,
        name=task_to_create_2.name,
        status=TaskStatus.DOING,
        user_id=task_to_create_2.user_id,
        due_date=today,
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
        CreateTask(name="Dishes", user_id=user_id_1, labels={"kitchen", "daily"})
    )
    created_task_2 = task_manager.create_task(
        CreateTask(
            name="Wash Clothes",
            user_id=user_id_1,
            status=TaskStatus.DOING,
            labels={"daily", "outside"},
        )
    )
    task_manager.create_task(
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
    task_manager.create_task(
        CreateTask(name="Wash Clothes", user_id=user_id_2, status=TaskStatus.DOING)
    )

    assert task_manager.get_task(task_id=created_task_1.id, user_id=user_id_3) is None
    assert task_manager.get_task(task_id=created_task_1.id, user_id=user_id_2) is None
    assert task_manager.get_task(task_id=None, user_id=user_id_1) is None


def test_update_tasks(
    task_manager: TaskManager, user_id_1: UUID, user_id_2: UUID
) -> None:

    created_task_1 = task_manager.create_task(
        CreateTask(name="Dishes", user_id=user_id_1, labels=["kitchen", "daily"])
    )

    fields_to_update = {
        "name": "Wash & Dry Dishes",
        "status": TaskStatus.DONE,
        "labels": {"kitchen", "hourly"},
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
    task_manager.create_task(
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


def test_delete_task(
    task_manager: TaskManager, user_id_1: UUID, user_id_2: UUID
) -> None:

    task_to_be_deleted = task_manager.create_task(
        CreateTask(name="Dishes", user_id=user_id_1, label={"kitchen", "daily"})
    )

    deleted_task = task_manager.delete_task(
        task_to_be_deleted.id,
        user_id_1,
    )

    assert deleted_task == task_to_be_deleted
    assert task_manager.get_task(task_to_be_deleted.id, user_id_1) is None

    task_deleted = task_manager.get_last_history_entry(task_to_be_deleted.id, user_id_1)

    assert task_deleted == HistoryEntry(
        id=task_deleted.id,
        entity_id=task_to_be_deleted.id,
        type=HistoryEntryType.TASK_DELETED,
        version=HistoryEntryVersion.TASK,
        event=deleted_task.model_dump_json(),
        created_at=task_deleted.created_at,
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
    task_manager.create_task(
        CreateTask(name="Wash Clothes", user_id=user_id_2, status=TaskStatus.DOING)
    )

    assert task_manager.delete_task(created_task_1.id, user_id=user_id_3) is None
    assert task_manager.delete_task(created_task_1.id, user_id=user_id_2) is None
    assert task_manager.get_task(created_task_1.id, user_id_1) == created_task_1


def test_get_last_history_entry_returns_none(
    task_manager: TaskManager, user_id_1: UUID, user_id_2: UUID
) -> None:
    user_id_3 = uuid4()

    created_task_1 = task_manager.create_task(
        CreateTask(name="Dishes", user_id=user_id_1)
    )
    created_task_2 = task_manager.create_task(
        CreateTask(name="Wash Clothes", user_id=user_id_2, status=TaskStatus.DOING)
    )
    task_manager.create_task(CreateTask(name="Cook", user_id=user_id_1))
    task_manager.delete_task(created_task_1.id, user_id=user_id_1)
    task_manager.delete_task(created_task_2.id, user_id=user_id_2)

    assert (
        task_manager.get_last_history_entry(created_task_1.id, user_id=user_id_3)
        is None
    )
    assert (
        task_manager.get_last_history_entry(created_task_1.id, user_id=user_id_2)
        is None
    )
    history_entry = task_manager.get_last_history_entry(created_task_1.id, user_id_1)
    assert history_entry == HistoryEntry(
        id=history_entry.id,
        entity_id=created_task_1.id,
        type=HistoryEntryType.TASK_DELETED,
        version=HistoryEntryVersion.TASK,
        event=created_task_1.model_dump_json(),
        created_at=history_entry.created_at,
    )


def test_restore_task(task_manager: TaskManager, user_id_1: UUID) -> None:
    created_task = task_manager.create_task(
        CreateTask(
            name="Dishes",
            user_id=user_id_1,
            status=TaskStatus.DONE,
            labels={"kitchen", "daily"},
        )
    )
    task_manager.delete_task(created_task.id, user_id_1)
    assert task_manager.get_task(created_task.id, user_id_1) is None

    restored_task = task_manager.restore_task(created_task.id, user_id_1)

    assert restored_task == created_task
    assert task_manager.get_task(created_task.id, user_id_1) == restored_task


def test_restore_task_returns_none(
    task_manager: TaskManager, user_id_1: UUID, user_id_2
) -> None:
    user_id_3 = uuid4()
    created_task_1 = task_manager.create_task(
        CreateTask(name="Dishes", user_id=user_id_1)
    )
    created_task_2 = task_manager.create_task(
        CreateTask(name="Wash Clothes", user_id=user_id_2, status=TaskStatus.DOING)
    )
    created_task_3 = task_manager.create_task(
        CreateTask(name="Cook", user_id=user_id_1, status=TaskStatus.DOING)
    )
    task_manager.delete_task(created_task_1.id, user_id_1)
    task_manager.delete_task(created_task_2.id, user_id_2)
    task_manager.delete_task(created_task_3.id, user_id_1)

    assert task_manager.restore_task(created_task_1.id, user_id=user_id_3) is None
    assert task_manager.restore_task(created_task_1.id, user_id=user_id_2) is None
    assert task_manager.restore_task(created_task_3.id, user_id=user_id_3) is None


def test_restore_task_already_exists(
    task_manager: TaskManager, user_id_1: UUID
) -> None:
    created_task = task_manager.create_task(
        CreateTask(name="Dishes", user_id=user_id_1, status=TaskStatus.DONE)
    )
    task_manager.delete_task(created_task.id, user_id_1)
    assert task_manager.get_task(created_task.id, user_id_1) is None

    task_manager.restore_task(created_task.id, user_id_1)

    with pytest.raises(
        TaskAlreadyExists,
    ) as e:
        task_manager.restore_task(created_task.id, user_id_1)

    assert e.value.task_id == created_task.id
