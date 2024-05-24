from dependency_injector import containers, providers

from domain.task_managers import TaskManager


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["app.api.routes.tasks"])

    task_manager = providers.AbstractFactory(TaskManager)
