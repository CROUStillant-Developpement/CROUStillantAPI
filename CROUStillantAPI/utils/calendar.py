import re
import unicodedata

from ..components.ratelimit import Bucket
from ..components.response import JSON
from .menu import build_menu_structure
from sanic import Request
from sanic.response import raw, HTTPResponse
from datetime import datetime, date as date_cls, time, timedelta
from json import loads
from pytz import timezone, utc


PARIS = timezone("Europe/Paris")

# Les applications de calendrier (Google Agenda en tête) interrogent les flux depuis
# un petit nombre d'adresses IP partagées par tous leurs utilisateurs : la limite
# par IP par défaut serait atteinte dès quelques centaines d'abonnés.
CALENDAR_BUCKET = Bucket("calendar", 1000, 60)

# Durée de cache des flux : les réponses en cache ne consomment pas de quota.
CALENDAR_CACHE_TTL = 60 * 30

WEBSITE_URL = "https://croustillant.menu"

# Créneaux utilisés lorsque les horaires du restaurant ne permettent pas de déduire l'heure d'un repas
DEFAULT_SLOTS: dict[str, tuple[time, time]] = {
    "matin": (time(7, 30), time(9, 30)),
    "midi": (time(11, 30), time(13, 30)),
    "soir": (time(18, 30), time(20, 0)),
}

MINIMAL_SLOTS: dict[str, tuple[time, time]] = {
    "matin": (time(8, 00), time(8, 15)),
    "midi": (time(12, 00), time(12, 15)),
    "soir": (time(19, 00), time(19, 15)),
}

# Plage (en heures) dans laquelle doit commencer un créneau pour être associé à un repas
MEAL_WINDOWS: dict[str, tuple[int, int]] = {
    "matin": (6, 10),
    "midi": (10, 15),
    "soir": (17, 22),
}

MEAL_LABELS: dict[str, str] = {
    "matin": "Petit-déjeuner",
    "midi": "Déjeuner",
    "soir": "Dîner",
}

_RANGE_PATTERN = re.compile(
    r"(\d{1,2})\s*[hH:]\s*(\d{2})?\s*(?:-|–|à|a)\s*(\d{1,2})\s*[hH:]\s*(\d{2})?"
)


def slugify(*args: str) -> str:
    """
    Convertit une ou plusieurs chaînes en slug d'URL (identique au slugify de CROUStillant Web).

    :param args: Les chaînes à convertir.
    :return: Le slug.
    """
    value = unicodedata.normalize("NFD", " ".join(args))
    value = "".join(c for c in value if not unicodedata.combining(c)).lower().strip()
    value = re.sub(r"[^a-z0-9 ]", "", value)
    return re.sub(r"\s+", "-", value)


def parse_meal_slots(horaires: list[str] | None) -> dict[str, tuple[time, time]]:
    """
    Déduit les créneaux des repas à partir des horaires (texte libre) d'un restaurant.

    Le premier créneau dont l'heure de début tombe dans la plage d'un repas est retenu.
    Les créneaux trop longs (ex : « 7h45-17h30 ») sont ignorés car ils correspondent à
    l'ouverture de l'établissement et non à un service.

    :param horaires: Les lignes d'horaires du restaurant.
    :return: Les créneaux de chaque repas.
    """
    slots = dict(DEFAULT_SLOTS)
    found: set[str] = set()

    for line in horaires or []:
        if not isinstance(line, str):
            continue

        for match in _RANGE_PATTERN.finditer(line):
            try:
                start = time(int(match.group(1)), int(match.group(2) or 0))
                end = time(int(match.group(3)), int(match.group(4) or 0))
            except ValueError:
                continue

            duration = (end.hour * 60 + end.minute) - (start.hour * 60 + start.minute)
            if duration <= 0 or duration > 5 * 60:
                continue

            for repas, (low, high) in MEAL_WINDOWS.items():
                if repas not in found and low <= start.hour < high:
                    slots[repas] = (start, end)
                    found.add(repas)
                    break

    return slots


def _escape(text: str) -> str:
    """
    Échappe une valeur texte selon la RFC 5545.

    :param text: Le texte à échapper.
    :return: Le texte échappé.
    """
    return (
        str(text)
        .replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\r\n", "\\n")
        .replace("\n", "\\n")
    )


def _fold(line: str) -> str:
    """
    Replie une ligne de contenu à 75 octets selon la RFC 5545.

    :param line: La ligne à replier.
    :return: La ligne repliée.
    """
    encoded = line.encode("utf-8")
    if len(encoded) <= 75:
        return line

    parts = []
    current = b""
    limit = 75
    for char in line:
        char_bytes = char.encode("utf-8")
        if len(current) + len(char_bytes) > limit:
            parts.append(current.decode("utf-8"))
            current = b""
            limit = 74  # l'espace de continuation compte pour un octet
        current += char_bytes
    parts.append(current.decode("utf-8"))

    return "\r\n ".join(parts)


def _utc(day: date_cls, moment: time) -> str:
    """
    Convertit une date et une heure locales (Europe/Paris) au format UTC iCalendar.

    :param day: La date.
    :param moment: L'heure locale.
    :return: La date au format ``YYYYMMDDTHHMMSSZ``.
    """
    local = PARIS.localize(datetime.combine(day, moment))
    return local.astimezone(utc).strftime("%Y%m%dT%H%M%SZ")


