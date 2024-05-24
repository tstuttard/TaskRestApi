import abc
from datetime import date
from enum import Enum
from typing import Dict, List, Optional
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


class InMemoryTaskManager(TaskManager):
    tasks: Dict[UUID, Dict[UUID, Task]]

    def __init__(self, tasks: Dict[UUID, Task] = None):
        if tasks is None:
            tasks = {}
        self.tasks = tasks

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
