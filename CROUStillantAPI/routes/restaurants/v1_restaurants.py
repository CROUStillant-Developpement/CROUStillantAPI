from ...components.ratelimit import ratelimit
from ...components.generate import generate
from ...components.response import JSON
from ...models.responses import Restaurants, Restaurant, TypesRestaurants, RestaurantInfo, Menus, Menu, Dates, Image
from ...models.exceptions import RateLimited, BadRequest, NotFound
from ...utils.opening import Opening
from ...utils.image import saveImageToBuffer
from ...utils.format import getBoolFromString
from sanic.response import JSONResponse, raw
from sanic import Blueprint, Request
from sanic_ext import openapi
from json import loads
from datetime import datetime
from pytz import timezone
from asyncio import get_event_loop


bp = Blueprint(
    name="Restaurants",
    url_prefix="/restaurants",
    version=1,
    version_prefix="v"
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
    content={
        "application/json": Restaurants
    },
    description="Liste des restaurants disponibles"
)
@openapi.response(
    status=429,
    content={
        "application/json": RateLimited
    },
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard."
)
@openapi.parameter(
    name="actif",
    description="Renvoie uniquement les restaurants actifs",
    required=False,
    schema=bool,
    location="query",
    example=True
)
@ratelimit()
async def getRestaurants(request: Request) -> JSONResponse:
    """
    Récupère les restaurants

    :return: Les restaurants
    """
    restaurants = await request.app.ctx.entities.restaurants.getAll(actif=getBoolFromString(request.args.get("actif", True)))

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
                "ouvert": restaurant.get("opened"),
                "actif": restaurant.get("actif")
            } for restaurant in restaurants
        ],
        status=200
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
    content={
        "application/json": Restaurant
    },
    description="Détails d'un restaurant."
)
@openapi.response(
    status=400,
    content={
        "application/json": BadRequest
    },
    description="L'ID du restaurant doit être un nombre."
)
@openapi.response(
    status=404,
    content={
        "application/json": NotFound
    },
    description="Le restaurant n'existe pas."
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
    description="ID du restaurant",
    required=True,
    schema=int,
    location="path",
    example=1
)
@ratelimit()
async def getRestaurant(request: Request, code: int) -> JSONResponse:
    """
    Retourne les détails d'un restaurant.

    :param code: ID du restaurant
    :return: Le restaurant
    """
    try:
        restaurantID = int(code)
    except ValueError:
        return JSON(
            request=request,
            success=False,
            message="L'ID du restaurant doit être un nombre.",
            status=400
        ).generate()


    restaurant = await request.app.ctx.entities.restaurants.getOne(restaurantID)

    if restaurant is None:
        return JSON(
            request=request,
            success=False,
            message="Le restaurant n'existe pas.",
            status=404
        ).generate()


    return JSON(
        request=request,
        success=True,
        data={
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
            "ouvert": restaurant.get("opened"),
            "actif": restaurant.get("actif")
        },
        status=200
    ).generate()


# /restaurants/{code}/menu
@bp.route("/<code>/menu", methods=["GET"])
@openapi.definition(
    summary="Menu d'un restaurant",
    description="Menu d'un restaurant en fonction de son code.",
    tag="Restaurants",
)
@openapi.response(
    status=200,
    content={
        "application/json": Menus
    },
    description="Menu d'un restaurant."
)
@openapi.response(
    status=400,
    content={
        "application/json": BadRequest
    },
    description="L'ID du restaurant doit être un nombre."
)
@openapi.response(
    status=404,
    content={
        "application/json": NotFound
    },
    description="Le restaurant n'existe pas."
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
    description="ID du restaurant",
    required=True,
    schema=int,
    location="path",
    example=1
)
@ratelimit()
async def getRestaurantMenu(request: Request, code: int) -> JSONResponse:
    """
    Retourne le menu d'un restaurant.

    :param code: ID du restaurant
    :return: Le menu du restaurant
    """
    try:
        restaurantID = int(code)
    except ValueError:
        return JSON(
            request=request,
            success=False,
            message="L'ID du restaurant doit être un nombre.",
            status=400
        ).generate()


    menu = await request.app.ctx.entities.menus.getCurrent(
        id=restaurantID, 
        date=datetime.now(
            tz=timezone("Europe/Paris")
        )
    )

    if menu is None or len(menu) == 0:
        return JSON(
            request=request,
            success=False,
            message="Aucun menu n'est disponible pour ce restaurant.",
            status=404
        ).generate()


    menu_per_day = {}
    for row in menu:
        date = row.get("date").strftime("%d-%m-%Y")

        day_menu = menu_per_day.setdefault(date, {
            "code": row.get("mid"),
            "date": date,
            "repas": []
        })

        repas_list = day_menu["repas"]

        if not repas_list or row.get("tpr") not in repas_list[-1]["type"]:
            repas_list.append(
                {
                    "code": row.get("rpid"),
                    "type": row.get("tpr"),
                    "categories": []
                }
            )

        repas = repas_list[-1]
        categories_list = repas["categories"]

        if not categories_list or row.get("tpcat") not in categories_list[-1]["libelle"]:
            categories_list.append(
                {
                    "code": row.get("catid"),
                    "libelle": row.get("tpcat"),
                    "ordre": row.get("cat_ordre") + 1,
                    "plats": []
                }
            )

        categories_list[-1]["plats"].append(
            {
                "code": row.get("platid"),
                "ordre": row.get("plat_ordre") + 1,
                "libelle": row.get("plat")
            }
        )

    keys = list(menu_per_day.keys())
    menus = []
    for key in keys:
        menus.append(menu_per_day[key])

    return JSON(
        request=request,
        success=True,
        data=menus,
        status=200
    ).generate()


