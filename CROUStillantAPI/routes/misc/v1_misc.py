from ...components.ratelimit import ratelimit
from sanic.response import HTTPResponse, redirect
from sanic import Blueprint, Request
from sanic_ext import openapi


bp = Blueprint(
    name="Misc",
    url_prefix="/",
    version=1,
    version_prefix="v"
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
