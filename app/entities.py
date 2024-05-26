from datetime import date, datetime
from typing import Any, Optional, Set
from uuid import UUID

from sqlalchemy import Column, ForeignKey, JSON, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.domain.models import HistoryEntryType, HistoryEntryVersion, TaskStatus


class Base(DeclarativeBase):
    type_annotation_map = {dict[str, Any]: JSON}


task_label_table = Table(
    "task_label",
    Base.metadata,
    Column("task_id", ForeignKey("task.id"), primary_key=True),
    Column("label_id", ForeignKey("label.id"), primary_key=True),
)


class TaskEntity(Base):
    __tablename__ = "task"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str]

    status: Mapped[TaskStatus]
    # TODO: create a new model for labels
    labels: Mapped[Set["LabelEntity"]] = relationship(
        "LabelEntity", secondary=task_label_table, back_populates="tasks"
    )
    due_date: Mapped[Optional[date]]
    # TODO: create a new model for sub tasks
    # sub_tasks: Mapped[List[Any]]
    user_id: Mapped[UUID]


class LabelEntity(Base):
    __tablename__ = "label"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str]
    tasks: Mapped[Set[TaskEntity]] = relationship(
        "TaskEntity", secondary=task_label_table, back_populates="labels"
    )


class HistoryEntity(Base):
    __tablename__ = "history"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    entity_id: Mapped[UUID] = mapped_column()

    type: Mapped[HistoryEntryType]
    version: Mapped[HistoryEntryVersion]
    event: Mapped[dict[str, Any]]
    created_at: Mapped[datetime]
