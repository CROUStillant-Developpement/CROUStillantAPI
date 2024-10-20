from ...models.responses import Regions, Region
from ...models.exceptions import RateLimited, BadRequest, NotFound
from sanic.response import JSONResponse, json
from sanic import Blueprint, Request
from sanic_ext import openapi


bp = Blueprint(
    name="Regions",
    url_prefix="/regions",
    version=1,
    version_prefix="v"
)


# /regions
@bp.route("/", methods=["GET"])
@openapi.definition(
    summary="Liste des régions",
    description="Liste des régions disponibles.",
    tag="Regions",
)
@openapi.response(
    status=200,
    content={
        "application/json": Regions
    },
    description="Liste des régions disponibles"
)
@openapi.response(
    status=429,
    content={
        "application/json": RateLimited
    },
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard."
)
async def getRegions(request: Request) -> JSONResponse:
    """
    Récupère les régions

    :return: Les régions
    """
    regions = await request.app.ctx.entities.regions.getAll()

    return json(
        {
            "success": True,
            "data": [
                {
                    "code": region.get("idreg"),
                    "libelle": region.get("libelle"),
                } for region in regions
            ]
        },
        status=200
    )
    

# /regions/{code}
@bp.route("/<code>", methods=["GET"])
@openapi.definition(
    summary="Détails d'une région",
    description="Détails d'une région en fonction de son code.",
    tag="Regions",
)
@openapi.response(
    status=200,
    content={
        "application/json": Region
    },
    description="Détails d'une région."
)
@openapi.response(
    status=400,
    content={
        "application/json": BadRequest
    },
    description="L'ID de la région doit être un nombre."
)
@openapi.response(
    status=404,
    content={
        "application/json": NotFound
    },
    description="La région n'existe pas."
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
    description="ID de la région",
    required=True,
    schema=int,
    location="path",
    example=1
)
async def getRegion(request: Request, code: int) -> JSONResponse:
    """
    Retourne les détails d'une région.

    :param code: ID de la région
    :return: La région
    """
    try:
        regionID = int(code)
    except ValueError:
        return json(
            {
                "success": False,
                "message": "L'ID de la région doit être un nombre."
            },
            status=400
        )

    region = await request.app.ctx.entities.regions.getOne(regionID)

    if region is None:
        return json(
            {
                "success": False,
                "message": "La région n'existe pas."
            },
            status=404
        )

    return json(
        {
            "success": True,
            "data": {
                "code": region.get("idreg"),
                "libelle": region.get("libelle"),
            }
        },
        status=200
    )
