from fastapi import Request, status
from fastapi.responses import JSONResponse

from services.game_service.app.domain.exceptions.exceptions import EntityNotFound, UnexpectedException


async def entity_not_found_handler(
    request: Request, 
    exc: EntityNotFound
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)}
    )

async def entity_not_found_handler(
    request: Request, 
    exc: UnexpectedException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)}
    )