from sanic import Sanic, Request
from datetime import datetime
from pytz import timezone
from uuid import uuid1


class Middleware:
    """
    Classe pour les middlewares
    """
    def __init__(self, app: Sanic) -> None:
        """
        Initialisation de la classe
        
        :param app: Sanic
        """

        @app.on_request(priority=999)
        async def before_request(request: Request):
            """
            Middleware pour suivre les requêtes entrantes

            :param request: Request
            """
            request.ctx.request_id = str(uuid1())
            request.ctx.process_time_start = datetime.now(timezone("Europe/Paris")).timestamp()


        @app.on_response
        async def after_request(request: Request, response):
            """
            Middleware pour suivre les réponses

            :param request: Request
            :param response: Response
            """
            request.ctx.process_time_end = datetime.now(timezone("Europe/Paris")).timestamp()
            request.ctx.process_time = int((request.ctx.process_time_end - request.ctx.process_time_start) * 1000)

            response.headers["X-Request-ID"] = request.ctx.request_id
            response.headers["X-Processing-Time"] = f"{request.ctx.process_time}ms"
            response.headers["X-API"] = "CROUStillantAPI"
            response.headers["X-API-Version"] = f"v{app.config.API_VERSION}"
            response.headers["Content-Language"] = "fr-FR"
