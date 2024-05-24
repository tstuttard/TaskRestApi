from datetime import date
from enum import Enum
from typing import Generic, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel

M = TypeVar("M", bound=BaseModel)


class StandardResponse(BaseModel, Generic[M]):
    """This allows for having the same response structure across all api endpoints"""

    data: M


class TaskStatus(Enum):
    PENDING = "Pending"
    DOING = "Doing"
    BLOCKED = "Blocked"
    DONE = "Done"


class TaskResource(BaseModel):
    id: Optional[UUID] = None
    name: str
    status: TaskStatus = TaskStatus.PENDING
    labels: List[str]
    due_date: Optional[date] = None
    sub_tasks: List
