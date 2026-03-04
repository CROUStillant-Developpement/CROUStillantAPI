from ..components.response import JSON
from sanic import Request
from sanic.response import raw, HTTPResponse
from sanic.log import logger
from datetime import datetime
from pytz import timezone
from jinja2 import Environment, FileSystemLoader


async def restaurantMenuIframe(request: Request, code: int, date: datetime, jinja_env: Environment)-> HTTPResponse:
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
            day_menu = menu_per_day.setdefault(d, {"code": row.get("mid"), "date": d, "repas": []})
            repas_list = day_menu["repas"]

            if not repas_list or row.get("tpr") not in repas_list[-1]["type"]:
                repas_list.append({"code": row.get("rpid"), "type": row.get("tpr"), "categories": []})

            r = repas_list[-1]
            categories_list = r["categories"]

            if not categories_list or row.get("tpcat") not in categories_list[-1]["libelle"]:
                categories_list.append({
                    "code": row.get("catid"),
                    "libelle": row.get("tpcat"),
                    "ordre": row.get("cat_ordre") + 1,
                    "plats": [],
                })

            if row.get("platid") is not None:
                categories_list[-1]["plats"].append({
                    "code": row.get("platid"),
                    "ordre": row.get("plat_ordre") + 1,
                    "libelle": row.get("plat"),
                })

        if date_str in menu_per_day:
            menu_data = menu_per_day[date_str]

    template = jinja_env.get_template("iframe_menu.html")
    html_content = template.render(
        request=request,
        restaurant=restaurant,
        preview=preview is not None,
        menu=menu_data,
        date_str=dt_date.strftime("%d/%m/%Y")
    )

    return raw(
        body=html_content,
        content_type="text/html; charset=utf-8",
        status=200
    )