def build_menu_calendar(
    restaurant: dict,
    menus: list[dict],
    meals: list[str] | None = None,
    minimal: bool = False,
) -> str:
    """
    Génère un calendrier iCalendar (RFC 5545) contenant un événement par repas.

    :param restaurant: Le restaurant (ligne de la base de données, horaires déjà décodés).
    :param menus: Les menus structurés (voir ``build_menu_structure``).
    :param meals: Les repas à inclure (matin, midi, soir). Tous par défaut.
    :param minimal: Utilise des créneaux fixes de 15 minutes (``MINIMAL_SLOTS``) au lieu des horaires du restaurant.
    :return: Le contenu du fichier ``.ics``.
    """
    code = restaurant.get("rid")
    nom = restaurant.get("nom") or "Restaurant"
    adresse = restaurant.get("adresse")
    latitude = restaurant.get("latitude")
    longitude = restaurant.get("longitude")
    restaurant_url = f"{WEBSITE_URL}/fr/restaurants/{slugify(nom)}-r{code}"

    slots = MINIMAL_SLOTS if minimal else parse_meal_slots(restaurant.get("horaires"))
    dtstamp = datetime.now(tz=utc).strftime("%Y%m%dT%H%M%SZ")

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//CROUStillant//Menus//FR",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{_escape(f'Menu - {nom}')}",
        f"X-WR-CALDESC:{_escape(f'Menus du restaurant {nom}, fournis par CROUStillant ({WEBSITE_URL})')}",
        "X-WR-TIMEZONE:Europe/Paris",
        "REFRESH-INTERVAL;VALUE=DURATION:PT6H",
        "X-PUBLISHED-TTL:PT6H",
    ]

    for menu in menus:
        day = datetime.strptime(menu["date"], "%d-%m-%Y").date()

        for repas in menu["repas"]:
            type_repas = repas.get("type")
            if type_repas not in slots or (meals and type_repas not in meals):
                continue

            categories = [c for c in repas["categories"] if c["plats"]]
            if not categories:
                continue

            description = []
            for categorie in categories:
                description.append(f"{categorie['libelle']} :")
                description.extend(f"- {plat['libelle']}" for plat in categorie["plats"])
                description.append("")
            description.append(f"Plus d'infos : {restaurant_url}")
            description.append(f"Menu fourni par CROUStillant - {WEBSITE_URL}")

            start, end = slots[type_repas]
            label = MEAL_LABELS.get(type_repas, type_repas.capitalize())

            lines.extend([
                "BEGIN:VEVENT",
                f"UID:{code}-{day.strftime('%Y%m%d')}-{type_repas}@croustillant.menu",
                f"DTSTAMP:{dtstamp}",
                f"DTSTART:{_utc(day, start)}",
                f"DTEND:{_utc(day, end)}",
                f"SUMMARY:{_escape(f'{label} - {nom}')}",
                f"DESCRIPTION:{_escape(chr(10).join(description))}",
                f"URL:{restaurant_url}",
                "TRANSP:TRANSPARENT",
            ])
            if adresse:
                lines.append(f"LOCATION:{_escape(adresse)}")
            if latitude is not None and longitude is not None:
                lines.append(f"GEO:{latitude};{longitude}")
            lines.append("END:VEVENT")

    lines.append("END:VCALENDAR")

    return "\r\n".join(_fold(line) for line in lines) + "\r\n"


def calendar_start_date(days_back: int = 14) -> datetime:
    """
    Date à partir de laquelle les menus sont inclus dans le calendrier.

    Les menus des jours précédents sont conservés pour que les événements passés
    ne disparaissent pas des agendas abonnés.

    :param days_back: Nombre de jours passés à inclure.
    :return: La date de début.
    """
    today = datetime.now(tz=PARIS).replace(hour=0, minute=0, second=0, microsecond=0)
    return today - timedelta(days=days_back)


async def restaurantMenuCalendar(
    request: Request,
    code: int,
    meals: list[str] | None = None,
    minimal: bool = False,
) -> HTTPResponse:
    """
    Retourne la réponse HTTP contenant le calendrier iCalendar des menus d'un restaurant.

    :param request: La requête
    :param code: ID du restaurant
    :param meals: Repas à inclure (matin, midi, soir). Tous par défaut.
    :param minimal: Utilise des créneaux fixes de 15 minutes
    :return: Le fichier .ics, ou une erreur 404 si le restaurant n'existe pas
    """
    restaurant = await request.app.ctx.entities.restaurants.getOne(code)

    if restaurant is None:
        return JSON(
            request=request,
            success=False,
            message="Le restaurant n'existe pas.",
            status=404,
        ).generate()

    restaurant = dict(restaurant)
    try:
        restaurant["horaires"] = (
            loads(restaurant["horaires"]) if restaurant.get("horaires") else None
        )
    except Exception:
        restaurant["horaires"] = None

    menu = await request.app.ctx.entities.menus.getCurrent(
        id=code, date=calendar_start_date()
    )
    menus = list(build_menu_structure(menu).values()) if menu else []

    content = build_menu_calendar(restaurant, menus, meals=meals, minimal=minimal)

    return raw(
        body=content.encode("utf-8"),
        status=200,
        content_type="text/calendar; charset=utf-8",
    )
