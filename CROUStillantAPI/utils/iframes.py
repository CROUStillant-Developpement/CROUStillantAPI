from ..components.response import JSON
from sanic import Request
from sanic.response import raw, HTTPResponse
from datetime import datetime
from pytz import timezone
from jinja2 import Environment
from json import loads


_DEFAULT_BLOCKS = ["header", "status", "menu", "hours"]
_DEFAULT_MEALS  = ["matin", "midi", "soir"]
_DEFAULT_COLOR  = "#ef4444"
_DEFAULT_FONT   = "Inter"
_DEFAULT_THEME  = "light"
_DEFAULT_HEIGHT = 600
_DEFAULT_LANG   = "fr"


async def restaurantMenuIframe(
    request: Request, code: int, date: datetime, jinja_env: Environment
) -> HTTPResponse:
    """
    Retourne le menu d'un restaurant sous forme de iframe.

    :param request: La requête
    :type request: Request
    :param code: Le code du restaurant
    :type code: int
    :param date: La date du menu
    :type date: datetime
    :param jinja_env: L'environnement Jinja2
    :type jinja_env: Environment
    :return: Le menu sous forme de iframe
    :rtype: HTTPResponse
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

    dt_date = date

    date_str = dt_date.strftime("%d-%m-%Y")

    menu_items = await request.app.ctx.entities.menus.getFromDate(id=code, date=dt_date)
    menu_data = None

    if menu_items and len(menu_items) > 0:
        menu_per_day = {}
        for row in menu_items:
            d = row.get("date").strftime("%d-%m-%Y")
            day_menu = menu_per_day.setdefault(
                d, {"code": row.get("mid"), "date": d, "repas": []}
            )
            repas_list = day_menu["repas"]

            if not repas_list or row.get("tpr") not in repas_list[-1]["type"]:
                repas_list.append(
                    {"code": row.get("rpid"), "type": row.get("tpr"), "categories": []}
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

        if date_str in menu_per_day:
            menu_data = menu_per_day[date_str]

    template = jinja_env.get_template("iframe_menu.html")
    html_content = template.render(
        request=request,
        restaurant=restaurant,
        preview=preview is not None,
        menu=menu_data,
        date_str=dt_date.strftime("%d/%m/%Y"),
    )

    return raw(body=html_content, content_type="text/html; charset=utf-8", status=200)


async def restaurantCustomIframe(
    request: Request,
    code: int,
    jinja_env: Environment,
    *,
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
    Retourne un iframe personnalisé d'un restaurant.

    Les paramètres sont pré-validés par le décorateur @inputs du handler.
    """
    theme = theme or _DEFAULT_THEME

    blocks_list = (
        list(dict.fromkeys(b.strip() for b in blocks.split(",") if b.strip()))
        if blocks else _DEFAULT_BLOCKS[:]
    )

    meals_list = (
        [m.strip() for m in meals.split(",") if m.strip()]
        if meals else _DEFAULT_MEALS[:]
    )

    accent_color = f"#{color}" if color else _DEFAULT_COLOR

    font = font or _DEFAULT_FONT

    dt_date = (
        datetime.strptime(date, "%d-%m-%Y")
        if date else datetime.now(tz=timezone("Europe/Paris"))
    )

    height = height if height is not None else _DEFAULT_HEIGHT

    lang = lang or _DEFAULT_LANG

    restaurant = await request.app.ctx.entities.restaurants.getOne(code)
    if not restaurant:
        return JSON(
            request=request,
            success=False,
            message="Le restaurant n'existe pas.",
            status=404,
        ).generate()

    parsed_restaurant = dict(restaurant)
    for field in ("horaires", "paiement", "acces"):
        if parsed_restaurant.get(field):
            try:
                parsed_restaurant[field] = loads(parsed_restaurant[field])
            except Exception:
                parsed_restaurant[field] = None

    preview = await request.app.ctx.entities.restaurants.getPreview(code)

    menu_data = None
    if "menu" in blocks_list:
        menu_items = await request.app.ctx.entities.menus.getFromDate(
            id=code, date=dt_date
        )
        if menu_items:
            menu_per_day = {}
            for row in menu_items:
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

            date_key = dt_date.strftime("%d-%m-%Y")
            if date_key in menu_per_day:
                menu_data = menu_per_day[date_key]
                menu_data["repas"] = [
                    r for r in menu_data["repas"] if r["type"] in meals_list
                ]

    template = jinja_env.get_template("iframe_custom.html")
    html_content = template.render(
        request=request,
        restaurant=parsed_restaurant,
        preview=preview is not None,
        menu=menu_data,
        date_str=dt_date.strftime("%d/%m/%Y"),
        blocks=blocks_list,
        theme=theme,
        accent_color=accent_color,
        font=font,
        height=height,
        lang=lang,
    )

    return raw(body=html_content, content_type="text/html; charset=utf-8", status=200)
