from ....components.ratelimit import ratelimit, Bucket
from ....components.cache import cache
from ....components.generate import generate
from ....components.response import JSON
from ....components.argument import Argument, inputs
from ....components.rules import Rules
from ....models.responses import (
    Restaurants,
    Restaurant,
    RestaurantsStatus,
    RestaurantsStatusMinimal,
    TypesRestaurants,
    RestaurantInfo,
    Menus,
    Menu,
    Dates,
    Image,
    RestaurantInsights,
    RestaurantActivity,
)
from ....models.exceptions import RateLimited, BadRequest, NotFound
from ....utils.opening import Opening
from ....utils.image import saveImageToBuffer
from ....utils.format import getBoolFromString, getIntFromString
from ....utils.colors import parse_custom_colours
from ....utils.iframes import restaurantMenuIframe, restaurantCustomIframe
from ....utils.menu import build_menu_structure
from ....exceptions.error import ServerErrorException
from sanic.response import HTTPResponse, JSONResponse, raw
from sanic import Blueprint, Request
from sanic.log import logger
from sanic_ext import openapi
from json import loads
from datetime import datetime, timedelta, date as date_cls
from pytz import timezone
from asyncio import get_event_loop, gather
from jinja2 import Environment, FileSystemLoader, select_autoescape


bp = Blueprint(
    name="Restaurants", url_prefix="/restaurants", version=1, version_prefix="v"
)

jinja_env = Environment(
    loader=FileSystemLoader("CROUStillantAPI/templates"),
    autoescape=select_autoescape(["html", "htm", "xml"]),
)


# /restaurants
@bp.route("/", methods=["GET"])
@openapi.definition(
    summary="Liste des restaurants",
    description="Liste des restaurants disponibles.",
    tag="Restaurants",
)
@openapi.response(
    status=200,
    content={"application/json": Restaurants},
    description="Liste des restaurants disponibles",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard.",
)
@openapi.parameter(
    name="actif",
    description="Renvoie uniquement les restaurants actifs",
    required=False,
    schema=bool,
    location="query",
    example=True,
)
@openapi.parameter(
    name="ouvert",
    description="Filtre les restaurants par statut d'ouverture",
    required=False,
    schema=bool,
    location="query",
    example=True,
)
@openapi.parameter(
    name="region",
    description="Filtre les restaurants par code de région",
    required=False,
    schema=int,
    location="query",
    example=17,
)
@openapi.parameter(
    name="type",
    description="Filtre les restaurants par code de type",
    required=False,
    schema=int,
    location="query",
    example=1,
)
@openapi.parameter(
    name="ispmr",
    description="Filtre les restaurants accessibles aux PMR",
    required=False,
    schema=bool,
    location="query",
    example=True,
)
@openapi.parameter(
    name="zone",
    description="Filtre les restaurants par zone (insensible à la casse)",
    required=False,
    schema=str,
    location="query",
    example="Pau",
)
@ratelimit()
@cache(ttl=300)
async def getRestaurants(request: Request) -> JSONResponse:
    """
    Récupère les restaurants

    :return: Les restaurants
    """
    ouvert_param = request.args.get("ouvert", None)
    ispmr_param = request.args.get("ispmr", None)
    region_param = request.args.get("region", None)
    type_param = request.args.get("type", None)
    zone_param = request.args.get("zone", None)

    restaurants = await request.app.ctx.entities.restaurants.getAll(
        actif=getBoolFromString(request.args.get("actif", True)),
        ouvert=getBoolFromString(ouvert_param) if ouvert_param is not None else None,
        ispmr=getBoolFromString(ispmr_param) if ispmr_param is not None else None,
        region=getIntFromString(region_param) if region_param is not None else None,
        type_=getIntFromString(type_param) if type_param is not None else None,
        zone=zone_param,
    )

    return JSON(
        request=request,
        success=True,
        data=[
            {
                "code": restaurant.get("rid"),
                "region": {
                    "code": restaurant.get("idreg"),
                    "libelle": restaurant.get("region"),
                },
                "type": {
                    "code": restaurant.get("idtpr"),
                    "libelle": restaurant.get("type"),
                },
                "nom": restaurant.get("nom"),
                "adresse": restaurant.get("adresse"),
                "latitude": restaurant.get("latitude"),
                "longitude": restaurant.get("longitude"),
                "horaires": loads(restaurant.get("horaires"))
                if restaurant.get("horaires", None)
                else None,
                "jours_ouvert": Opening(restaurant.get("jours_ouvert")).get(),
                "image_url": restaurant.get("image_url"),
                "email": restaurant.get("email"),
                "telephone": restaurant.get("telephone"),
                "ispmr": restaurant.get("ispmr"),
                "zone": restaurant.get("zone"),
                "paiement": loads(restaurant.get("paiement"))
                if restaurant.get("paiement", None)
                else None,
                "acces": loads(restaurant.get("acces"))
                if restaurant.get("acces", None)
                else None,
                "ouvert": restaurant.get("opened"),
                "actif": restaurant.get("actif"),
            }
            for restaurant in restaurants
        ],
        status=200,
    ).generate()


# /restaurants/status
@bp.route("/status", methods=["GET"])
@openapi.definition(
    summary="Statut d'ouverture des restaurants",
    description="Liste des restaurants actifs avec leur statut d'ouverture.",
    tag="Restaurants",
)
@openapi.response(
    status=200,
    content={"application/json": RestaurantsStatus},
    description="Liste des statuts des restaurants.",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard.",
)
@openapi.parameter(
    name="ouvert",
    description="Filtre les restaurants par statut d'ouverture",
    required=False,
    schema=bool,
    location="query",
    example=True,
)
@ratelimit()
@cache(ttl=300)
async def getRestaurantsStatus(request: Request) -> JSONResponse:
    ouvert_param = request.args.get("ouvert", None)
    restaurants = await request.app.ctx.entities.restaurants.getStatus(
        ouvert=getBoolFromString(ouvert_param) if ouvert_param is not None else None,
    )

    return JSON(
        request=request,
        success=True,
        data=[
            {
                "code": restaurant.get("rid"),
                "nom": restaurant.get("nom"),
                "region": {
                    "code": restaurant.get("idreg"),
                    "libelle": restaurant.get("region"),
                },
                "type": {
                    "code": restaurant.get("idtpr"),
                    "libelle": restaurant.get("type"),
                },
                "ouvert": restaurant.get("opened"),
                "actif": restaurant.get("actif"),
            }
            for restaurant in restaurants
        ],
        status=200,
    ).generate()


