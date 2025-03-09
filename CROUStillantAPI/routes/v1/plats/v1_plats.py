from ....components.ratelimit import ratelimit
from ....components.response import JSON
from ....models.responses import Plats, Plat, PlatsWithTotal
from ....models.exceptions import RateLimited, BadRequest, NotFound
from sanic.response import JSONResponse
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
    Récupère les 100 derniers plats ajoutés à la base de données

    :return: Les plats
    """
    # plats = await request.app.ctx.entities.plats.getAll()
    plats = await request.app.ctx.entities.plats.getLast(100)

    return JSON(
        request=request,
        success=True,
        data=[
            {
                "code": plat.get("platid"),
                "libelle": plat.get("libelle"),
            } for plat in plats
        ],
        status=200
    ).generate()


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
        return JSON(
            request=request,
            success=False,
            status=400,
            message="L'ID du plat doit être un nombre."
        ).generate()


    plat = await request.app.ctx.entities.plats.getOne(platID)

    if plat is None:
        return JSON(
            request=request,
            success=False,
            status=404,
            message="Le plat n'existe pas."
        ).generate()


    return JSON(
        request=request,
        success=True,
        data={
            "code": plat.get("platid"),
            "libelle": plat.get("libelle"),
        },
        status=200
    ).generate()


# /plats/top
@bp.route("/top", methods=["GET"])
@openapi.definition(
    summary="Top 100 des plats",
    description="Top 100 des plats les plus populaires.",
    tag="Plats",
)
@openapi.response(
    status=200,
    content={
        "application/json": PlatsWithTotal
    },
    description="Top 100 des plats les plus populaires."
)
@openapi.response(
    status=429,
    content={
        "application/json": RateLimited
    },
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard."
)
@ratelimit()
async def getPlatTop(request: Request) -> JSONResponse:
    """
    Retourne le top 100 des plats.

    :return: Le top 100 des plats
    """
    plats = await request.app.ctx.entities.plats.getTop(100)

    return JSON(
        request=request,
        success=True,
        data=[
            {
                "code": plat.get("platid"),
                "libelle": plat.get("libelle"),
                "total": plat.get("nb")
            } for plat in plats
        ],
        status=200
    ).generate()
