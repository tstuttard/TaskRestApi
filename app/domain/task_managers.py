import abc


class TaskManager(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def create_task(self, param):
        pass


class InMemoryTaskManager(TaskManager):
    def create_task(self, param):
        pass