# /restaurants/status/minimal
@bp.route("/status/minimal", methods=["GET"])
@openapi.definition(
    summary="Statut d'ouverture minimal des restaurants",
    description="Liste des restaurants actifs avec leur statut d'ouverture (champs minimaux : code, actif, ouvert).",
    tag="Restaurants",
)
@openapi.response(
    status=200,
    content={"application/json": RestaurantsStatusMinimal},
    description="Liste des statuts minimaux des restaurants.",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard.",
)
@openapi.parameter(
    name="ouvert",
    description="Filtre les restaurants par statut d'ouverture",
    required=False,
    schema=bool,
    location="query",
    example=True,
)
@ratelimit()
@cache(ttl=300)
async def getRestaurantsStatusMinimal(request: Request) -> JSONResponse:
    ouvert_param = request.args.get("ouvert", None)
    restaurants = await request.app.ctx.entities.restaurants.getStatus(
        ouvert=getBoolFromString(ouvert_param) if ouvert_param is not None else None,
    )

    return JSON(
        request=request,
        success=True,
        data=[
            {
                "code": restaurant.get("rid"),
                "actif": restaurant.get("actif"),
                "ouvert": restaurant.get("opened"),
            }
            for restaurant in restaurants
        ],
        status=200,
    ).generate()


# /restaurants/{code}
@bp.route("/<code>", methods=["GET"])
@openapi.definition(
    summary="Détails d'un restaurant",
    description="Détails d'un restaurant en fonction de son code.",
    tag="Restaurants",
)
@openapi.response(
    status=200,
    content={"application/json": Restaurant},
    description="Détails d'un restaurant.",
)
@openapi.response(
    status=400,
    content={"application/json": BadRequest},
    description="L'ID du restaurant doit être un nombre.",
)
@openapi.response(
    status=404,
    content={"application/json": NotFound},
    description="Le restaurant n'existe pas.",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard.",
)
@openapi.parameter(
    name="code",
    description="ID du restaurant",
    required=True,
    schema=int,
    location="path",
    example=1,
)
@inputs(
    Argument(
        name="code",
        description="ID du restaurant",
        methods={"code": Rules.integer},
        call=int,
        required=True,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    )
)
@ratelimit()
@cache(ttl=300)
async def getRestaurant(request: Request, code: int) -> JSONResponse:
    """
    Retourne les détails d'un restaurant.

    :param code: ID du restaurant
    :return: Le restaurant
    """
    restaurant = await request.app.ctx.entities.restaurants.getOne(code)

    if restaurant is None:
        return JSON(
            request=request,
            success=False,
            message="Le restaurant n'existe pas.",
            status=404,
        ).generate()

    return JSON(
        request=request,
        success=True,
        data={
            "code": restaurant.get("rid"),
            "region": {
                "code": restaurant.get("idreg"),
                "libelle": restaurant.get("region"),
            },
            "type": {
                "code": restaurant.get("idtpr"),
                "libelle": restaurant.get("type"),
            },
            "nom": restaurant.get("nom"),
            "adresse": restaurant.get("adresse"),
            "latitude": restaurant.get("latitude"),
            "longitude": restaurant.get("longitude"),
            "horaires": loads(restaurant.get("horaires"))
            if restaurant.get("horaires", None)
            else None,
            "jours_ouvert": Opening(restaurant.get("jours_ouvert")).get(),
            "image_url": restaurant.get("image_url"),
            "email": restaurant.get("email"),
            "telephone": restaurant.get("telephone"),
            "ispmr": restaurant.get("ispmr"),
            "zone": restaurant.get("zone"),
            "paiement": loads(restaurant.get("paiement"))
            if restaurant.get("paiement", None)
            else None,
            "acces": loads(restaurant.get("acces"))
            if restaurant.get("acces", None)
            else None,
            "ouvert": restaurant.get("opened"),
            "actif": restaurant.get("actif"),
        },
        status=200,
    ).generate()


# /restaurants/{code}/iframe
@bp.route("/<code>/iframe", methods=["GET"])
@openapi.definition(
    summary="Widget Iframe Informations d'un restaurant",
    description="Retourne un widget HTML intégrable affichant les informations d'un restaurant.",
    tag="Restaurants",
)
@openapi.response(
    status=200,
    content={"text/html": str},
    description="Widget Iframe HTML",
)
@openapi.response(
    status=400,
    content={"application/json": BadRequest},
    description="L'ID du restaurant doit être un nombre.",
)
@openapi.response(
    status=404,
    content={"application/json": NotFound},
    description="Le restaurant n'existe pas.",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard.",
)
@openapi.parameter(
    name="code",
    description="ID du restaurant",
    required=True,
    schema=int,
    location="path",
    example=1,
)
@openapi.parameter(
    name="theme",
    description="Thème du widget (light, dark)",
    required=False,
    schema=str,
    location="query",
    example="light",
)
@inputs(
    Argument(
        name="code",
        description="ID du restaurant",
        methods={"code": Rules.integer},
        call=int,
        required=True,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    )
)
@ratelimit()
@cache(ttl=60 * 5)
async def getRestaurantIframe(request: Request, code: int) -> HTTPResponse:
    """
    Retourne un widget Iframe d'informations d'un restaurant.

    :param code: ID du restaurant
    :return: Le widget Iframe HTML
    """
    restaurant = await request.app.ctx.entities.restaurants.getOne(code)

    if not restaurant:
        return JSON(
            request=request,
            success=False,
            message="Le restaurant n'existe pas.",
            status=404,
        ).generate()

    preview = await request.app.ctx.entities.restaurants.getPreview(code)

    parsed_restaurant = dict(restaurant)
    if parsed_restaurant.get("horaires"):
        try:
            parsed_restaurant["horaires"] = loads(parsed_restaurant.get("horaires"))
        except Exception:
            parsed_restaurant["horaires"] = None
    if parsed_restaurant.get("paiement"):
        try:
            parsed_restaurant["paiement"] = loads(parsed_restaurant.get("paiement"))
        except Exception:
            parsed_restaurant["paiement"] = None
    if parsed_restaurant.get("acces"):
        try:
            parsed_restaurant["acces"] = loads(parsed_restaurant.get("acces"))
        except Exception:
            parsed_restaurant["acces"] = None

    template = jinja_env.get_template("iframe_info.html")
    html_content = template.render(
        request=request, restaurant=parsed_restaurant, preview=preview is not None
    )

    return raw(body=html_content, content_type="text/html; charset=utf-8", status=200)


