import prometheus_client as prometheus

from prometheus_client import CollectorRegistry
from ..models.exceptions import Unauthorized
from sanic import Sanic, Request, response, HTTPResponse
from sanic_ext import openapi
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


        @app.route("/metrics", methods=["GET"])
        @openapi.definition(
            summary="Métriques Prometheus",
            description="Route pour les métriques Prometheus.\n\n**⚠️ Attention** : Cette route nécessite une authentification valide. Son usage est réservé aux administrateurs de l'API.",
            tag="Administration",
        )
        @openapi.response(
            status=200,
            content=openapi.String,
            description="Métriques Prometheus"
        )
        @openapi.response(
            status=401,
            content={
                "application/json": Unauthorized
            },
            description="La ressource demandée nécessite une authentification valide."
        )
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