# /restaurants/{code}/menu/dates
@bp.route("/<code>/menu/dates", methods=["GET"])
@openapi.definition(
    summary="Dates des prochains menus disponibles d'un restaurant",
    description="Dates des prochains menus disponibles d'un restaurant en fonction de son code.",
    tag="Restaurants",
)
@openapi.response(
    status=200,
    content={
        "application/json": Dates
    },
    description="Dates des prochains menus disponibles"
)
@openapi.response(
    status=400,
    content={
        "application/json": BadRequest
    },
    description="L'ID du restaurant doit être un nombre."
)
@openapi.response(
    status=404,
    content={
        "application/json": NotFound
    },
    description="Le restaurant n'existe pas."
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
    description="ID du restaurant",
    required=True,
    schema=int,
    location="path",
    example=1
)
@ratelimit()
async def getRestaurantMenuDates(request: Request, code: int) -> JSONResponse:
    """
    Retourne les dates des prochains menus disponibles

    :param code: ID du restaurant
    :return: Le menu du restaurant
    """
    try:
        restaurantID = int(code)
    except ValueError:
        return JSON(
            request=request,
            success=False,
            message="L'ID du restaurant doit être un nombre.",
            status=400
        ).generate()


    dates = await request.app.ctx.entities.menus.getDates(
        id=restaurantID
    )

    if dates is None or len(dates) == 0:
        return JSON(
            request=request,
            success=False,
            message="Aucun menu n'a été trouvé.",
            status=404
        ).generate()


    return JSON(
        request=request,
        success=True,
        data=[
            {
                "code": row.get("mid"),
                "date": row.get("date").strftime("%d-%m-%Y")
            } for row in dates
        ],
        status=200
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
    content={
        "application/json": Dates
    },
    description="Dates des menus disponibles"
)
@openapi.response(
    status=400,
    content={
        "application/json": BadRequest
    },
    description="L'ID du restaurant doit être un nombre."
)
@openapi.response(
    status=404,
    content={
        "application/json": NotFound
    },
    description="Le restaurant n'existe pas."
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
    description="ID du restaurant",
    required=True,
    schema=int,
    location="path",
    example=1
)
@ratelimit()
async def getRestaurantMenuAllDates(request: Request, code: int) -> JSONResponse:
    """
    Retourne les dates des menus disponibles

    :param code: ID du restaurant
    :return: Le menu du restaurant
    """
    try:
        restaurantID = int(code)
    except ValueError:
        return JSON(
            request=request,
            success=False,
            message="L'ID du restaurant doit être un nombre.",
            status=400
        ).generate()


    dates = await request.app.ctx.entities.menus.getAllDates(
        id=restaurantID
    )

    if dates is None or len(dates) == 0:
        return JSON(
            request=request,
            success=False,
            message="Aucun menu n'a été trouvé.",
            status=404
        ).generate()


    return JSON(
        request=request,
        success=True,
        data=[
            {
                "code": row.get("mid"),
                "date": row.get("date").strftime("%d-%m-%Y")
            } for row in dates
        ],
        status=200
    ).generate()


