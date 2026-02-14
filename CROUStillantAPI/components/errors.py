from .ratelimit import ratelimit
from .response import JSON
from ..exceptions.ratelimit import RatelimitException
from ..exceptions.forbidden import ForbiddenException
from sanic import Sanic
from sanic.exceptions import NotFound, SanicException
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

        @app.exception(Exception, SanicException)
        @ratelimit()
        async def handle_exception(request, exception):
            self.app.ctx.logs.error(f"Erreur: {exception}")

            return JSON(
                request=request,
                success=False,
                message=exception.message
                if hasattr(exception, "message")
                else "Une erreur s'est produite lors du traitement de votre requête. Nous nous excusons pour la gêne occasionnée, notre équipe est sur le coup !",
                status=500,
            ).generate()
