import abc
import datetime
import json
from contextlib import AbstractContextManager
from typing import Callable, cast, Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import ColumnElement, delete, insert, select, update
from sqlalchemy.orm import Session

from app.entities import HistoryEntity, TaskEntity
from app.domain.models import (
    CreateTask,
    Task,
    UpdateTask,
    HistoryEntry,
    HistoryEntryType,
    HistoryEntryVersion,
)
from app.domain.errors import TaskAlreadyExists


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

    @abc.abstractmethod
    def get_last_history_entry(
        self, task_id: UUID, user_id: UUID
    ) -> Optional[HistoryEntry]:
        pass

    @abc.abstractmethod
    def restore_task(self, task_id: UUID, user_id: UUID) -> Optional[Task]:
        pass


class InMemoryTaskManager(TaskManager):
    tasks: Dict[UUID, Dict[UUID, Task]]
    history: Dict[UUID, Dict[UUID, List[HistoryEntry]]] = {}

    def __init__(
        self,
        tasks: Optional[Dict[UUID, Dict[UUID, Task]]] = None,
        history: Optional[Dict[UUID, Dict[UUID, List[HistoryEntry]]]] = None,
    ):
        if tasks is None:
            tasks = {}
        if history is None:
            history = {}
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
        user_tasks = self.tasks.get(task.user_id, None)
        if user_tasks is None:
            self.tasks.update({task.user_id: {task.id: task}})
        else:
            user_tasks.update({task.id: task})

        return task

    def get_task(self, task_id: UUID, user_id: UUID) -> Optional[Task]:
        user_tasks = self.tasks.get(user_id, None)
        if user_tasks is None:
            return None
        return user_tasks.get(task_id, None)

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

        deleted_task = user_tasks.pop(task_id)

        history_entry = HistoryEntry(
            id=uuid4(),
            entity_id=task_id,
            type=HistoryEntryType.TASK_DELETED,
            version=HistoryEntryVersion.TASK,
            event=deleted_task.model_dump_json(),
            created_at=datetime.datetime.now(),
        )

        user_history = self.history.get(user_id, None)
        if user_history is None or task_id not in user_history:
            self.history.update({user_id: {task_id: [history_entry]}})
        else:
            task_history = user_history.get(task_id, [])
            task_history.append(history_entry)

        return deleted_task

    def get_last_history_entry(
        self, task_id: UUID, user_id: UUID
    ) -> Optional[HistoryEntry]:
        user_history = self.history.get(user_id)
        if user_history is None:
            return None
        if task_id not in user_history:
            return None

        task_history = user_history.get(task_id, [])
        return sorted(task_history, key=lambda entry: entry.created_at, reverse=True)[0]

    def restore_task(self, task_id: UUID, user_id: UUID) -> Optional[Task]:
        if self.get_task(task_id, user_id) is not None:
            raise TaskAlreadyExists(task_id)

        last_history_entry = self.get_last_history_entry(task_id, user_id)

        if last_history_entry is None:
            return None

        deleted_task = Task(**json.loads(last_history_entry.model_dump().get("event")))

        if deleted_task.user_id not in self.tasks:
            self.tasks.update({deleted_task.user_id: {deleted_task.id: deleted_task}})
        else:
            self.tasks.get(deleted_task.user_id, {}).update(
                {deleted_task.id: deleted_task}
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
                cast(ColumnElement[bool], TaskEntity.id == task_id),
                cast(ColumnElement[bool], TaskEntity.user_id == user_id),
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
                cast(ColumnElement[bool], TaskEntity.user_id == user_id),
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
                    cast(ColumnElement[bool], TaskEntity.id == update_task.id),
                    cast(ColumnElement[bool], TaskEntity.user_id == user_id),
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
                cast(ColumnElement[bool], TaskEntity.id == task_to_delete.id),
                cast(ColumnElement[bool], TaskEntity.user_id == user_id),
            )

            result = session.execute(statement)
            if result.rowcount == 0:
                return None

            history_insert_statement = insert(HistoryEntity).values(
                id=uuid4(),
                entity_id=task_id,
                type=HistoryEntryType.TASK_DELETED,
                version=HistoryEntryVersion.TASK,
                event=task_to_delete.model_dump_json(),
                created_at=datetime.datetime.now(),
            )
            history_insert_result = session.execute(history_insert_statement)
            if history_insert_result.rowcount == 0:
                return None

            session.commit()

            return task_to_delete

    def get_last_history_entry(
        self, task_id: UUID, user_id: UUID
    ) -> Optional[HistoryEntry]:
        if user_id is None:
            return None
        with self.session_factory() as session:
            statement = (
                select(HistoryEntity)
                .where(
                    cast(ColumnElement[bool], HistoryEntity.entity_id == task_id),
                    cast(
                        ColumnElement[bool],
                        HistoryEntity.type == HistoryEntryType.TASK_DELETED,
                    ),
                )
                .order_by(HistoryEntity.created_at.desc())
            )
            result = session.execute(statement)
            history_entity: HistoryEntity = result.scalars().first()
            if history_entity is None:
                return None

            history_entry = HistoryEntry(
                id=history_entity.id,
                entity_id=history_entity.entity_id,
                type=history_entity.type,
                version=history_entity.version,
                event=history_entity.event,
                created_at=history_entity.created_at,
            )
            # TODO: figure out how to dynamically restore the HistoryEntry.event based on the version
            task_deleted_event = Task(
                **json.loads(history_entry.model_dump().get("event"))
            )

            if task_deleted_event.user_id != user_id:
                return None

            return history_entry

    def restore_task(self, task_id: UUID, user_id: UUID) -> Optional[Task]:
        if self.get_task(task_id, user_id) is not None:
            raise TaskAlreadyExists(task_id)

        last_history_entry = self.get_last_history_entry(task_id, user_id)

        if last_history_entry is None:
            return None

        deleted_task = Task(**json.loads(last_history_entry.model_dump().get("event")))

        with self.session_factory() as session:

            statement = insert(TaskEntity).values(
                id=deleted_task.id,
                name=deleted_task.name,
                status=deleted_task.status,
                # labels=deleted_task.labels,
                due_date=deleted_task.due_date,
                # sub_tasks=deleted_task.sub_tasks,
                user_id=deleted_task.user_id,
            )
            result = session.execute(statement)
            session.commit()

            if result.rowcount == 0:
                return None

            return deleted_task
