import traceback
import asyncio

from .ratelimit import ratelimit
from .response import JSON
from ..exceptions.ratelimit import RatelimitException
from ..exceptions.forbidden import ForbiddenException
from sanic import Sanic
from sanic.exceptions import NotFound, MethodNotAllowed, SanicException
from asyncpg.exceptions import ConnectionDoesNotExistError


class ErrorHandler:
    """
    Classe pour gérer les erreurs
    """

    def __init__(self, app: Sanic) -> None:
        """
        Constructeur de la classe
        """
        self.app = app

        @app.exception(NotFound)
        @ratelimit()
        async def handle_not_found(request, exception):
            return JSON(
                request=request,
                success=False,
                message="La ressource demandée n'existe pas.",
                status=exception.status_code,
            ).generate()

        @app.exception(ForbiddenException)
        async def handle_forbidden(request, exception):
            return JSON(
                request=request,
                success=False,
                message=exception.message,
                status=exception.status_code,
            ).generate()

        @app.exception(RatelimitException)
        async def handle_ratelimit(request, exception):
            return JSON(
                request=request,
                success=False,
                message=exception.message,
                status=exception.status_code,
            ).generate()

        @app.exception(MethodNotAllowed)
        @ratelimit()
        async def handle_method_not_allowed(request, exception):
            return JSON(
                request=request,
                success=False,
                message=f"La méthode {request.method} n'est pas autorisée pour cette route.",
                status=405,
            ).generate()

        @app.exception(ConnectionDoesNotExistError, ConnectionRefusedError)
        @ratelimit()
        async def handle_db_connection_error(request, exception):
            self.app.ctx.logs.error(
                f"Erreur de connexion à la base de données: {exception}"
            )

            return JSON(
                request=request,
                success=False,
                message="Le service est temporairement indisponible en raison de problèmes de connexion à la base de données. Veuillez réessayer plus tard.",
                status=503,
            ).generate()

        @app.exception(TimeoutError, asyncio.TimeoutError)
        @ratelimit()
        async def handle_timeout_error(request, exception):
            self.app.ctx.logs.warning(
                f"Timeout base de données [{type(exception).__name__}] {request.method} {request.path}"
            )

            return JSON(
                request=request,
                success=False,
                message="Le service est temporairement indisponible. Veuillez réessayer dans quelques instants.",
                status=503,
            ).generate()

        @app.exception(Exception, SanicException)
        @ratelimit()
        async def handle_exception(request, exception):
            tb = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))
            self.app.ctx.logs.error(
                f"Erreur 500 [{type(exception).__name__}] {request.method} {request.path}\n{tb}"
            )

            if hasattr(self.app.ctx, "error_webhook"):
                await self.app.ctx.error_webhook.collect(request, exception)

            return JSON(
                request=request,
                success=False,
                message=exception.message
                if hasattr(exception, "message")
                else "Une erreur s'est produite lors du traitement de votre requête. Nous nous excusons pour la gêne occasionnée, notre équipe est sur le coup !",
                status=500,
            ).generate()
