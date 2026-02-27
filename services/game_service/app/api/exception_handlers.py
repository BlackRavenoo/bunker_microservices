from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from shared.src.exceptions import EntityNotFound, EntityAlreadyExists, InvalidOperation, UnexpectedException

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(EntityNotFound)
    async def entity_not_found_handler(request: Request, exc: EntityNotFound):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error_code": exc.error_code}
        )

    @app.exception_handler(EntityAlreadyExists)
    async def entity_already_exists_handler(request: Request, exc: EntityAlreadyExists):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"error_code": exc.error_code}
        )

    @app.exception_handler(UnexpectedException)
    async def unexpected_exception_handler(request: Request, exc: UnexpectedException):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error_code": exc.error_code}
        )
    
    @app.exception_handler(InvalidOperation)
    async def invalid_operation_handler(request: Request, exc: InvalidOperation):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error_code": exc.error_code}
        )