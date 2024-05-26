from uuid import UUID


class Error(Exception):
    pass


class TaskAlreadyExists(Error):

    def __init__(self, task_id: UUID, *args):
        self.task_id = task_id
        super().__init__(*args)