# /restaurants/{code}/menu/{date}
@bp.route("/<code>/menu/<date>", methods=["GET"])
@openapi.definition(
    summary="Menu d'un restaurant à une date donnée",
    description="Menu d'un restaurant en fonction de son code et d'une date donnée.",
    tag="Restaurants",
)
@openapi.response(
    status=200,
    content={
        "application/json": Menu
    },
    description="Menu d'un restaurant."
)
@openapi.response(
    status=400,
    content={
        "application/json": BadRequest
    },
    description="L'ID du restaurant doit être un nombre et la date doit être au format DD-MM-YYYY."
)
@openapi.response(
    status=404,
    content={
        "application/json": NotFound
    },
    description="Le restaurant n'existe pas."
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
    description="ID du restaurant",
    required=True,
    schema=int,
    location="path",
    example=1
)
@openapi.parameter(
    name="date",
    description="Date du menu (format: DD-MM-YYYY)",
    required=True,
    schema=str,
    location="path",
    example="21-10-2024"
)
@ratelimit()
async def getRestaurantMenuFromDate(request: Request, code: int, date: str) -> JSONResponse:
    """
    Retourne le menu d'un restaurant.

    :param code: ID du restaurant
    :param date: Date du menu
    :return: Le menu du restaurant
    """
    try:
        restaurantID = int(code)

        date = datetime.strptime(date, "%d-%m-%Y")
    except ValueError:
        return JSON(
            request=request,
            success=False,
            message="L'ID du restaurant doit être un nombre et la date doit être au format DD-MM-YYYY.",
            status=400
        ).generate()


    menu = await request.app.ctx.entities.menus.getFromDate(
        id=restaurantID, 
        date=date
    )

    if menu is None or len(menu) == 0:
        return JSON(
            request=request,
            success=False,
            message="Aucun menu n'a été trouvé pour cette date.",
            status=404
        ).generate()


    menu_per_day = {}
    for row in menu:
        date = row.get("date").strftime("%d-%m-%Y")

        day_menu = menu_per_day.setdefault(date, {
            "code": row.get("mid"),
            "date": date,
            "repas": []
        })

        repas_list = day_menu["repas"]

        if not repas_list or row.get("tpr") not in repas_list[-1]["type"]:
            repas_list.append(
                {
                    "code": row.get("rpid"),
                    "type": row.get("tpr"),
                    "categories": []
                }
            )

        repas = repas_list[-1]
        categories_list = repas["categories"]

        if not categories_list or row.get("tpcat") not in categories_list[-1]["libelle"]:
            categories_list.append(
                {
                    "code": row.get("catid"),
                    "libelle": row.get("tpcat"),
                    "ordre": row.get("cat_ordre") + 1,
                    "plats": []
                }
            )

        categories_list[-1]["plats"].append(
            {
                "code": row.get("platid"),
                "ordre": row.get("plat_ordre") + 1,
                "libelle": row.get("plat")
            }
        )


    return JSON(
        request=request,
        success=True,
        data=menu_per_day[date],
        status=200
    ).generate()