# /restaurants/{code}/iframe/custom
@bp.route("/<code>/iframe/custom", methods=["GET"])
@openapi.definition(
    summary="Widget Iframe personnalisé d'un restaurant",
    description="Retourne un widget HTML intégrable entièrement personnalisable via la query string (blocs, thème, couleur, police, repas, date, taille).",
    tag="Restaurants",
)
@openapi.response(
    status=200,
    content={"text/html": str},
    description="Widget Iframe HTML personnalisé",
)
@openapi.response(
    status=400,
    content={"application/json": BadRequest},
    description="Paramètre invalide : ID non entier, thème inconnu, couleur mal formée, police non supportée, langue non supportée, bloc ou repas invalide, hauteur hors plage, date mal formatée.",
)
@openapi.response(
    status=404,
    content={"application/json": NotFound},
    description="Le restaurant n'existe pas.",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard.",
)
@openapi.parameter(
    name="code",
    description="ID du restaurant",
    required=True,
    schema=int,
    location="path",
    example=1,
)
@openapi.parameter(
    name="theme",
    description="Thème (light, dark)",
    required=False,
    schema=str,
    location="query",
    example="light",
)
@openapi.parameter(
    name="date",
    description="Date du menu (DD-MM-YYYY, défaut : aujourd'hui)",
    required=False,
    schema=str,
    location="query",
    example="15-05-2026",
)
@openapi.parameter(
    name="blocks",
    description="Blocs à afficher, dans l'ordre souhaité (header,header_text,region,status,address,menu,hours,contact,payment,access,link)",
    required=False,
    schema=str,
    location="query",
    example="header,header_text,status,menu,hours",
)
@openapi.parameter(
    name="meals",
    description="Repas à afficher dans le bloc menu (matin,midi,soir)",
    required=False,
    schema=str,
    location="query",
    example="midi,soir",
)
@openapi.parameter(
    name="color",
    description="Couleur d'accent hexadécimale sans # (ex: ef4444)",
    required=False,
    schema=str,
    location="query",
    example="ef4444",
)
@openapi.parameter(
    name="font",
    description="Police (Inter, Roboto, Outfit, Nunito, system)",
    required=False,
    schema=str,
    location="query",
    example="Inter",
)
@openapi.parameter(
    name="height",
    description="Hauteur fixe du widget en px (200-1200, défaut: 600)",
    required=False,
    schema=int,
    location="query",
    example=600,
)
@openapi.parameter(
    name="lang",
    description="Langue (fr, en)",
    required=False,
    schema=str,
    location="query",
    example="fr",
)
@inputs(
    Argument(
        name="code",
        description="ID du restaurant",
        methods={"code": Rules.integer},
        call=int,
        required=True,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    )
)
@inputs(
    Argument(
        name="theme",
        description="Thème du widget (light ou dark)",
        methods={"theme": Rules.iframe_theme},
        call=str,
        required=False,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    )
)
@inputs(
    Argument(
        name="date",
        description="Date du menu (format DD-MM-YYYY)",
        methods={"date": Rules.date},
        call=str,
        required=False,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    )
)
@inputs(
    Argument(
        name="blocks",
        description="Blocs à afficher séparés par des virgules",
        methods={"blocks": Rules.iframe_blocks},
        call=str,
        required=False,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    )
)
@inputs(
    Argument(
        name="meals",
        description="Repas à afficher séparés par des virgules",
        methods={"meals": Rules.iframe_meals},
        call=str,
        required=False,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    )
)
@inputs(
    Argument(
        name="color",
        description="Couleur d'accent hexadécimale sans # (6 caractères)",
        methods={"color": Rules.hex_color},
        call=str,
        required=False,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    )
)
@inputs(
    Argument(
        name="font",
        description="Police de caractères du widget",
        methods={"font": Rules.iframe_font},
        call=str,
        required=False,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    )
)
@inputs(
    Argument(
        name="height",
        description="Hauteur du widget en pixels (200-1200)",
        methods={"height": Rules.iframe_height},
        call=int,
        required=False,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    )
)
@inputs(
    Argument(
        name="lang",
        description="Langue du widget (fr ou en)",
        methods={"lang": Rules.iframe_lang},
        call=str,
        required=False,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    )
)
@ratelimit()
@cache(ttl=60)
async def getRestaurantCustomIframe(
    request: Request,
    code: int,
    theme: str | None = None,
    date: str | None = None,
    blocks: str | None = None,
    meals: str | None = None,
    color: str | None = None,
    font: str | None = None,
    height: int | None = None,
    lang: str | None = None,
) -> HTTPResponse:
    """
    Retourne un widget Iframe personnalisé d'un restaurant.

    :param code: ID du restaurant
    :return: Le widget Iframe HTML personnalisé
    """
    return await restaurantCustomIframe(
        request, code, jinja_env,
        theme=theme,
        date=date,
        blocks=blocks,
        meals=meals,
        color=color,
        font=font,
        height=height,
        lang=lang,
    )


# /restaurants/{code}/menu
@bp.route("/<code>/menu", methods=["GET"])
@openapi.definition(
    summary="Menu d'un restaurant",
    description="Menu d'un restaurant en fonction de son code.",
    tag="Restaurants",
)
@openapi.response(
    status=200, content={"application/json": Menus}, description="Menu d'un restaurant."
)
@openapi.response(
    status=400,
    content={"application/json": BadRequest},
    description="L'ID du restaurant doit être un nombre.",
)
@openapi.response(
    status=404,
    content={"application/json": NotFound},
    description="Le restaurant n'existe pas.",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard.",
)
@openapi.parameter(
    name="code",
    description="ID du restaurant",
    required=True,
    schema=int,
    location="path",
    example=1,
)
@inputs(
    Argument(
        name="code",
        description="ID du restaurant",
        methods={"code": Rules.integer},
        call=int,
        required=True,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    )
)
@ratelimit()
@cache(ttl=300)
async def getRestaurantMenu(request: Request, code: int) -> JSONResponse:
    """
    Retourne le menu d'un restaurant.

    :param code: ID du restaurant
    :return: Le menu du restaurant
    """
    menu = await request.app.ctx.entities.menus.getCurrent(
        id=code, date=datetime.now(tz=timezone("Europe/Paris"))
    )

    if menu is None or len(menu) == 0:
        return JSON(
            request=request,
            success=False,
            message="Aucun menu n'est disponible pour ce restaurant.",
            status=404,
        ).generate()

    menu_per_day = build_menu_structure(menu)
    return JSON(
        request=request, success=True, data=list(menu_per_day.values()), status=200
    ).generate()


