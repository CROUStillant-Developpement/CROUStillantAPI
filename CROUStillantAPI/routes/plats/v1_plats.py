from ...components.ratelimit import ratelimit
from ...models.responses import Plats, Plat
from ...models.exceptions import RateLimited, BadRequest, NotFound
from sanic.response import JSONResponse, json
from sanic import Blueprint, Request
from sanic_ext import openapi


bp = Blueprint(
    name="Plats",
    url_prefix="/plats",
    version=1,
    version_prefix="v"
)


# /plats
@bp.route("/", methods=["GET"])
@openapi.definition(
    summary="Liste des 100 derniers plats",
    description="Liste des 100 derniers plats ajoutés à la base de données.",
    tag="Plats",
)
@openapi.response(
    status=200,
    content={
        "application/json": Plats
    },
    description="Liste des 100 derniers plats ajoutés à la base de données."
)
@openapi.response(
    status=429,
    content={
        "application/json": RateLimited
    },
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard."
)
@ratelimit()
async def getPlats(request: Request) -> JSONResponse:
    """
    Récupère ls 100 derniers plats ajoutés à la base de données

    :return: Les plats
    """
    # plats = await request.app.ctx.entities.plats.getAll()
    plats = await request.app.ctx.entities.plats.getLast(100)

    return json(
        {
            "success": True,
            "data": [
                {
                    "code": plat.get("platid"),
                    "libelle": plat.get("libelle"),
                } for plat in plats
            ]
        },
        status=200
    )


# /plats/{code}
@bp.route("/<code>", methods=["GET"])
@openapi.definition(
    summary="Détails d'un plat",
    description="Détails d'un plat en fonction de son code.",
    tag="Plats",
)
@openapi.response(
    status=200,
    content={
        "application/json": Plat
    },
    description="Détails d'un plat."
)
@openapi.response(
    status=400,
    content={
        "application/json": BadRequest
    },
    description="L'ID du plat doit être un nombre."
)
@openapi.response(
    status=404,
    content={
        "application/json": NotFound
    },
    description="Le plat n'existe pas."
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
    description="ID du plat",
    required=True,
    schema=int,
    location="path",
    example=1
)
@ratelimit()
async def getPlat(request: Request, code: int) -> JSONResponse:
    """
    Retourne les détails d'un plat.

    :param code: ID du plat
    :return: Le plat
    """
    try:
        platID = int(code)
    except ValueError:
        return json(
            {
                "success": False,
                "message": "L'ID du plat doit être un nombre."
            },
            status=400
        )

    plat = await request.app.ctx.entities.plats.getOne(platID)

    if plat is None:
        return json(
            {
                "success": False,
                "message": "Le plat n'existe pas."
            },
            status=404
        )

    return json(
        {
            "success": True,
            "data": {
                "code": plat.get("platid"),
                "libelle": plat.get("libelle"),
            }
        },
        status=200
    )
