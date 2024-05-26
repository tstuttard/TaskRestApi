from dependency_injector import containers, providers

from app.domain.task_managers import InMemoryTaskManager, SqliteTaskManager


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["app.api.routes.tasks"])

    config = providers.Configuration(yaml_files=["config.yaml"])

    in_memory_task_manager = providers.Singleton(InMemoryTaskManager)
    sqlite_task_manager = providers.Singleton(SqliteTaskManager)

    task_manager = providers.Selector(
        config.task_manager.type,
        in_memory=in_memory_task_manager,
        sqlite=sqlite_task_manager,
    )
