from ....components.ratelimit import ratelimit
from ....components.cache import cache
from ....components.response import JSON
from ....components.argument import Argument, inputs
from ....components.rules import Rules
from ....models.responses import Status, Stats, StatsByRegion, BotStats, BotStatsHistory
from ....models.exceptions import RateLimited, BadRequest, NotFound
from ....utils.format import toFloat
from sanic.response import JSONResponse
from sanic import Blueprint, Request
from sanic_ext import openapi


bp = Blueprint(name="Service", url_prefix="/", version=1, version_prefix="v")


# /status
@bp.route("/status", methods=["GET"])
@openapi.definition(
    summary="Statut de l'API",
    description="Retourne le statut de l'API.",
    tag="Service",
)
@openapi.response(
    status=200, content={"application/json": Status}, description="L'API est en ligne."
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard.",
)
@ratelimit()
async def getStatus(request: Request) -> JSONResponse:
    """
    Retourne le statut de l'API.

    :return: JSONResponse
    """
    return JSON(
        request=request,
        success=True,
        message="L'API est en ligne.",
        status=200,
    ).generate()


# /stats
@bp.route("/stats", methods=["GET"])
@openapi.definition(
    summary="Statistiques de l'API",
    description="Retourne les statistiques de l'API.",
    tag="Service",
)
@openapi.response(
    status=200, content={"application/json": Stats}, description="L'API est en ligne."
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard.",
)
@ratelimit()
@cache(ttl=300)
async def getStats(request: Request) -> JSONResponse:
    """
    Retourne les statistiques de l'API.

    :return: JSONResponse
    """
    stats = await request.app.ctx.entities.stats.get()

    return JSON(
        request=request,
        success=True,
        data={
            "regions": stats.get("regions", -1),
            "restaurants": stats.get("restaurants", -1),
            "restaurants_actifs": stats.get("restaurants_actifs", -1),
            "types_restaurants": stats.get("types_restaurants", -1),
            "menus": stats.get("menus", -1),
            "repas": stats.get("repas", -1),
            "categories": stats.get("categories", -1),
            "plats": stats.get("plats", -1),
            "compositions": stats.get("compositions", -1),
        },
        status=200,
    ).generate()


# /stats/regions
@bp.route("/stats/regions", methods=["GET"])
@openapi.definition(
    summary="Statistiques par région",
    description="Retourne les statistiques de l'API agrégées par région (CROUS) : nombre de restaurants, richesse et variété des menus sur l'année scolaire en cours.",
    tag="Service",
)
@openapi.response(
    status=200,
    content={"application/json": StatsByRegion},
    description="Statistiques par région.",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard.",
)
@ratelimit()
@cache(ttl=300)
async def getStatsByRegion(request: Request) -> JSONResponse:
    """
    Retourne les statistiques de l'API agrégées par région.

    :return: JSONResponse
    """
    regions = await request.app.ctx.entities.stats.getByRegion()

    return JSON(
        request=request,
        success=True,
        data=[
            {
                "code": region.get("idreg"),
                "libelle": region.get("libelle"),
                "nb_restaurants": region.get("nb_restaurants"),
                "nb_restaurants_actifs": region.get("nb_restaurants_actifs"),
                "nb_restaurants_avec_menu": region.get("nb_restaurants_avec_menu"),
                "nb_repas": region.get("nb_repas"),
                "nb_categories": region.get("nb_categories"),
                "nb_plats": region.get("nb_plats"),
                "plats_uniques": region.get("plats_uniques"),
            }
            for region in regions
        ],
        status=200,
    ).generate()


# /stats/bot
@bp.route("/stats/bot", methods=["GET"])
@openapi.definition(
    summary="Statistiques du bot Discord",
    description="Retourne le statut et les statistiques du bot Discord CROUStillant (serveurs, utilisateurs, salons, shards, disponibilité). Relevé toutes les 5 minutes.",
    tag="Service",
)
@openapi.response(
    status=200,
    content={"application/json": BotStats},
    description="Statistiques du bot Discord.",
)
@openapi.response(
    status=404,
    content={"application/json": NotFound},
    description="Aucun relevé n'est encore disponible.",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard.",
)
@ratelimit()
@cache(ttl=60)
async def getBotStats(request: Request) -> JSONResponse:
    """
    Retourne les statistiques du bot Discord.

    :return: Le dernier relevé du bot
    """
    stats = await request.app.ctx.entities.bot.getLatest()

    if stats is None:
        return JSON(
            request=request,
            success=False,
            message="Aucun relevé du bot n'est encore disponible.",
            status=404,
        ).generate()

    return JSON(
        request=request,
        success=True,
        data={
            "statut": stats.get("statut"),
            "date": stats.get("date").strftime("%d-%m-%Y %H:%M:%S"),
            "latence_ms": toFloat(stats.get("latence_ms")),
            "serveurs": stats.get("serveurs"),
            "utilisateurs": stats.get("utilisateurs"),
            "salons": stats.get("salons"),
            "shards": stats.get("shards"),
            "disponibilite_24h": toFloat(stats.get("disponibilite_24h")),
            "disponibilite_30j": toFloat(stats.get("disponibilite_30j")),
        },
        status=200,
    ).generate()


# /stats/bot/history
@bp.route("/stats/bot/history", methods=["GET"])
@openapi.definition(
    summary="Évolution des statistiques du bot Discord",
    description="Retourne l'évolution journalière des statistiques du bot Discord CROUStillant (serveurs, utilisateurs, salons, shards, latence moyenne et disponibilité par jour).",
    tag="Service",
)
@openapi.response(
    status=200,
    content={"application/json": BotStatsHistory},
    description="Évolution journalière des statistiques du bot Discord.",
)
@openapi.response(
    status=400,
    content={"application/json": BadRequest},
    description="Le nombre de jours doit être compris entre 1 et 365.",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard.",
)
@openapi.parameter(
    name="jours",
    description="Nombre de jours d'historique (entre 1 et 365, 30 par défaut)",
    required=False,
    schema=int,
    location="query",
    example=30,
)
@ratelimit()
@inputs(
    Argument(
        name="jours",
        description="Nombre de jours d'historique",
        methods={"jours": Rules.history},
        call=int,
        required=False,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    )
)
@cache(ttl=600)
async def getBotStatsHistory(request: Request, jours: int | None) -> JSONResponse:
    """
    Retourne l'évolution journalière des statistiques du bot Discord.

    :param jours: Nombre de jours d'historique
    :return: Une ligne par jour
    """
    history = await request.app.ctx.entities.bot.getHistory(jours or 30)

    return JSON(
        request=request,
        success=True,
        data=[
            {
                "jour": day.get("jour").strftime("%d-%m-%Y"),
                "serveurs": day.get("serveurs"),
                "utilisateurs": day.get("utilisateurs"),
                "salons": day.get("salons"),
                "shards": day.get("shards"),
                "latence_ms": toFloat(day.get("latence_ms")),
                "disponibilite": toFloat(day.get("disponibilite")),
                "releves": day.get("releves"),
            }
            for day in history
        ],
        status=200,
    ).generate()
