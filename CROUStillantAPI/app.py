from sanic import Sanic, Request
from .config import AppConfig
from .entities.entities import Entities
from .routes import RouteService, RouteRegions, RouteRestaurants, RoutePlats
from .utils.logger import Logger
from dotenv import load_dotenv
from os import environ
from textwrap import dedent
from asyncpg import create_pool
from datetime import datetime
from pytz import timezone


load_dotenv(dotenv_path=f".env")


# Initialisation de l'application
app = Sanic(
    name="CROUStillantAPI",
    config=AppConfig(),
)


# Ajoute des informations à la documentation OpenAPI
app.ext.openapi.raw(
    {
        "servers": [
            {
                "url": f"{environ.get('API_DOMAIN')}",
                "description": "Serveur de production"
            }
        ],
    }
)

app.ext.openapi.describe(
    title=app.name,
    version=f"v{app.config.API_VERSION}",
    description=dedent(
        """
            ![banner](https://raw.githubusercontent.com/CROUStillant-Developpement/CROUStillantAssets/main/images/banner.png)

            CROUStillant est un projet qui a pour but de fournir les menus des restaurants universitaires en France et en Outre-Mer.
        """
    ),
)


# Enregistrement des variables d'environnement
app.ctx.schema = environ["PGRST_DB_SCHEMA"]


# Enregistrement des routes
app.blueprint(RouteService)
app.blueprint(RouteRegions)
app.blueprint(RouteRestaurants)
app.blueprint(RoutePlats)


@app.listener("before_server_start")
async def setup_app(app: Sanic, loop):
    app.ctx.logs = Logger("logs")
    app.ctx.requests = Logger("requests")

    # Chargement de la base de données
    try:
        app.ctx.pool = await create_pool(
            database=environ["POSTGRES_DATABASE"], 
            user=environ["POSTGRES_USER"], 
            password=environ["POSTGRES_PASSWORD"], 
            host=environ["POSTGRES_HOST"],
            port=environ["POSTGRES_PORT"],
            min_size=10,        # 10 connections
            max_size=10,        # 10 connections
            max_queries=50000,  # 50,000 queries
            loop=loop
        )
    except OSError:
        app.ctx.logs.error("Impossible de se connecter à la base de données !")
        app.ctx.logs.debug("Arrêt de l'API !")
        exit(1)


    app.ctx.entities = Entities(app.ctx.pool)

    app.ctx.logs.info("API démarrée")


@app.listener("after_server_stop")
async def close_app(app: Sanic, loop):
    await app.ctx.pool.close()
    await app.ctx.session.close()

    app.ctx.logs.info("API arrêtée")


@app.on_request
async def before_request(request: Request):
    # app.ctx.requests.info(f"{request.client_ip} - [{request.method}] {request.url}")

    request.ctx.start = datetime.now(timezone("Europe/Paris")).timestamp()


@app.on_response
async def after_request(request: Request, response):
    end = datetime.now(timezone("Europe/Paris")).timestamp()
    process = end - request.ctx.start

    app.ctx.requests.info(f"{request.client_ip} - [{request.method}] {request.url} - {response.status} ({process * 1000:.2f}ms)")


if __name__ == "__main__":
    """
    Lancement de l'API en mode développement
    
    [!] Ne pas utiliser en production. Utiliser un serveur WSGI tel que Gunicorn.
    """
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        auto_reload=True
    )
