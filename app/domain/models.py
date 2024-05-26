from datetime import date, datetime
from enum import Enum
from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel


class TaskStatus(str, Enum):
    PENDING = "Pending"
    DOING = "Doing"
    BLOCKED = "Blocked"
    DONE = "Done"


class Task(BaseModel):
    id: UUID
    name: str
    status: TaskStatus = TaskStatus.PENDING
    labels: List[str] = []
    due_date: Optional[date] = None
    sub_tasks: List = []
    user_id: UUID


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


class HistoryEntryType(Enum):
    TASK_DELETED = "TASK_DELETED"


class HistoryEntryVersion(Enum):
    TASK = "Task"


class HistoryEntry(BaseModel):
    id: UUID
    entity_id: UUID
    type: HistoryEntryType = (HistoryEntryType.TASK_DELETED,)
    version: HistoryEntryVersion
    event: Any
    created_at: datetime
