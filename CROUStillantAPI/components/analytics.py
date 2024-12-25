from sanic import Sanic, Request
from datetime import datetime
from asyncpg import Pool


class Analytics:
    """
    Classe pour les
    """
    def __init__(self, app: Sanic, analytics: Pool) -> None:
        """
        Initialisation de la classe
        
        :param app: Sanic
        :param analytics: Pool
        """
        

        # Middlewares pour suivre les requêtes
        @app.middleware("request")
        async def track_requests_request(request) -> None:
            """
            Middleware pour suivre les requêtes entrantes
            """
            request.ctx.process_time = datetime.now().timestamp()


        @app.middleware("response")
        async def track_requests_response(request, response) -> None:
            """
            Middleware pour suivre les réponses
            """
