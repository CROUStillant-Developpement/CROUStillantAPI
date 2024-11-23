from ...components.ratelimit import ratelimit
from sanic.response import HTTPResponse, file
from sanic import Blueprint, Request
from sanic_ext import openapi, render
from datetime import datetime
from pytz import timezone


bp = Blueprint(
    name="BetterIUTRCC",
    url_prefix="/betteriutrcc",
    version=1,
    version_prefix="v"
)


# /assets/style.css
@bp.route("/assets/style.css", methods=["GET"])
@openapi.no_autodoc
@openapi.exclude()
@ratelimit()
async def getPageStyle(request: Request) -> HTTPResponse:
    """
    Retourne le style de la page.

    :return: Le style de la page
    """
    return await file(
        location="./static/betteriutrcc/app.css"
    )


# /menu
@bp.route("/menu", methods=["GET"])
@openapi.no_autodoc
@openapi.exclude()
@ratelimit()
async def getMenu(request: Request) -> HTTPResponse:
    """
    Retourne le menu de la page.

    :return: Le menu de la page
    """
    return await render(
        "betteriutrcc/crous.html",
        context={
            "theme": request.args.get("theme", "light").lower() if request.args.get("theme", "light").lower() in ["light", "dark"] else "light",
            "date": datetime.now(timezone("Europe/Paris")).strftime("%d-%m-%Y")
        }
    )
