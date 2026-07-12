from ....components.ratelimit import ratelimit
from ....components.cache import cache
from ....components.response import JSON
from ....models.responses import Status, Stats, StatsByRegion
from ....models.exceptions import RateLimited
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
