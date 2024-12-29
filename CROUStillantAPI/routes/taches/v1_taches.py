from ...components.ratelimit import ratelimit
from ...models.responses import Taches, Tache
from ...models.exceptions import RateLimited, BadRequest, NotFound
from sanic.response import JSONResponse, json
from sanic import Blueprint, Request
from sanic_ext import openapi


bp = Blueprint(
    name="Taches",
    url_prefix="/taches",
    version=1,
    version_prefix="v"
)


# /taches
@bp.route("/", methods=["GET"])
@openapi.definition(
    summary="Liste des 100 dernières tâches",
    description="Liste des 100 dernières tâches ajoutées à la base de données.",
    tag="Taches",
)
@openapi.response(
    status=200,
    content={
        "application/json": Taches
    },
    description="Liste des 100 dernières tâches ajoutées à la base de données."
)
@openapi.response(
    status=429,
    content={
        "application/json": RateLimited
    },
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard."
)
@ratelimit()
async def getTaches(request: Request) -> JSONResponse:
    """
    Récupère les 100 dernières tâches.

    :return: Les 100 dernières tâches
    """
    taches = await request.app.ctx.entities.taches.getLast(100)

    return json(
        {
            "success": True,
            "data": [
                {
                    "id": tache.get("id"),
                    "debut": tache.get("debut").strftime("%d-%m-%Y %H:%M:%S"),
                    "debut_regions": tache.get("debut_regions"),
                    "debut_restaurants": tache.get("debut_restaurants"),
                    "debut_types_restaurants": tache.get("debut_types_restaurants"),
                    "debut_menus": tache.get("debut_menus"),
                    "debut_repas": tache.get("debut_repas"),
                    "debut_categories": tache.get("debut_categories"),
                    "debut_plats": tache.get("debut_plats"),
                    "debut_compositions": tache.get("debut_compositions"),
                    "fin": tache.get("fin").strftime("%d-%m-%Y %H:%M:%S") if tache.get("fin") is not None else None,
                    "fin_regions": tache.get("fin_regions"),
                    "fin_restaurants": tache.get("fin_restaurants"),
                    "fin_types_restaurants": tache.get("fin_types_restaurants"),
                    "fin_menus": tache.get("fin_menus"),
                    "fin_repas": tache.get("fin_repas"),
                    "fin_categories": tache.get("fin_categories"),
                    "fin_plats": tache.get("fin_plats"),
                    "fin_compositions": tache.get("fin_compositions"),
                    "requetes": tache.get("requetes"),
                } for tache in taches
            ]
        },
        status=200
    )


# /taches/{code}
@bp.route("/<code>", methods=["GET"])
@openapi.definition(
    summary="Détails d'une tâche",
    description="Détails d'une tâche en fonction de son code.",
    tag="Taches",
)
@openapi.response(
    status=200,
    content={
        "application/json": Tache
    },
    description="Détails d'une tâche."
)
@openapi.response(
    status=400,
    content={
        "application/json": BadRequest
    },
    description="L'ID de la tâche doit être un nombre."
)
@openapi.response(
    status=404,
    content={
        "application/json": NotFound
    },
    description="La tâche n'existe pas."
)
@openapi.response(
    status=429,
    content={
        "application/json": RateLimited
    },
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard."
)
@openapi.parameter(
    name="code",
    description="ID de la tâche",
    required=True,
    schema=int,
    location="path",
    example=1
)
@ratelimit()
async def getTache(request: Request, code: int) -> JSONResponse:
    """
    Retourne les détails d'une tâche.

    :param code: ID de la tâche
    :return: Les détails de la tâche
    """
    try:
        tacheID = int(code)
    except ValueError:
        return json(
            {
                "success": False,
                "message": "L'ID de la tâche doit être un nombre."
            },
            status=400
        )

    tache = await request.app.ctx.entities.taches.getOne(tacheID)

    if tache is None:
        return json(
            {
                "success": False,
                "message": "La tâche n'existe pas."
            },
            status=404
        )

    return json(
        {
            "success": True,
            "data": {
                "id": tache.get("id"),
                "debut": tache.get("debut").strftime("%d-%m-%Y %H:%M:%S"),
                "debut_regions": tache.get("debut_regions"),
                "debut_restaurants": tache.get("debut_restaurants"),
                "debut_types_restaurants": tache.get("debut_types_restaurants"),
                "debut_menus": tache.get("debut_menus"),
                "debut_repas": tache.get("debut_repas"),
                "debut_categories": tache.get("debut_categories"),
                "debut_plats": tache.get("debut_plats"),
                "debut_compositions": tache.get("debut_compositions"),
                "fin": tache.get("fin").strftime("%d-%m-%Y %H:%M:%S") if tache.get("fin") is not None else None,
                "fin_regions": tache.get("fin_regions"),
                "fin_restaurants": tache.get("fin_restaurants"),
                "fin_types_restaurants": tache.get("fin_types_restaurants"),
                "fin_menus": tache.get("fin_menus"),
                "fin_repas": tache.get("fin_repas"),
                "fin_categories": tache.get("fin_categories"),
                "fin_plats": tache.get("fin_plats"),
                "fin_compositions": tache.get("fin_compositions"),
                "requetes": tache.get("requetes"),
                "restaurants": [
                    restaurant.get("rid") for restaurant in await request.app.ctx.entities.taches.getRestaurants(tacheID)
                ]
            }
        },
        status=200
    )
