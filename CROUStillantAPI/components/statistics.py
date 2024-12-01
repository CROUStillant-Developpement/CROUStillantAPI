import prometheus_client as prometheus

from prometheus_client import CollectorRegistry
from sanic import Sanic, Request, response, HTTPResponse
from datetime import datetime
from os import environ
from dotenv import load_dotenv


load_dotenv(dotenv_path=f".env")


class PrometheusStatistics:
    """
    Classe pour les statistiques Prometheus
    """
    def __init__(self, app: Sanic) -> None:
        """
        Initialisation de la classe
        
        :param app: Sanic
        """
        self.app = app
        self.registry = CollectorRegistry()

        # Initialisation des métriques Prometheus
        self.requests = prometheus.Counter(
            name="sanic_requests_total", 
            documentation="Requests",
            labelnames=["method", "endpoint", "status"],
            registry=self.registry
        )
        self.requests_duration = prometheus.Histogram(
            name="sanic_requests_duration", 
            documentation="Duration of requests",
            labelnames=["method", "endpoint", "status"],
            registry=self.registry
        )

        # Ajoute la route pour les métriques Prometheus
        self.app.add_route(self.metrics, "/metrics")

        # Middlewares pour suivre les requêtes
        @self.app.middleware("request")
        async def track_requests_request(request) -> None:
            """
            Middleware pour suivre les requêtes entrantes
            """
            request.ctx.process_time = datetime.now().timestamp()


        @self.app.middleware("response")
        async def track_requests_response(request, response) -> None:
            """
            Middleware pour suivre les réponses
            """
            self.requests.labels(
                method=request.method,
                endpoint=request.path,
                status=response.status
            ).inc()

            self.requests_duration.labels(
                method=request.method,
                endpoint=request.path,
                status=response.status
            ).observe(datetime.now().timestamp() - request.ctx.process_time)


    async def metrics(self, request: Request) -> HTTPResponse:
        """
        Route pour les métriques Prometheus
        
        :param request: Request
        :return: HTTPResponse
        """
        # Check if the request is authorized to access the metrics
        if request.headers.get("Authorization") != environ["PROMETHEUS_AUTH"]:
            return response.json(
                {
                "message": "La ressource demandée nécessite une authentification valide !",
                "success": False
                },
                status=401
            )

        output = prometheus.exposition.generate_latest(self.registry).decode("utf-8")
        content_type = prometheus.exposition.CONTENT_TYPE_LATEST
        return response.text(
            body=output,        
            content_type=content_type
        )
