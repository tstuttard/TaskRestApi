import abc
from contextlib import AbstractContextManager
from enum import Enum
from typing import Any, Callable, cast, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlalchemy import delete, insert, select, update
from sqlalchemy.orm import Session

from app.entities import TaskEntity
from app.domain.models import CreateTask, Task, UpdateTask


class TaskManager(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def create_task(self, create_task: CreateTask) -> Optional[Task]:
        pass

    @abc.abstractmethod
    def get_task(self, task_id: UUID, user_id: UUID) -> Optional[Task]:
        pass

    @abc.abstractmethod
    def get_tasks(self, user_id: UUID) -> List[Task]:
        pass

    @abc.abstractmethod
    def update_task(self, update_task: UpdateTask, user_id: UUID) -> Optional[Task]:
        pass

    @abc.abstractmethod
    def delete_task(self, task_id: UUID, user_id: UUID) -> Optional[Task]:
        pass


class HistoryEntryType(Enum):
    TASK_DELETED = "TASK_DELETED"


class HistoryEntryVersion(Enum):
    TASK = "Task"


class HistoryEntry(BaseModel):
    id: UUID
    type: HistoryEntryType = (HistoryEntryType.TASK_DELETED,)
    version: HistoryEntryVersion
    event: Any


class InMemoryTaskManager(TaskManager):
    tasks: Dict[UUID, Dict[UUID, Task]]
    history: List[HistoryEntry] = []

    def __init__(
        self, tasks: Dict[UUID, Task] = None, history: List[HistoryEntry] = None
    ):
        if tasks is None:
            tasks = {}
        if history is None:
            history = []
        self.tasks = tasks
        self.history = history

    def create_task(self, create_task: CreateTask) -> Optional[Task]:
        task = Task(
            id=uuid4(),
            name=create_task.name,
            status=create_task.status,
            labels=create_task.labels,
            due_date=create_task.due_date,
            sub_tasks=create_task.sub_tasks,
            user_id=create_task.user_id,
        )
        if task.user_id not in self.tasks:
            self.tasks.update({task.user_id: {task.id: task}})
        else:
            self.tasks.get(task.user_id).update({task.id: task})

        return task

    def get_task(self, task_id: UUID, user_id: UUID) -> Optional[Task]:
        if user_id not in self.tasks:
            return None
        return self.tasks.get(user_id).get(task_id, None)

    def get_tasks(self, user_id: UUID) -> List[Task]:
        user_tasks = self.tasks.get(user_id)
        if user_tasks is None:
            return []
        else:
            return list(user_tasks.values())

    def update_task(self, update_task: UpdateTask, user_id: UUID) -> Optional[Task]:
        user_tasks = self.tasks.get(user_id)
        if user_tasks is None:
            return None
        if update_task.id not in user_tasks:
            return None

        updated_task = Task(**{**update_task.model_dump(), "user_id": user_id})
        user_tasks.update({update_task.id: updated_task})

        return updated_task

    def delete_task(self, task_id: UUID, user_id: UUID) -> Optional[Task]:
        user_tasks = self.tasks.get(user_id)
        if user_tasks is None:
            return None
        if task_id not in user_tasks:
            return None

        deleted_task = user_tasks.pop(task_id, None)

        self.history.append(
            HistoryEntry(
                id=deleted_task.id,
                type=HistoryEntryType.TASK_DELETED,
                version=HistoryEntryVersion.TASK,
                event=deleted_task.model_dump_json(),
            )
        )

        return deleted_task


class SqliteTaskManager(TaskManager):

    def __init__(
        self, session_factory: Callable[..., AbstractContextManager[Session]]
    ) -> None:
        self.session_factory = session_factory

    def create_task(self, create_task: CreateTask) -> Optional[Task]:
        with self.session_factory() as session:
            task_entity = TaskEntity(
                id=uuid4(),
                name=create_task.name,
                status=create_task.status,
                # labels=create_task.labels,
                due_date=create_task.due_date,
                # sub_tasks=create_task.sub_tasks,
                user_id=create_task.user_id,
            )
            statement = insert(TaskEntity).values(
                id=task_entity.id,
                name=task_entity.name,
                status=task_entity.status,
                # labels=task_entity.labels,
                due_date=task_entity.due_date,
                # sub_tasks=task_entity.sub_tasks,
                user_id=task_entity.user_id,
            )
            result = session.execute(statement)
            session.commit()

            if result.rowcount == 0:
                return None

            task = Task(
                id=task_entity.id,
                name=task_entity.name,
                status=task_entity.status,
                labels=[],
                due_date=task_entity.due_date,
                sub_tasks=[],
                user_id=task_entity.user_id,
            )

            return task

    def get_task(self, task_id: UUID, user_id: UUID) -> Optional[Task]:
        with self.session_factory() as session:
            statement = select(TaskEntity).where(
                cast("ColumnElement[bool]", TaskEntity.id == task_id),
                cast("ColumnElement[bool]", TaskEntity.user_id == user_id),
            )
            result = session.execute(statement)
            task_entity = result.scalars().first()
            if task_entity is None:
                return None

            task = Task(
                id=task_entity.id,
                name=task_entity.name,
                status=task_entity.status,
                labels=[],
                due_date=task_entity.due_date,
                sub_tasks=[],
                user_id=task_entity.user_id,
            )

            return task

    def get_tasks(self, user_id: UUID) -> List[Task]:
        with self.session_factory() as session:
            statement = select(TaskEntity).where(
                cast("ColumnElement[bool]", TaskEntity.user_id == user_id),
            )
            result = session.execute(statement)
            task_entities = result.scalars().all()

            tasks = []
            for task_entity in task_entities:
                task = Task(
                    id=task_entity.id,
                    name=task_entity.name,
                    status=task_entity.status,
                    labels=[],
                    due_date=task_entity.due_date,
                    sub_tasks=[],
                    user_id=task_entity.user_id,
                )
                tasks.append(task)

            return tasks

    def update_task(self, update_task: UpdateTask, user_id: UUID) -> Optional[Task]:
        task_to_update = self.get_task(update_task.id, user_id)
        if task_to_update is None:
            return None

        with self.session_factory() as session:
            statement = (
                update(TaskEntity)
                .where(
                    cast("ColumnElement[bool]", TaskEntity.id == update_task.id),
                    cast("ColumnElement[bool]", TaskEntity.user_id == user_id),
                )
                .values(
                    name=update_task.name,
                    status=update_task.status,
                    # labels=update_task.labels,
                    due_date=update_task.due_date,
                    # sub_tasks=update_task.sub_tasks,
                )
            )
            result = session.execute(statement)
            if result.rowcount == 0:
                return None
            session.commit()

            return self.get_task(update_task.id, user_id)

    def delete_task(self, task_id: UUID, user_id: UUID) -> Optional[Task]:
        task_to_delete = self.get_task(task_id, user_id)
        if task_to_delete is None:
            return None

        with self.session_factory() as session:
            statement = delete(TaskEntity).where(
                cast("ColumnElement[bool]", TaskEntity.id == task_to_delete.id),
                cast("ColumnElement[bool]", TaskEntity.user_id == user_id),
            )

            result = session.execute(statement)
            if result.rowcount == 0:
                return None
            session.commit()
            return task_to_delete