# /restaurants/{code}/menu/{date}/image
@bp.route("/<code>/menu/<date>/image", methods=["GET"])
@openapi.definition(
    summary="Menu d'un restaurant à une date donnée sous forme d'image",
    description="Menu d'un restaurant en fonction de son code et d'une date donnée sous forme d'image.",
    tag="Restaurants",
)
@openapi.response(
    status=200,
    content={
        "image/png": Image
    },
    description="Menu d'un restaurant sous forme d'image."
)
@openapi.response(
    status=400,
    content={
        "application/json": BadRequest
    },
    description="L'ID du restaurant doit être un nombre et la date doit être au format DD-MM-YYYY."
)
@openapi.response(
    status=404,
    content={
        "application/json": NotFound
    },
    description="Le restaurant n'existe pas."
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
    description="ID du restaurant",
    required=True,
    schema=int,
    location="path",
    example=1
)
@openapi.parameter(
    name="date",
    description="Date du menu (format: DD-MM-YYYY)",
    required=True,
    schema=str,
    location="path",
    example="21-10-2024"
)
@openapi.parameter(
    name="repas",
    description="Repas du menu",
    required=False,
    schema=str,
    location="query",
    example="midi"
)
@openapi.parameter(
    name="theme",
    description="Thème de l'image",
    required=False,
    schema=str,
    location="query",
    example="light"
)
@ratelimit()
async def getRestaurantMenuFromDateImage(request: Request, code: int, date: str) -> JSONResponse:
    """
    Retourne le menu d'un restaurant.

    :param code: ID du restaurant
    :param date: Date du menu:
    :param repas: Repas du menu
    :param theme: Thème de l'image
    :return: Le menu du restaurant
    """
    try:
        restaurantID = int(code)

        date = datetime.strptime(date, "%d-%m-%Y")
    except ValueError:
        return JSON(
            request=request,
            success=False,
            message="L'ID du restaurant doit être un nombre et la date doit être au format DD-MM-YYYY.",
            status=400
        ).generate()


    repas = request.args.get("repas", "midi").lower() if request.args.get("repas", "midi").lower() in ["matin", "midi", "soir"] else "midi"
    theme = request.args.get("theme", "light").lower() if request.args.get("theme", "light").lower() in ["light", "dark"] else "light"

    restaurant = await request.app.ctx.entities.restaurants.getOne(restaurantID)

    menu = await request.app.ctx.entities.menus.getFromDate(
        id=restaurantID, 
        date=date
    )

    if menu:
        menu_per_day = {}
        for row in menu:
            d = row.get("date").strftime("%d-%m-%Y")

            day_menu = menu_per_day.setdefault(
                d, 
                {
                    "code": row.get("mid"),
                    "date": d,
                    "repas": []
                }
            )

            repas_list = day_menu["repas"]

            if not repas_list or row.get("tpr") not in repas_list[-1]["type"]:
                repas_list.append(
                    {
                        "code": row.get("rpid"),
                        "type": row.get("tpr"),
                        "categories": []
                    }
                )

            r = repas_list[-1]
            categories_list = r["categories"]

            if not categories_list or row.get("tpcat") not in categories_list[-1]["libelle"]:
                categories_list.append(
                    {
                        "code": row.get("catid"),
                        "libelle": row.get("tpcat"),
                        "ordre": row.get("cat_ordre") + 1,
                        "plats": []
                    }
                )

            categories_list[-1]["plats"].append(
                {
                    "code": row.get("platid"),
                    "ordre": row.get("plat_ordre") + 1,
                    "libelle": row.get("plat")
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


    def generate_image_in_background(restaurant, menu, date, theme):
        image = generate(
            restaurant=restaurant, 
            menu=menu,
            date=date, 
            theme=theme
        )
        buffer = saveImageToBuffer(image, compression_level=1)
        return buffer.getvalue()


    loop = get_event_loop()
    content = await loop.run_in_executor(
        request.app.ctx.executor, 
        generate_image_in_background, 
        restaurant, data, date, theme
    )

    return raw(
        body=content,
        status=200,
        headers={
            "Content-Disposition": f"attachment; filename={restaurant.get('nom')} - {date.strftime('%d-%m-%Y')}.png",
            "Content-Length": str(len(content)),
            "Content-Type": "image/png"
        },
        content_type="image/png"
    )


# /restaurants/{code}/info
@bp.route("/<code>/info", methods=["GET"])
@openapi.definition(
    summary="Informations d'un restaurant",
    description="Informations d'un restaurant en fonction de son code.",
    tag="Restaurants",
)
@openapi.response(
    status=200,
    content={
        "application/json": RestaurantInfo
    },
    description="Informations d'un restaurant."
)
@openapi.response(
    status=400,
    content={
        "application/json": BadRequest
    },
    description="L'ID du restaurant doit être un nombre."
)
@openapi.response(
    status=404,
    content={
        "application/json": NotFound
    },
    description="Le restaurant n'existe pas."
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
    description="ID du restaurant",
    required=True,
    schema=int,
    location="path",
    example=1
)
@ratelimit()
async def getInformations(request: Request, code: int) -> JSONResponse:
    """
    Retourne les informations d'un restaurant.

    :param code: ID du restaurant
    :return: Les informations du restaurant
    """
    try:
        restaurantID = int(code)
    except ValueError:
        return JSON(
            request=request,
            success=False,
            message="L'ID du restaurant doit être un nombre.",
            status=400
        ).generate()


    info = await request.app.ctx.entities.restaurants.getInfo(restaurantID)

    if info is None:
        return JSON(
            request=request,
            success=False,
            message="Le restaurant n'existe pas.",
            status=404
        ).generate()


    return JSON(
        request=request,
        success=True,
        data={
            "code": info.get("rid"),
            "ajout": info.get("ajout").strftime("%Y-%m-%d %H:%M:%S"),
            "modifie": info.get("modifie").strftime("%Y-%m-%d %H:%M:%S") if info.get("modifie") else None,
            "nb": info.get("taches"),
        },
        status=200
    ).generate()


# /restaurants/types
@bp.route("/types", methods=["GET"])
@openapi.definition(
    summary="Liste des types de restaurants",
    description="Liste des types de restaurants disponibles.",
    tag="Restaurants",
)
@openapi.response(
    status=200,
    content={
        "application/json": TypesRestaurants
    },
    description="Liste des types des restaurants disponibles"
)
@openapi.response(
    status=429,
    content={
        "application/json": RateLimited
    },
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard."
)
@ratelimit()
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
                "libelle": type_restaurant.get("libelle")
            } for type_restaurant in types_restaurants
        ],
        status=200
    ).generate()
