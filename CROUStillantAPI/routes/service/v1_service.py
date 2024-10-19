from models.responses import Status, Stats
from models.exceptions import RateLimited
from sanic.response import JSONResponse, json
from sanic import Blueprint, Request
from sanic_ext import openapi


bp = Blueprint(
    name="Service",
    version=1,
    version_prefix="v"
)


# /status
@bp.route("/status", methods=["GET"])
@openapi.definition(
    summary="Statut de l'API",
    description="Retourne le statut de l'API.",
    tag="Service",
)
@openapi.response(
    status=200,
    content={
        "application/json": Status
    },
    description="L'API est en ligne."
)
@openapi.response(
    status=429,
    content={
        "application/json": RateLimited
    },
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard."
)
async def getStatus(request: Request) -> JSONResponse:
    """
    Retourne le statut de l'API.

    :return: JSONResponse
    """
    return json(
        {
            "success": True,
            "message": "L'API est en ligne."
        },
        status=200
    )


# /stats
@bp.route("/stats", methods=["GET"])
@openapi.definition(
    summary="Statistiques de l'API",
    description="Retourne les statistiques de l'API.",
    tag="Service",
)
@openapi.response(
    status=200,
    content={
        "application/json": Stats
    },
    description="L'API est en ligne."
)
@openapi.response(
    status=429,
    content={
        "application/json": RateLimited
    },
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard."
)
async def getStats(request: Request) -> JSONResponse:
    """
    Retourne les statistiques de l'API.

    :return: JSONResponse
    """
    stats = await request.app.ctx.entities.stats.get()

    return json(
        {
            "success": True,
            "data": {
                "regions": stats.get("regions"),
                "restaurants": stats.get("restaurants"),
                "types_restaurants": stats.get("types_restaurants"),
                "menus": stats.get("menus"),
                "repas": stats.get("repas"),
                "categories": stats.get("categories"),
                "plats": stats.get("plats"),
                "compositions": stats.get("compositions"),
            }
        },
        status=200
    )
