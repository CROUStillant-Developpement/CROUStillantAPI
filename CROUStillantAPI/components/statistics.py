import prometheus_client as prometheus

from prometheus_client import CollectorRegistry
from sanic import Sanic, Request, response, HTTPResponse
from sanic_ext import openapi
from os import environ
from dotenv import load_dotenv


load_dotenv(dotenv_path=".env")


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


        @app.middleware("response", priority=999)
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
            ).observe(request.ctx.process_time)


        @app.route("/metrics", methods=["GET"])
        @openapi.no_autodoc
        @openapi.exclude()
        async def metrics(request: Request) -> HTTPResponse:
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
