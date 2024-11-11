from sanic import Sanic, Request
from .config import AppConfig
from .components.ratelimit import Ratelimiter
from .entities.entities import Entities
from .routes import RouteService, RouteRegions, RouteRestaurants, RoutePlats
from .utils.logger import Logger
from dotenv import load_dotenv
from os import environ
from textwrap import dedent
from asyncpg import create_pool
from datetime import datetime
from pytz import timezone
from aiohttp import ClientSession
from concurrent.futures import ThreadPoolExecutor


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
            # 📝 • Introduction
            CROUStillant est un projet open-source et gratuit qui a pour but de fournir des informations sur les menus des restaurants universitaires en France et en Outre-Mer.  
            ⁣  
            L'API CROUStillant permet d'accéder à toutes les informations stockées dans la base de données du projet :  
            - Les régions où se trouvent les restaurants universitaires.  
            - Les restaurants universitaires.  
            - Les menus et plats proposés par les restaurants universitaires.  
              
            ⁣  
            💻 *Si vous souhaitez contribuer au projet, vous pouvez consulter nos dépôts sur GitHub : [github.com/CROUStillant-Developpement](https://github.com/CROUStillant-Developpement) !*  
            ⁣  
            # 🔒 • Authentification
            L'API CROUStillant ne nécessite pas d'authentification pour accéder aux données.  
            Cependant **les requêtes sont limitées à 200 par minute par adresse IP**.  
            ⁣  
            🏫 *Si vous êtes une organisation (université, entreprise, association, etc.), ou un particulier et que vous avez besoin de plus de requêtes, vous pouvez nous contacter à l'adresse suivante : [croustillant@bayfield.dev](mailto:croustillant@bayfield.dev) !*   
            ⁣  
            # ⚙️ • Données
            - Les données sont mises à jour 4 fois par jour (1h, 9h, 11h et 15h).
            - Toutes les dates sont stockées en UTC+0.  
            ⁣  
            # 📄 • Termes d'utilisation
            Il y a quelques règles à respecter pour toute utilisation de l'API CROUStillant :
            - Vous ne pouvez pas utiliser l'API à des fins commerciales.
            - Vous ne pouvez pas utiliser l'API pour des activités illégales / malveillantes.
            - Vous ne devez pas abuser de l'API (limite de 200 requêtes par minute), l'utilisation de plusieurs adresses IP pour contourner cette limite est interdite.  
               
            ⁣  
            ⚠️ ***Tout abus de l'API entraînera un bannissement de l'adresse IP.***  
            ⁣  
            # 📩 • Contact
            Pour toute question, suggestion, bug, ou problème n'hésitez pas à nous contacter !  
            - E-mail : [croustillant@bayfield.dev](mailto:croustillant@bayfield.dev)  
            - GitHub : [github.com/CROUStillant-Developpement](https://github.com/CROUStillant-Developpement)  
              
            ⁣  
            ![empty](https://raw.githubusercontent.com/CROUStillant-Developpement/CROUStillantAssets/main/banner-small.png)  

            **CROUStillant Développement © 2022 - 2024 | Tous droits réservés.**  
            *CROUStillant n'est pas affilié au 'CROUS' ou au 'CNOUS'.*  
        """
    ),
)


# Enregistrement des variables d'environnement
app.ctx.schema = environ["PGRST_DB_SCHEMA"]


# Enregistrement du rate limiter
app.ctx.ratelimiter = Ratelimiter()


# Enregistrement des routes
app.blueprint(RouteService)
app.blueprint(RouteRegions)
app.blueprint(RouteRestaurants)
app.blueprint(RoutePlats)


@app.listener("before_server_start")
async def setup_app(app: Sanic, loop):
    app.ctx.logs = Logger("logs")
    app.ctx.requests = Logger("requests")
    app.ctx.session = ClientSession()

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
        
    
    app.ctx.executor = ThreadPoolExecutor(max_workers=4)


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

    app.ctx.requests.info(f"{request.headers.get('CF-Connecting-IP')} - [{request.method}] {request.url} - {response.status} ({process * 1000:.2f}ms)")
