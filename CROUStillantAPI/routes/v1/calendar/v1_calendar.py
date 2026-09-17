from ....components.ratelimit import ratelimit
from ....components.cache import cache
from ....components.argument import Argument, inputs
from ....components.rules import Rules
from ....models.exceptions import RateLimited, BadRequest, NotFound
from ....utils.format import getBoolFromString
from ....utils.calendar import (
    restaurantMenuCalendar,
    CALENDAR_BUCKET,
    CALENDAR_CACHE_TTL,
)
from sanic.response import HTTPResponse
from sanic import Blueprint, Request
from sanic_ext import openapi


# Sans version : l'URL d'un abonnement est conservée indéfiniment par les applications
# de calendrier, elle doit donc survivre aux futures versions de l'API.
bp = Blueprint(name="Calendar", url_prefix="/calendar")


# /calendar/{code}.ics
@bp.route("/<code:ext=ics>", methods=["GET"])
@openapi.definition(
    summary="Calendrier des menus d'un restaurant (iCalendar)",
    description=(
        "Flux iCalendar (.ics) des menus d'un restaurant, un événement par repas. "
        "Peut être ajouté en abonnement dans Google Agenda, Apple Calendar ou Outlook "
        "et se met à jour automatiquement. Les menus des 14 derniers jours sont conservés. "
        "Cette URL est stable et indépendante de la version de l'API : utilisez-la pour les abonnements."
    ),
    tag="Restaurants",
)
@openapi.response(
    status=200,
    content={"text/calendar": str},
    description="Calendrier iCalendar des menus.",
)
@openapi.response(
    status=400,
    content={"application/json": BadRequest},
    description="L'ID du restaurant doit être un nombre et les repas doivent être valides.",
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
    name="repas",
    description="Repas à inclure séparés par des virgules (matin, midi, soir). Tous par défaut.",
    required=False,
    schema=str,
    location="query",
    example="midi,soir",
)
@openapi.parameter(
    name="minimal",
    description="Utilise des créneaux fixes de 15 minutes (8h00, 12h00, 19h00) au lieu des horaires du restaurant.",
    required=False,
    schema=bool,
    location="query",
    example=False,
)
@cache(ttl=CALENDAR_CACHE_TTL)
@ratelimit(default_bucket=CALENDAR_BUCKET)
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
        name="repas",
        description="Repas à inclure séparés par des virgules",
        methods={"repas": Rules.iframe_meals},
        call=lambda x: [m.strip() for m in x.split(",") if m.strip()],
        required=False,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    )
)
@inputs(
    Argument(
        name="minimal",
        description="Utilise des créneaux fixes de 15 minutes",
        methods={"minimal": Rules.boolean},
        call=getBoolFromString,
        required=False,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    )
)
async def getCalendar(
    request: Request,
    code: int,
    ext: str,
    repas: list[str] | None = None,
    minimal: bool | None = None,
) -> HTTPResponse:
    """
    Retourne le calendrier iCalendar des menus d'un restaurant (alias sans version).

    :param code: ID du restaurant
    :param ext: Extension du fichier (toujours ``ics``)
    :param repas: Repas à inclure
    :param minimal: Utilise des créneaux fixes de 15 minutes
    :return: Le fichier .ics
    """
    return await restaurantMenuCalendar(
        request, code, meals=repas, minimal=bool(minimal)
    )