# /restaurants/{code}/menu/iframe
@bp.route("/<code>/menu/iframe", methods=["GET"])
@openapi.definition(
    summary="Widget Iframe Menu d'un restaurant (Aujourd'hui)",
    description="Retourne un widget HTML intégrable affichant le menu d'un restaurant pour la date d'aujourd'hui.",
    tag="Restaurants",
)
@openapi.response(
    status=200,
    content={"text/html": str},
    description="Widget Iframe HTML",
)
@openapi.response(
    status=400,
    content={"application/json": BadRequest},
    description="L'ID du restaurant doit être un nombre.",
)
@openapi.response(
    status=404,
    content={"application/json": NotFound},
    description="Le restaurant n'existe pas.",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard.",
)
@openapi.parameter(
    name="code",
    description="ID du restaurant",
    required=True,
    schema=int,
    location="path",
    example=1,
)
@openapi.parameter(
    name="theme",
    description="Thème du widget (light, dark)",
    required=False,
    schema=str,
    location="query",
    example="light",
)
@inputs(
    Argument(
        name="code",
        description="ID du restaurant",
        methods={"code": Rules.integer},
        call=int,
        required=True,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    )
)
@ratelimit()
@cache(ttl=60 * 5)
async def getRestaurantTodayMenuIframe(request: Request, code: int) -> HTTPResponse:
    """
    Retourne un widget Iframe du menu d'un restaurant pour aujourd'hui.

    :param code: ID du restaurant
    :return: Le widget Iframe HTML
    """
    today = datetime.now(tz=timezone("Europe/Paris"))
    return await restaurantMenuIframe(request, code, today, jinja_env)


# /restaurants/{code}/menu/dates
@bp.route("/<code>/menu/dates", methods=["GET"])
@openapi.definition(
    summary="Dates des prochains menus disponibles d'un restaurant",
    description="Dates des prochains menus disponibles d'un restaurant en fonction de son code.",
    tag="Restaurants",
)
@openapi.response(
    status=200,
    content={"application/json": Dates},
    description="Dates des prochains menus disponibles",
)
@openapi.response(
    status=400,
    content={"application/json": BadRequest},
    description="L'ID du restaurant doit être un nombre.",
)
@openapi.response(
    status=404,
    content={"application/json": NotFound},
    description="Le restaurant n'existe pas.",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard.",
)
@openapi.parameter(
    name="code",
    description="ID du restaurant",
    required=True,
    schema=int,
    location="path",
    example=1,
)
@inputs(
    Argument(
        name="code",
        description="ID du restaurant",
        methods={"code": Rules.integer},
        call=int,
        required=True,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    )
)
@ratelimit()
@cache(ttl=300)
async def getRestaurantMenuDates(request: Request, code: int) -> JSONResponse:
    """
    Retourne les dates des prochains menus disponibles

    :param code: ID du restaurant
    :return: Le menu du restaurant
    """
    dates = await request.app.ctx.entities.menus.getDates(id=code)

    if dates is None or len(dates) == 0:
        return JSON(
            request=request,
            success=False,
            message="Aucun menu n'a été trouvé.",
            status=404,
        ).generate()

    return JSON(
        request=request,
        success=True,
        data=[
            {"code": row.get("mid"), "date": row.get("date").strftime("%d-%m-%Y")}
            for row in dates
        ],
        status=200,
    ).generate()


# /restaurants/{code}/menu/dates/all
@bp.route("/<code>/menu/dates/all", methods=["GET"])
@openapi.definition(
    summary="Dates des menus disponibles d'un restaurant",
    description="Dates des menus disponibles d'un restaurant en fonction de son code.",
    tag="Restaurants",
)
@openapi.response(
    status=200,
    content={"application/json": Dates},
    description="Dates des menus disponibles",
)
@openapi.response(
    status=400,
    content={"application/json": BadRequest},
    description="L'ID du restaurant doit être un nombre.",
)
@openapi.response(
    status=404,
    content={"application/json": NotFound},
    description="Le restaurant n'existe pas.",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard.",
)
@openapi.parameter(
    name="code",
    description="ID du restaurant",
    required=True,
    schema=int,
    location="path",
    example=1,
)
@inputs(
    Argument(
        name="code",
        description="ID du restaurant",
        methods={"code": Rules.integer},
        call=int,
        required=True,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    )
)
@ratelimit()
@cache(ttl=300)
async def getRestaurantMenuAllDates(request: Request, code: int) -> JSONResponse:
    """
    Retourne les dates des menus disponibles

    :param code: ID du restaurant
    :return: Le menu du restaurant
    """
    dates = await request.app.ctx.entities.menus.getAllDates(id=code)

    if dates is None or len(dates) == 0:
        return JSON(
            request=request,
            success=False,
            message="Aucun menu n'a été trouvé.",
            status=404,
        ).generate()

    return JSON(
        request=request,
        success=True,
        data=[
            {"code": row.get("mid"), "date": row.get("date").strftime("%d-%m-%Y")}
            for row in dates
        ],
        status=200,
    ).generate()


# /restaurants/{code}/menu/{date}
@bp.route("/<code>/menu/<date>", methods=["GET"])
@openapi.definition(
    summary="Menu d'un restaurant à une date donnée",
    description="Menu d'un restaurant en fonction de son code et d'une date donnée.",
    tag="Restaurants",
)
@openapi.response(
    status=200, content={"application/json": Menu}, description="Menu d'un restaurant."
)
@openapi.response(
    status=400,
    content={"application/json": BadRequest},
    description="L'ID du restaurant doit être un nombre et la date doit être au format DD-MM-YYYY.",
)
@openapi.response(
    status=404,
    content={"application/json": NotFound},
    description="Le restaurant n'existe pas.",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard.",
)
@openapi.parameter(
    name="code",
    description="ID du restaurant",
    required=True,
    schema=int,
    location="path",
    example=1,
)
@openapi.parameter(
    name="date",
    description="Date du menu (format: DD-MM-YYYY)",
    required=True,
    schema=str,
    location="path",
    example="21-10-2024",
)
@inputs(
    Argument(
        name="code",
        description="ID du restaurant",
        methods={"code": Rules.integer},
        call=int,
        required=True,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    )
)
@inputs(
    Argument(
        name="date",
        description="Date du menu",
        methods={"date": Rules.date},
        call=lambda x: datetime.strptime(x, "%d-%m-%Y"),
        required=True,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    )
)
@ratelimit()
@cache(ttl=300)
async def getRestaurantMenuFromDate(
    request: Request, code: int, date: datetime
) -> JSONResponse:
    """
    Retourne le menu d'un restaurant.

    :param code: ID du restaurant
    :param date: Date du menu
    :return: Le menu du restaurant
    """
    menu = await request.app.ctx.entities.menus.getFromDate(id=code, date=date)

    if menu is None or len(menu) == 0:
        return JSON(
            request=request,
            success=False,
            message="Aucun menu n'a été trouvé pour cette date.",
            status=404,
        ).generate()

    menu_per_day = build_menu_structure(menu)
    date_key = date.strftime("%d-%m-%Y")
    return JSON(
        request=request, success=True, data=menu_per_day[date_key], status=200
    ).generate()


