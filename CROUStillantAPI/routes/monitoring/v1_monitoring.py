from ...components.ratelimit import ratelimit
from ...components.response import JSON
from sanic.response import JSONResponse
from sanic import Blueprint, Request
from sanic_ext import openapi


bp = Blueprint(
    name="Monitoring",
    url_prefix="/monitoring",
    version=1,
    version_prefix="v"
)


# /cache
@bp.route("/cache", methods=["GET"])
@openapi.no_autodoc
@openapi.exclude()
@ratelimit()
async def getStatus(request: Request) -> JSONResponse:
    """
    Retourne les informations du cache

    :return: JSONResponse
    """
    cache = request.app.cache

    return JSON({
        "size": len(cache.cache),
        "last_check": cache.last_check,
        "expiration_time": cache.expiration_time,
        "keys": await cache.get_all_keys()
    })
