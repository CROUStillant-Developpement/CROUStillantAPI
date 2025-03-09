from ....components.ratelimit import ratelimit
from ....components.response import JSON
from ....models.responses import ChangeLog
from ....models.exceptions import RateLimited
from sanic.response import JSONResponse
from sanic import Blueprint, Request
from sanic_ext import openapi
from json import loads


bp = Blueprint(
    name="Interne",
    url_prefix="/interne",
    version=1,
    version_prefix="v"
)


# /changelog
@bp.route("/changelog", methods=["GET"])
@openapi.definition(
    summary="Changelog des services de CROUStillant",
    description="Retourne le changelog des services de CROUStillant.",
    tag="Interne",
)
@openapi.response(
    status=200,
    content={
        "application/json": ChangeLog
    },
    description="Les dernières modifications des services de CROUStillant."
)
@openapi.response(
    status=429,
    content={
        "application/json": RateLimited
    },
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard."
)
@ratelimit()
async def getChangelog(request: Request) -> JSONResponse:
    """
    Retourne le changelog des services de CROUStillant.

    :return: JSONResponse
    """
    with open("changelog.json", "r") as f:
        changelog = loads(f.read())

    return JSON(
        request=request,
        success=True,
        data=changelog,
        status=200
    ).generate()