# /restaurants/{code}/menu/{date}/iframe
@bp.route("/<code>/menu/<date>/iframe", methods=["GET"])
@openapi.definition(
    summary="Widget Iframe Menu d'un restaurant",
    description="Retourne un widget HTML intégrable affichant le menu d'un restaurant pour une date précise.",
    tag="Restaurants",
)
@openapi.response(
    status=200,
    content={"text/html": str},
    description="Widget Iframe HTML",
)
@openapi.response(
    status=400,
    content={"application/json": BadRequest},
    description="L'ID du restaurant doit être un nombre et la date au format DD-MM-YYYY.",
)
@openapi.response(
    status=404,
    content={"application/json": NotFound},
    description="Le restaurant n'existe pas.",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard.",
)
@openapi.parameter(
    name="code",
    description="ID du restaurant",
    required=True,
    schema=int,
    location="path",
    example=1,
)
@openapi.parameter(
    name="date",
    description="Date du menu",
    required=True,
    schema=str,
    location="path",
    example="10-10-2026",
)
@openapi.parameter(
    name="theme",
    description="Thème du widget (light, dark)",
    required=False,
    schema=str,
    location="query",
    example="light",
)
@inputs(
    Argument(
        name="code",
        description="ID du restaurant",
        methods={"code": Rules.integer},
        call=int,
        required=True,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    )
)
@inputs(
    Argument(
        name="date",
        description="Date du menu",
        methods={"date": Rules.date},
        call=lambda x: datetime.strptime(x, "%d-%m-%Y"),
        required=True,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    )
)
@ratelimit()
@cache(ttl=60 * 5)
async def getRestaurantMenuIframe(
    request: Request, code: int, date: datetime
) -> HTTPResponse:
    """
    Retourne un widget Iframe du menu d'un restaurant.

    :param code: ID du restaurant
    :param date: Date du menu
    :return: Le widget Iframe HTML
    """
    return await restaurantMenuIframe(request, code, date, jinja_env)


# /restaurants/{code}/menu/{date}/image
@bp.route("/<code>/menu/<date>/image", methods=["GET"])
@openapi.definition(
    summary="Menu d'un restaurant à une date donnée sous forme d'image",
    description="Menu d'un restaurant en fonction de son code et d'une date donnée sous forme d'image.",
    tag="Restaurants",
)
@openapi.response(
    status=200,
    content={"image/png": Image},
    description="Menu d'un restaurant sous forme d'image.",
)
@openapi.response(
    status=400,
    content={"application/json": BadRequest},
    description="L'ID du restaurant doit être un nombre et la date doit être au format DD-MM-YYYY.",
)
@openapi.response(
    status=404,
    content={"application/json": NotFound},
    description="Le restaurant n'existe pas.",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard.",
)
@openapi.parameter(
    name="code",
    description="ID du restaurant",
    required=True,
    schema=int,
    location="path",
    example=1,
)
@openapi.parameter(
    name="date",
    description="Date du menu (format: DD-MM-YYYY)",
    required=True,
    schema=str,
    location="path",
    example="21-10-2024",
)
@openapi.parameter(
    name="repas",
    description="Repas du menu",
    required=False,
    schema=str,
    location="query",
    example="midi",
)
@openapi.parameter(
    name="theme",
    description="Thème de l'image (light, purple, dark)",
    required=False,
    schema=str,
    location="query",
    example="light",
)
@openapi.parameter(
    name="color_header",
    description="Couleur personnalisée pour l'en-tête (format: #RRGGBB ou #RGB)",
    required=False,
    schema=str,
    location="query",
    example="#000000",
)
@openapi.parameter(
    name="color_content",
    description="Couleur personnalisée pour le contenu (format: #RRGGBB ou #RGB)",
    required=False,
    schema=str,
    location="query",
    example="#373737",
)
@openapi.parameter(
    name="color_title",
    description="Couleur personnalisée pour les titres (format: #RRGGBB ou #RGB)",
    required=False,
    schema=str,
    location="query",
    example="#333333",
)
@openapi.parameter(
    name="color_infos",
    description="Couleur personnalisée pour les informations (format: #RRGGBB ou #RGB)",
    required=False,
    schema=str,
    location="query",
    example="#4F4F4F",
)
@inputs(
    Argument(
        name="code",
        description="ID du restaurant",
        methods={"code": Rules.integer},
        call=int,
        required=True,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    )
)
@inputs(
    Argument(
        name="date",
        description="Date du menu",
        methods={"date": Rules.date},
        call=lambda x: datetime.strptime(x, "%d-%m-%Y"),
        required=True,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    )
)
@ratelimit()
@cache(
    ttl=60 * 5  # 5 minutes
)
async def getRestaurantMenuFromDateImage(
    request: Request, code: int, date: datetime
) -> HTTPResponse:
    """
    Retourne le menu d'un restaurant.

    :param code: ID du restaurant
    :param date: Date du menu
    :return: Le menu du restaurant
    """
    repas = (
        request.args.get("repas", "midi").lower()
        if request.args.get("repas", "midi").lower() in ["matin", "midi", "soir"]
        else "midi"
    )
    theme = (
        request.args.get("theme", "light").lower()
        if request.args.get("theme", "light").lower() in ["light", "purple", "dark"]
        else "light"
    )

    # Parse custom colours from query parameters
    custom_colours = parse_custom_colours(request.args)

    restaurant = await request.app.ctx.entities.restaurants.getOne(code)

    if not restaurant:
        return JSON(
            request=request,
            success=False,
            message="Le restaurant n'existe pas.",
            status=404,
        ).generate()

    preview = await request.app.ctx.entities.restaurants.getPreview(code)

    try:
        menu = await request.app.ctx.entities.menus.getFromDate(id=code, date=date)

        if menu:
            menu_per_day = {}
            for row in menu:
                d = row.get("date").strftime("%d-%m-%Y")

                day_menu = menu_per_day.setdefault(
                    d, {"code": row.get("mid"), "date": d, "repas": []}
                )

                repas_list = day_menu["repas"]

                if not repas_list or row.get("tpr") not in repas_list[-1]["type"]:
                    repas_list.append(
                        {
                            "code": row.get("rpid"),
                            "type": row.get("tpr"),
                            "categories": [],
                        }
                    )

                r = repas_list[-1]
                categories_list = r["categories"]

                if (
                    not categories_list
                    or row.get("tpcat") not in categories_list[-1]["libelle"]
                ):
                    categories_list.append(
                        {
                            "code": row.get("catid"),
                            "libelle": row.get("tpcat"),
                            "ordre": row.get("cat_ordre") + 1,
                            "plats": [],
                        }
                    )

                if row.get("platid") is not None:
                    categories_list[-1]["plats"].append(
                        {
                            "code": row.get("platid"),
                            "ordre": row.get("plat_ordre") + 1,
                            "libelle": row.get("plat"),
                        }
                    )

            data = None
            for menu in menu_per_day:
                if date.strftime("%d-%m-%Y") == menu:
                    for m in menu_per_day[menu]["repas"]:
                        if m["type"] == repas:
                            data = m
                            break
                    break
        else:
            data = None

        def generate_image_in_background(
            restaurant, menu, date, preview, theme, custom_colours
        ):
            image = generate(
                restaurant=restaurant,
                menu=menu,
                date=date,
                preview=preview,
                theme=theme,
                custom_colours=custom_colours,
            )
            buffer = saveImageToBuffer(image, compression_level=1)
            return buffer.getvalue()

        if preview:
            preview = preview.get("raw_image", None)
        else:
            preview = None

        loop = get_event_loop()
        content = await loop.run_in_executor(
            request.app.ctx.executor,
            generate_image_in_background,
            restaurant,
            data,
            date,
            preview,
            theme,
            custom_colours,
        )

        return raw(
            body=content,
            status=200,
            headers={
                "Content-Disposition": f"attachment; filename={restaurant.get('nom')} - {date.strftime('%d-%m-%Y')}.png",
                "Content-Length": str(len(content)),
                "Content-Type": "image/png",
            },
            content_type="image/png",
        )
    except Exception as e:
        logger.error(
            f"/restaurants/{code}/menu/{date.strftime('%d-%m-%Y')}/image?repas={repas}&theme={theme}",
            e,
        )

        raise ServerErrorException(
            headers={"Retry-After": 60},
            extra={
                "message": f"Une erreur est survenue lors de la génération de l'image (/restaurants/{code}/menu/{date.strftime('%d-%m-%Y')}/image?repas={repas}?theme={theme})"
            },
        )


