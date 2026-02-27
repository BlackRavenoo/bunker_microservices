from dependency_injector import containers, providers

from services.game_service.app.infrastructure.uow import SqlAlchemyUnitOfWork

class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=["app.api.v1.endpoints.games"]
    )

    uow = providers.Factory(
        SqlAlchemyUnitOfWork,
    )

    