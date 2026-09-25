import asyncio
import json

from ....components.events import TYPES, HISTORY_DAYS, EventBroker
from ....components.ratelimit import checkRatelimit
from ....models.exceptions import RateLimited, BadRequest
from ....components.response import JSON
from sanic import Blueprint, Request
from sanic.response import JSONResponse
from sanic_ext import openapi


bp = Blueprint(name="Evenements", url_prefix="/evenements", version=1, version_prefix="v")


# Intervalle d'envoi d'un commentaire de maintien de connexion (secondes)
HEARTBEAT_INTERVAL = 15

# Délai de reconnexion conseillé aux clients (millisecondes)
RETRY_DELAY = 5000


def parseIds(value: str | None, name: str) -> set[int] | None:
    """
    Convertit une liste d'IDs séparés par des virgules.
    """
    if not value:
        return None

    try:
        return {int(item) for item in value.split(",") if item.strip()}
    except ValueError:
        raise ValueError(f"Le paramètre '{name}' doit être une liste de nombres séparés par des virgules.")


def parseTypes(value: str | None) -> set[str] | None:
    """
    Convertit une liste de types d'événements séparés par des virgules.
    """
    if not value:
        return None

    types = {item.strip() for item in value.split(",") if item.strip()}
    unknown = types - set(TYPES)
    if unknown:
        raise ValueError(
            f"Types d'événements inconnus : {', '.join(sorted(unknown))}. Types disponibles : {', '.join(TYPES)}."
        )

    return types


def parseSince(value: str | None) -> int | None:
    """
    Convertit l'ID du dernier événement reçu (en-tête Last-Event-ID ou paramètre since).
    """
    if value is None or value == "":
        return None

    try:
        return int(value)
    except ValueError:
        raise ValueError("Le paramètre 'since' (ou l'en-tête Last-Event-ID) doit être un nombre.")


def formatEvent(event: dict) -> str:
    """
    Formate un événement au format Server-Sent Events.
    """
    data = json.dumps(event, ensure_ascii=False)
    return f"id: {event['id']}\nevent: {event['type']}\ndata: {data}\n\n"


# /evenements
@bp.route("/", methods=["GET"])
@openapi.definition(
    summary="Flux des événements en temps réel",
    description=(
        "Flux [Server-Sent Events](https://developer.mozilla.org/fr/docs/Web/API/Server-sent_events) "
        "des changements de menus et de restaurants, envoyés dès leur enregistrement.\n\n"
        f"Types d'événements : `{'`, `'.join(TYPES)}`.\n\n"
        "Chaque événement a un `id` croissant. En cas de déconnexion, reconnectez-vous avec l'en-tête "
        "`Last-Event-ID` (envoyé automatiquement par `EventSource`) ou le paramètre `since` pour recevoir "
        f"les événements manqués (jusqu'à {HISTORY_DAYS} jours). "
        f"Un commentaire est envoyé toutes les {HEARTBEAT_INTERVAL} secondes pour maintenir la connexion.\n\n"
        "Les événements indiquent ce qui a changé : utilisez les routes `/restaurants` pour récupérer les données."
    ),
    tag="Evenements",
)
@openapi.response(
    status=200,
    content={"text/event-stream": str},
    description=(
        "Flux d'événements, par exemple :\n\n"
        "```\nid: 1234\nevent: menu.updated\n"
        'data: {"id": 1234, "type": "menu.updated", "code": 871, "date": "25-09-2026", '
        '"menu": 1879114, "donnees": null, "creation": "24-09-2026 09:05:07"}\n```'
    ),
)
@openapi.response(
    status=400,
    content={"application/json": BadRequest},
    description="Paramètres invalides.",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard.",
)
@openapi.parameter(
    name="code",
    description="Restaurants suivis (IDs séparés par des virgules). Par défaut : tous.",
    required=False,
    schema=str,
    location="query",
    example="870,871",
)
@openapi.parameter(
    name="types",
    description="Types d'événements suivis (séparés par des virgules). Par défaut : tous.",
    required=False,
    schema=str,
    location="query",
    example="menu.created,menu.updated",
)
@openapi.parameter(
    name="since",
    description="Reçoit d'abord les événements postérieurs à cet ID (équivalent à l'en-tête `Last-Event-ID`).",
    required=False,
    schema=int,
    location="query",
    example=1234,
)
async def getEvenements(request: Request) -> JSONResponse | None:
    """
    Flux des événements en temps réel (Server-Sent Events).
    """
    headers = await checkRatelimit(request)

    try:
        rids = parseIds(request.args.get("code"), "code")
        types = parseTypes(request.args.get("types"))
        since = parseSince(request.headers.get("Last-Event-ID") or request.args.get("since"))
    except ValueError as e:
        return JSON(request=request, success=False, message=str(e), status=400).generate()

    broker: EventBroker = request.app.ctx.events

    # Abonnement avant le rattrapage : aucun événement n'est perdu entre les deux
    subscription = broker.subscribe(rids, types)

    try:
        response = await request.respond(
            content_type="text/event-stream; charset=utf-8",
            headers={
                **headers,
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

        await response.send(f"retry: {RETRY_DELAY}\n\n")

        lastSent = since if since is not None else 0

        if since is not None:
            for event in await broker.history(since, rids, types):
                await response.send(formatEvent(event))
                lastSent = event["id"]

        while True:
            try:
                event = await asyncio.wait_for(
                    subscription.queue.get(), timeout=HEARTBEAT_INTERVAL
                )
            except TimeoutError:
                await response.send(": ping\n\n")
                continue

            if event is None:
                # Abonnement terminé (client trop lent ou arrêt du serveur)
                break

            if event["id"] <= lastSent:
                # Déjà envoyé lors du rattrapage
                continue

            await response.send(formatEvent(event))
            lastSent = event["id"]

        await response.eof()
    finally:
        broker.unsubscribe(subscription)