# /restaurants/{code}/insights
@bp.route("/<code>/insights", methods=["GET"])
@openapi.definition(
    summary="Insights d'un restaurant",
    description="Statistiques d'un restaurant sur l'année scolaire en cours : couverture des menus (jours avec/sans menu) et plats les plus fréquents.",
    tag="Restaurants",
)
@openapi.response(
    status=200,
    content={"application/json": RestaurantInsights},
    description="Insights d'un restaurant.",
)
@openapi.response(
    status=400,
    content={"application/json": BadRequest},
    description="L'ID du restaurant doit être un nombre.",
)
@openapi.response(
    status=404,
    content={"application/json": NotFound},
    description="Le restaurant n'existe pas.",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard.",
)
@openapi.parameter(
    name="code",
    description="ID du restaurant",
    required=True,
    schema=int,
    location="path",
    example=1,
)
@openapi.parameter(
    name="limit",
    description="Nombre de plats les plus fréquents à retourner (1-50, défaut 10)",
    required=False,
    schema=int,
    location="query",
    example=10,
)
@inputs(
    Argument(
        name="code",
        description="ID du restaurant",
        methods={"code": Rules.integer},
        call=int,
        required=True,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    )
)
@ratelimit()
@cache(ttl=60 * 30)  # 30 minutes
async def getRestaurantInsights(request: Request, code: int) -> JSONResponse:
    """
    Retourne les insights d'un restaurant (couverture des menus, plats fréquents).

    :param code: ID du restaurant
    :return: Les insights du restaurant
    """
    restaurant = await request.app.ctx.entities.restaurants.getOne(code)

    if not restaurant:
        return JSON(
            request=request,
            success=False,
            message="Le restaurant n'existe pas.",
            status=404,
        ).generate()

    limit_raw = request.args.get("limit", "10")
    limit = int(limit_raw) if Rules.integer(limit_raw) else 10
    limit = max(1, min(limit, 50))

    today = datetime.now(tz=timezone("Europe/Paris")).date()
    school_year_start = date_cls(today.year if today.month >= 9 else today.year - 1, 9, 1)
    date_to = today - timedelta(days=1)

    first_menu = await request.app.ctx.entities.menus.getFirstDate(code)
    first_date = first_menu.get("date") if first_menu else None
    date_from = max(school_year_start, first_date) if first_date else school_year_start

    if date_from > date_to:
        return JSON(
            request=request,
            success=True,
            data={
                "periode": {
                    "debut": date_from.strftime("%d-%m-%Y"),
                    "fin": date_to.strftime("%d-%m-%Y"),
                },
                "couverture": {
                    "jours_ouvres": 0,
                    "jours_avec_menu": 0,
                    "jours_sans_menu": 0,
                    "taux_couverture": 0.0,
                },
                "repartition_repas": {"matin": 0, "midi": 0, "soir": 0},
                "plats_frequents": [],
                "couverture_par_jour": [],
                "series": {
                    "meilleure_serie_avec_menu": 0,
                    "plus_longue_serie_sans_menu": 0,
                    "serie_actuelle": {"avec_menu": False, "jours": 0},
                },
                "variete": {
                    "plats_uniques": 0,
                    "plats_total": 0,
                    "taux_variete": 0.0,
                },
                "richesse": {
                    "moyenne_categories_par_repas": 0.0,
                    "moyenne_plats_par_repas": 0.0,
                },
                "delai_publication": {"moyenne_jours": None},
                "comparaison_regionale": {
                    "jours_avec_menu_restaurant": 0,
                    "moyenne_jours_avec_menu_region": None,
                    "nb_restaurants_compares": 0,
                },
            },
            status=200,
        ).generate()

    menu_dates_rows = await request.app.ctx.entities.menus.getDatesInRange(
        code, date_from, date_to
    )
    menu_dates = {row.get("date") for row in menu_dates_rows}

    opening = Opening(restaurant.get("jours_ouvert")).get()
    open_weekdays = {
        i for i, jour in enumerate(opening) if any(jour["ouverture"].values())
    }

    jours_semaine = [
        "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche",
    ]
    par_jour = {i: {"jours_ouvres": 0, "jours_avec_menu": 0} for i in open_weekdays}

    jours_ouvres = 0
    jours_avec_menu = 0

    meilleure_serie_avec_menu = 0
    plus_longue_serie_sans_menu = 0
    courante_avec = 0
    courante_sans = 0
    serie_actuelle_avec_menu = False
    longueur_serie_actuelle = 0

    current = date_from
    while current <= date_to:
        weekday = current.weekday()
        if weekday in open_weekdays:
            jours_ouvres += 1
            a_menu = current in menu_dates
            par_jour[weekday]["jours_ouvres"] += 1

            if a_menu:
                jours_avec_menu += 1
                par_jour[weekday]["jours_avec_menu"] += 1

                courante_avec += 1
                courante_sans = 0
                meilleure_serie_avec_menu = max(meilleure_serie_avec_menu, courante_avec)
                serie_actuelle_avec_menu = True
                longueur_serie_actuelle = courante_avec
            else:
                courante_sans += 1
                courante_avec = 0
                plus_longue_serie_sans_menu = max(plus_longue_serie_sans_menu, courante_sans)
                serie_actuelle_avec_menu = False
                longueur_serie_actuelle = courante_sans

        current += timedelta(days=1)

    jours_sans_menu = jours_ouvres - jours_avec_menu
    taux_couverture = (
        round(jours_avec_menu / jours_ouvres * 100, 1) if jours_ouvres else 0.0
    )

    couverture_par_jour = []
    for i, nom in enumerate(jours_semaine):
        if i not in par_jour:
            continue
        jo = par_jour[i]["jours_ouvres"]
        jam = par_jour[i]["jours_avec_menu"]
        couverture_par_jour.append(
            {
                "jour": nom,
                "jours_ouvres": jo,
                "jours_avec_menu": jam,
                "taux_couverture": round(jam / jo * 100, 1) if jo else 0.0,
            }
        )

    # Richesse, variété et plats fréquents viennent de `restaurant_insights_summary`,
    # une vue matérialisée rafraîchie à chaque cycle d'ingestion (voir CROUStillant/__main__.py).
    # Ces agrégats traversent PLAT->COMPOSITION->CATEGORIE->REPAS->MENU, des tables partitionnées
    # par HASH sur leur propre clé (pas alignée avec les jointures) : calculés en direct sur toute
    # une année scolaire, ils prennent plusieurs secondes par restaurant. Précalculés une seule
    # fois pour tous les restaurants, la lecture ici est un simple lookup indexé par RID.
    (
        repas_rows,
        summary,
        lag_row,
        region_row,
    ) = await gather(
        request.app.ctx.entities.menus.getRepasBreakdown(code, date_from, date_to),
        request.app.ctx.entities.insights.getSummary(code),
        request.app.ctx.entities.menus.getPublishLag(code, date_from, date_to),
        request.app.ctx.entities.menus.getRegionAverageMenuDays(
            restaurant.get("idreg"), code, date_from, date_to
        ),
    )

    repartition_repas = {"matin": 0, "midi": 0, "soir": 0}
    for row in repas_rows:
        tpr = row.get("tpr")
        if tpr in repartition_repas:
            repartition_repas[tpr] = row.get("nb")

    plats_uniques = (summary.get("plats_uniques") or 0) if summary else 0
    plats_total = (summary.get("nb_plats") or 0) if summary else 0
    taux_variete = round(plats_uniques / plats_total * 100, 1) if plats_total else 0.0

    nb_repas = (summary.get("nb_repas") or 0) if summary else 0
    nb_categories = (summary.get("nb_categories") or 0) if summary else 0
    moyenne_categories_par_repas = (
        round(nb_categories / nb_repas, 1) if nb_repas else 0.0
    )
    moyenne_plats_par_repas = round(plats_total / nb_repas, 1) if nb_repas else 0.0

    plats_frequents_raw = (
        loads(summary.get("plats_frequents")) if summary and summary.get("plats_frequents") else []
    )
    plats_frequents = [
        {
            "code": plat.get("code"),
            "libelle": plat.get("libelle"),
            "total": plat.get("total"),
        }
        for plat in plats_frequents_raw[:limit]
    ]

    lag_moyenne = lag_row.get("moyenne_jours") if lag_row else None
    region_moyenne = region_row.get("moyenne") if region_row else None
    region_nb = (region_row.get("nb_restaurants") if region_row else 0) or 0

    return JSON(
        request=request,
        success=True,
        data={
            "periode": {
                "debut": date_from.strftime("%d-%m-%Y"),
                "fin": date_to.strftime("%d-%m-%Y"),
            },
            "couverture": {
                "jours_ouvres": jours_ouvres,
                "jours_avec_menu": jours_avec_menu,
                "jours_sans_menu": jours_sans_menu,
                "taux_couverture": taux_couverture,
            },
            "repartition_repas": repartition_repas,
            "plats_frequents": plats_frequents,
            "couverture_par_jour": couverture_par_jour,
            "series": {
                "meilleure_serie_avec_menu": meilleure_serie_avec_menu,
                "plus_longue_serie_sans_menu": plus_longue_serie_sans_menu,
                "serie_actuelle": {
                    "avec_menu": serie_actuelle_avec_menu,
                    "jours": longueur_serie_actuelle,
                },
            },
            "variete": {
                "plats_uniques": plats_uniques,
                "plats_total": plats_total,
                "taux_variete": taux_variete,
            },
            "richesse": {
                "moyenne_categories_par_repas": moyenne_categories_par_repas,
                "moyenne_plats_par_repas": moyenne_plats_par_repas,
            },
            "delai_publication": {
                "moyenne_jours": round(float(lag_moyenne), 1) if lag_moyenne is not None else None,
            },
            "comparaison_regionale": {
                "jours_avec_menu_restaurant": jours_avec_menu,
                "moyenne_jours_avec_menu_region": round(float(region_moyenne), 1) if region_moyenne is not None else None,
                "nb_restaurants_compares": region_nb,
            },
        },
        status=200,
    ).generate()


