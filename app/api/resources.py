from datetime import date
from typing import Generic, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel

from app.domain.models import TaskStatus

M = TypeVar("M", bound=BaseModel)


class StandardResponse(BaseModel, Generic[M]):
    """This allows for having the same response structure across all api endpoints"""

    data: M


class CreateTaskRequestBody(BaseModel):
    name: str
    status: TaskStatus = TaskStatus.PENDING
    labels: List[str] = []
    due_date: Optional[date] = None
    sub_tasks: List = []


class UpdateTaskRequestBody(BaseModel):
    id: Optional[UUID] = None
    name: str
    status: TaskStatus
    labels: List[str]
    due_date: Optional[date]
    sub_tasks: List


class TaskResource(BaseModel):
    id: Optional[UUID] = None
    name: str
    status: TaskStatus = TaskStatus.PENDING
    labels: List[str] = []
    due_date: Optional[date] = None
    sub_tasks: List = []
