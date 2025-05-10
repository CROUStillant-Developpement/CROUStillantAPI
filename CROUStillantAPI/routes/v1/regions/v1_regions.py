from ....components.ratelimit import ratelimit
from ....components.cache import cache
from ....components.response import JSON
from ....components.argument import Argument, inputs
from ....components.rules import Rules
from ....models.responses import Regions, Region, Restaurants
from ....models.exceptions import RateLimited, BadRequest, NotFound
from ....utils.opening import Opening
from sanic.response import JSONResponse
from sanic import Blueprint, Request
from sanic_ext import openapi
from json import loads


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
@ratelimit()
@cache()
async def getRegions(request: Request) -> JSONResponse:
    """
    Récupère les régions

    :return: Les régions
    """
    regions = await request.app.ctx.entities.regions.getAll()

    return JSON(
        request=request,
        success=True,
        data=[
            {
                "code": region.get("idreg"),
                "libelle": region.get("libelle"),
            } for region in regions
        ],
        status=200
    ).generate()
    

# /regions/{code}
@bp.route("/<code>", methods=["GET"])
@inputs(
    Argument(
        name="code",
        description="ID de la région",
        methods={
            "code": Rules.integer
        },
        call=int,
        required=True,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    )
)
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
@ratelimit()
@cache()
async def getRegion(request: Request, code: int) -> JSONResponse:
    """
    Retourne les détails d'une région.

    :param code: ID de la région
    :return: La région
    """
    region = await request.app.ctx.entities.regions.getOne(code)

    if region is None:
        return JSON(
            request=request,
            success=False,
            status=404,
            message="La région n'existe pas."
        ).generate()


    return JSON(
        request=request,
        success=True,
        data={
            "code": region.get("idreg"),
            "libelle": region.get("libelle"),
        },
        status=200
    ).generate()


# /regions/{code}/restaurants
@bp.route("/<code>/restaurants", methods=["GET"])
@inputs(
    Argument(
        name="code",
        description="ID de la région",
        methods={
            "code": Rules.integer
        },
        call=int,
        required=True,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    )
)
@openapi.definition(
    summary="Liste des restaurants d'une région",
    description="Liste des restaurants disponibles dans une région en fonction de son code.",
    tag="Regions",
)
@openapi.response(
    status=200,
    content={
        "application/json": Restaurants
    },
    description="Liste des restaurants disponibles dans une région."
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
@ratelimit()
@cache()
async def getRegionRestaurants(request: Request, code: int) -> JSONResponse:
    """
    Récupère les restaurants

    :return: Les restaurants
    """
    region = await request.app.ctx.entities.regions.getOne(code)

    if region is None:
        return JSON(
            request=request,
            success=False,
            status=404,
            message="La région n'existe pas."
        ).generate()


    restaurants = await request.app.ctx.entities.regions.getRestaurants(code)

    return JSON(
        request=request,
        success=True,
        data=[
            {
                "code": restaurant.get("rid"),
                "region": {
                    "code": restaurant.get("idreg"),
                    "libelle": restaurant.get("region")
                },
                "type": {
                    "code": restaurant.get("idtpr"),
                    "libelle": restaurant.get("type")
                },
                "nom": restaurant.get("nom"),
                "adresse": restaurant.get("adresse"),
                "latitude": restaurant.get("latitude"),
                "longitude": restaurant.get("longitude"),
                "horaires": loads(restaurant.get("horaires")) if restaurant.get("horaires", None) else None,
                "jours_ouvert": Opening(restaurant.get("jours_ouvert")).get(),
                "image_url": restaurant.get("image_url"),
                "email": restaurant.get("email"),
                "telephone": restaurant.get("telephone"),
                "ispmr": restaurant.get("ispmr"),
                "zone": restaurant.get("zone"),
                "paiement": loads(restaurant.get("paiement")) if restaurant.get("paiement", None) else None,
                "acces": loads(restaurant.get("acces")) if restaurant.get("acces", None) else None,
                "ouvert": restaurant.get("opened")
            } for restaurant in restaurants
        ],
        status=200
    ).generate()