# /restaurants/{code}/info
@bp.route("/<code>/info", methods=["GET"])
@openapi.definition(
    summary="Informations d'un restaurant",
    description="Informations d'un restaurant en fonction de son code.",
    tag="Restaurants",
)
@openapi.response(
    status=200,
    content={"application/json": RestaurantInfo},
    description="Informations d'un restaurant.",
)
@openapi.response(
    status=400,
    content={"application/json": BadRequest},
    description="L'ID du restaurant doit être un nombre.",
)
@openapi.response(
    status=404,
    content={"application/json": NotFound},
    description="Le restaurant n'existe pas.",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard.",
)
@openapi.parameter(
    name="code",
    description="ID du restaurant",
    required=True,
    schema=int,
    location="path",
    example=1,
)
@inputs(
    Argument(
        name="code",
        description="ID du restaurant",
        methods={"code": Rules.integer},
        call=int,
        required=True,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    )
)
@ratelimit()
@cache(ttl=300)
async def getInformations(request: Request, code: int) -> JSONResponse:
    """
    Retourne les informations d'un restaurant.

    :param code: ID du restaurant
    :return: Les informations du restaurant
    """
    info = await request.app.ctx.entities.restaurants.getInfo(code)

    if info is None:
        return JSON(
            request=request,
            success=False,
            message="Le restaurant n'existe pas.",
            status=404,
        ).generate()

    return JSON(
        request=request,
        success=True,
        data={
            "code": info.get("rid"),
            "ajout": info.get("ajout").strftime("%Y-%m-%d %H:%M:%S"),
            "modifie": info.get("modifie").strftime("%Y-%m-%d %H:%M:%S")
            if info.get("modifie")
            else None,
            "nb": info.get("taches"),
        },
        status=200,
    ).generate()


