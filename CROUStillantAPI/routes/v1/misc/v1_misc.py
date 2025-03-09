from ....components.ratelimit import ratelimit
from sanic.response import HTTPResponse, redirect, file
from sanic import Blueprint, Request
from sanic_ext import openapi


bp = Blueprint(
    name="Misc",
    url_prefix="/"
)


# /contact
@bp.route("/contact", methods=["GET"])
@openapi.no_autodoc
@openapi.exclude()
@ratelimit()
async def redirectEmail(request: Request) -> HTTPResponse:
    """
    Redirige vers l'adresse e-mail de contact.

    :return: Redirige vers l'adresse e-mail de contact
    """
    return redirect("mailto:croustillant@bayfield.dev")


# /favicon.ico
@bp.route("/favicon.ico", methods=["GET"])
@openapi.no_autodoc
@openapi.exclude()
@ratelimit()
async def favicon(request: Request) -> HTTPResponse:
    """
    Redirige vers l'icône du site.

    :return: Redirige vers l'icône du site
    """
    return await file(
        location="./static/favicon.ico"
    )
