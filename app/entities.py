from datetime import date, datetime
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.domain.models import HistoryEntryType, HistoryEntryVersion, TaskStatus


class Base(DeclarativeBase):
    type_annotation_map = {dict[str, Any]: JSON}


class TaskEntity(Base):
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


class HistoryEntity(Base):
    __tablename__ = "history"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    entity_id: Mapped[UUID] = mapped_column()

    type: Mapped[HistoryEntryType]
    version: Mapped[HistoryEntryVersion]
    event: Mapped[dict[str, Any]]
    created_at: Mapped[datetime]