# /restaurants/{code}/activity
@bp.route("/<code>/activity", methods=["GET"])
@openapi.definition(
    summary="Activité d'un restaurant",
    description="Historique d'activité d'un restaurant : date d'ajout, dernière mise à jour, nombre de vérifications et dernières tâches d'ingestion l'ayant touché.",
    tag="Restaurants",
)
@openapi.response(
    status=200,
    content={"application/json": RestaurantActivity},
    description="Activité d'un restaurant.",
)
@openapi.response(
    status=400,
    content={"application/json": BadRequest},
    description="L'ID du restaurant doit être un nombre.",
)
@openapi.response(
    status=404,
    content={"application/json": NotFound},
    description="Le restaurant n'existe pas.",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard.",
)
@openapi.parameter(
    name="code",
    description="ID du restaurant",
    required=True,
    schema=int,
    location="path",
    example=1,
)
@openapi.parameter(
    name="limit",
    description="Nombre de dernières tâches d'ingestion à retourner (1-100, défaut 20)",
    required=False,
    schema=int,
    location="query",
    example=20,
)
@inputs(
    Argument(
        name="code",
        description="ID du restaurant",
        methods={"code": Rules.integer},
        call=int,
        required=True,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    )
)
@ratelimit()
@cache(ttl=60 * 15)  # 15 minutes
async def getRestaurantActivity(request: Request, code: int) -> JSONResponse:
    """
    Retourne l'activité d'un restaurant (ajout, dernière mise à jour, historique des vérifications).

    :param code: ID du restaurant
    :return: L'activité du restaurant
    """
    info = await request.app.ctx.entities.restaurants.getInfo(code)

    if info is None:
        return JSON(
            request=request,
            success=False,
            message="Le restaurant n'existe pas.",
            status=404,
        ).generate()

    limit_raw = request.args.get("limit", "20")
    limit = int(limit_raw) if Rules.integer(limit_raw) else 20
    limit = max(1, min(limit, 100))

    runs = await request.app.ctx.entities.taches.getForRestaurant(code, limit)

    return JSON(
        request=request,
        success=True,
        data={
            "ajout": info.get("ajout").strftime("%Y-%m-%d %H:%M:%S"),
            "modifie": info.get("modifie").strftime("%Y-%m-%d %H:%M:%S")
            if info.get("modifie")
            else None,
            "nb_verifications": info.get("taches"),
            "dernieres_verifications": [
                {
                    "id": run.get("id"),
                    "debut": run.get("debut").strftime("%Y-%m-%d %H:%M:%S")
                    if run.get("debut")
                    else None,
                    "fin": run.get("fin").strftime("%Y-%m-%d %H:%M:%S")
                    if run.get("fin")
                    else None,
                }
                for run in runs
            ],
        },
        status=200,
    ).generate()


# /restaurants/{code}/preview
@bp.route("/<code>/preview", methods=["GET"])
@openapi.definition(
    summary="Image d'un restaurant",
    description="Image d'un restaurant en fonction de son code.",
    tag="Restaurants",
)
@openapi.response(
    status=200, content={"image/png": Image}, description="Image d'un restaurant."
)
@openapi.response(
    status=400,
    content={"application/json": BadRequest},
    description="L'ID du restaurant doit être un nombre.",
)
@openapi.response(
    status=404,
    content={"application/json": NotFound},
    description="Le restaurant ou l'image n'existe pas.",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard.",
)
@openapi.parameter(
    name="code",
    description="ID du restaurant",
    required=True,
    schema=int,
    location="path",
    example=1,
)
@inputs(
    Argument(
        name="code",
        description="ID du restaurant",
        methods={"code": Rules.integer},
        call=int,
        required=True,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    )
)
@ratelimit(default_bucket=Bucket("media", 400, 60))
@cache(
    ttl=60 * 60  # 1 heure
)
async def getRestaurantPreview(request: Request, code: int) -> HTTPResponse:
    """
    Retourne le menu d'un restaurant.

    :param code: ID du restaurant
    :return: Le menu du restaurant
    """
    restaurant = await request.app.ctx.entities.restaurants.getPreview(code)

    if restaurant is None:
        return JSON(
            request=request,
            success=False,
            message="Le restaurant n'existe pas.",
            status=404,
        ).generate()

    content = restaurant.get("raw_image")

    if content is None:
        return JSON(
            request=request,
            success=False,
            message="L'image n'a pas pu être récupérée.",
            status=404,
        ).generate()

    return raw(
        body=content,
        status=200,
        headers={
            "Content-Disposition": f"attachment; filename={restaurant.get('nom')}.jpeg",
            "Content-Length": str(len(content)),
            "Content-Type": "image/jpeg",
        },
        content_type="image/jpeg",
    )


# /restaurants/types
@bp.route("/types", methods=["GET"])
@openapi.definition(
    summary="Liste des types de restaurants",
    description="Liste des types de restaurants disponibles.",
    tag="Restaurants",
)
@openapi.response(
    status=200,
    content={"application/json": TypesRestaurants},
    description="Liste des types des restaurants disponibles",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard.",
)
@ratelimit()
@cache(ttl=300)
async def getTypesRestaurants(request: Request) -> JSONResponse:
    """
    Récupère les types des restaurants

    :return: Les types des restaurants
    """
    types_restaurants = await request.app.ctx.entities.types_restaurants.getAll()

    return JSON(
        request=request,
        success=True,
        data=[
            {
                "code": type_restaurant.get("idtpr"),
                "libelle": type_restaurant.get("libelle"),
            }
            for type_restaurant in types_restaurants
        ],
        status=200,
    ).generate()
