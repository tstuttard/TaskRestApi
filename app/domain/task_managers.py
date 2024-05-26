import abc
from datetime import date
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel


class TaskStatus(Enum):
    PENDING = "Pending"
    DOING = "Doing"
    BLOCKED = "Blocked"
    DONE = "Done"


class CreateTask(BaseModel):
    name: str
    status: TaskStatus = TaskStatus.PENDING
    labels: List[str] = []
    due_date: Optional[date] = None
    sub_tasks: List = []
    user_id: UUID


class UpdateTask(BaseModel):
    id: UUID
    name: str
    status: TaskStatus
    labels: List[str]
    due_date: Optional[date]
    sub_tasks: List


class Task(BaseModel):
    id: UUID
    name: str
    status: TaskStatus = TaskStatus.PENDING
    labels: List[str] = []
    due_date: Optional[date] = None
    sub_tasks: List = []
    user_id: UUID


class TaskManager(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def create_task(self, create_task: CreateTask) -> Task:
        pass

    @abc.abstractmethod
    def get_task(self, task_id: UUID, user_id: UUID) -> Task:
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

    def create_task(self, create_task: CreateTask) -> Task:
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
    def create_task(self, create_task: CreateTask) -> Task:
        pass

    def get_task(self, task_id: UUID, user_id: UUID) -> Task:
        pass

    def get_tasks(self, user_id: UUID) -> List[Task]:
        pass

    def update_task(self, update_task: UpdateTask, user_id: UUID) -> Optional[Task]:
        pass

    def delete_task(self, task_id: UUID, user_id: UUID) -> Optional[Task]:
        pass
