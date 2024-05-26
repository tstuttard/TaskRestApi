from enum import Enum


class TaskStatus(Enum):
    PENDING = "Pending"
    DOING = "Doing"
    BLOCKED = "Blocked"
    DONE = "Done"
