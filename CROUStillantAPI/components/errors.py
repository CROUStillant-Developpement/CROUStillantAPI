from .ratelimit import ratelimit
from .response import JSON
from ..exceptions.ratelimit import RatelimitException
from sanic.exceptions import NotFound, SanicException


class ErrorHandler:
    """
    Classe pour gérer les erreurs
    """
    def __init__(self, app):
        """
        Constructeur de la classe
        """
        self.app = app


        @app.exception(NotFound)
        @ratelimit()
        async def not_found(request, exception):
            return JSON(
                request=request,
                success=False,
                message="La ressource demandée n'existe pas.",
                status=404
            ).generate()


        @app.exception(RatelimitException)
        @ratelimit()
        async def ratelimit_exception(request, exception):
            return JSON(
                request=request,
                success=False,
                message=exception.message if hasattr(exception, "message") else "Trop de requêtes envoyées. Veuillez réessayer plus tard.",
                status=429
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
