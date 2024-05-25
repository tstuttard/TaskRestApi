from datetime import date
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.domain.task_managers import TaskStatus


class Base(DeclarativeBase):
    pass


class Task(Base):
    __tablename__ = "task"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str]

    status: Mapped[TaskStatus]
    # TODO: create a new model for labels
    # labels: Mapped[List[str]]
    due_date: Mapped[Optional[date]]
    # TODO: create a new model for sub tasks
    # sub_tasks: Mapped[List[Any]]
    user_id: Mapped[UUID]
