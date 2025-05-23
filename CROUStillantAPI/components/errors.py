from .ratelimit import ratelimit
from .response import JSON
from ..exceptions.ratelimit import RatelimitException
from sanic import Sanic
from sanic.exceptions import NotFound, SanicException


class ErrorHandler:
    """
    Classe pour gérer les erreurs
    """
    def __init__(self, app: Sanic) -> None:
        """
        Constructeur de la classe
        """
        self.app = app


        @app.report_exception
        async def catch_any_exception(app: Sanic, exception: Exception):
            if isinstance(exception, RatelimitException):
                pass
            else:
                print("Caught exception:", exception)


        @app.exception(NotFound)
        @ratelimit()
        async def not_found(request, exception):
            return JSON(
                request=request,
                success=False,
                message="La ressource demandée n'existe pas.",
                status=404
            ).generate()


        @app.exception(Exception, SanicException)
        @ratelimit()
        async def handle_exception(request, exception):
            self.app.ctx.logs.error(f"Erreur: {exception}")

            return JSON(
                request=request,
                success=False,
                message=exception.message if hasattr(exception, "message") else "Une erreur s'est produite lors du traitement de votre requête. Nous nous excusons pour la gêne occasionnée, notre équipe est sur le coup !",
                status=500
            ).generate()
