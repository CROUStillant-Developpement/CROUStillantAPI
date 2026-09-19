from ..utils.date import getCleanDate
from ..utils.image import addCorners, loadAsset, loadAssetResized
from ..utils.text import Text, splitText, shorten_px_cached, split_px_cached
from ..utils.fonts import make_font
from ..utils.weights import Weights
from PIL import Image, ImageDraw
from textwrap import shorten
from datetime import datetime
from functools import lru_cache
from json import loads
from io import BytesIO


def _menu_key(menu: dict) -> tuple:
    """
    Réduit un menu aux seuls libellés qui influencent la mise en page.

    Sert de clé de cache : deux menus de même contenu textuel produisent
    exactement la même mise en page (voir _select_menu_layout).

    :param menu: Menu du restaurant universitaire.
    :type menu: dict
    :return: Les catégories et leurs plats, sous forme de tuples.
    :rtype: tuple
    """
    return tuple(
        (
            (category.get("libelle") or "").strip(),
            tuple(
                (dish.get("libelle") or "").strip()
                for dish in category.get("plats", [])
                if (dish.get("libelle") or "").strip()
            ),
        )
        for category in (menu.get("categories", []) if menu else [])
    )


def _build_menu_entries(menu: tuple, title_font: tuple, dish_font: tuple, col_max_px: int) -> list[dict]:
    """
    Build drawable menu entries with wrapped text lines.

    Les polices sont passées sous forme (taille, poids) : les raccourcis et
    découpages de libellés sont mémoïsés sur ces valeurs (voir
    shorten_px_cached / split_px_cached), et donc réutilisés d'une requête à
    l'autre.

    :param menu: Menu réduit à ses libellés (voir _menu_key).
    :type menu: tuple
    :param title_font: (taille, poids) de la police des titres de catégories.
    :param dish_font: (taille, poids) de la police des plats.
    :param col_max_px: Largeur maximale en pixels d'une colonne.
    :type col_max_px: int
    :return: Liste d'entrées de menu formatées pour le dessin.
    :rtype: list[dict]
    """
    entries: list[dict] = []
    bullet_w = int(make_font(*dish_font).getlength("• "))

    for category_label, dishes in menu:
        if category_label:
            entries.append(
                {
                    "type": "category",
                    "text": shorten_px_cached(category_label, *title_font, col_max_px),
                }
            )

        for dish_label in dishes:
            lines = split_px_cached(dish_label, *dish_font, col_max_px - bullet_w)
            if not lines:
                continue

            for index, line in enumerate(lines):
                entries.append(
                    {
                        "type": "dish",
                        "text": f"• {line}" if index == 0 else f"   {line}",
                    }
                )

        entries.append({"type": "gap"})

    return entries


def _fits_two_columns(entries: list[dict], top: int, bottom: int, sizes: dict) -> bool:
    """
    Return True when all menu entries fit in two columns for a given layout.

    :param entries: Liste d'entrées de menu formatées pour le dessin.
    :type entries: list[dict]
    :param top: Position y du haut de la zone de contenu.
    :type top: int
    :param bottom: Position y du bas de la zone de contenu.
    :type bottom: int
    :param sizes: Tailles et espacements du layout à tester.
    :type sizes: dict
    :return: True si les entrées tiennent dans deux colonnes, sinon False.
    :rtype: bool
    """
    y = top
    column = 1

    for entry in entries:
        if entry["type"] == "category":
            height = sizes["category_step"]
        elif entry["type"] == "dish":
            height = sizes["dish_step"]
        else:
            height = sizes["gap_step"]

        if y + height > bottom:
            if column == 1:
                column = 2
                y = top
            else:
                return False

        y += height

    return True


def _make_fonts(title_size: int, dish_size: int) -> tuple[tuple, tuple]:
    return (
        (title_size, Weights.EXTRA_BOLD.value),
        (dish_size, Weights.MEDIUM.value),
    )


@lru_cache(maxsize=512)
def _select_menu_layout(menu: tuple, top: int, bottom: int, col_max_px: int) -> dict:
    """
    Pick the biggest readable layout that still fits all categories and dishes.

    Mémoïsé sur le contenu textuel du menu (voir _menu_key) : c'est l'étape la
    plus coûteuse (mesures de texte pour chaque taille candidate), et elle est
    identique pour toutes les requêtes d'un même menu, quels que soient le
    thème et le restaurant. Le résultat est partagé : ne pas le modifier.

    :param menu: Menu réduit à ses libellés (voir _menu_key).
    :type menu: tuple
    :param top: Position y du haut de la zone de contenu.
    :type top: int
    :param bottom: Position y du bas de la zone de contenu.
    :type bottom: int
    :param col_max_px: Largeur maximale en pixels d'une colonne.
    :type col_max_px: int
    :return: Layout choisi avec les tailles et les entrées formatées.
    :rtype: dict
    """
    max_scale = 1.25
    min_scale = 0.45
    step = 0.05

    scales = [
        round(max_scale - i * step, 2)
        for i in range(int(round((max_scale - min_scale) / step)) + 1)
    ]

    def _candidate(scale: float) -> dict:
        title_size = max(16, int(round(40 * scale)))
        dish_size = max(14, int(round(35 * scale)))
        title_font, dish_font = _make_fonts(title_size, dish_size)
        sizes = {
            "title_size": title_size,
            "dish_size": dish_size,
            "category_step": max(22, int(round(50 * scale))),
            "dish_step": max(18, int(round(40 * scale))),
            "gap_step": max(14, int(round(40 * scale))),
        }
        entries = _build_menu_entries(menu, title_font=title_font, dish_font=dish_font, col_max_px=col_max_px)
        return sizes, entries

    lo, hi = 0, len(scales) - 1
    chosen = None

    while lo <= hi:
        mid = (lo + hi) // 2
        sizes, entries = _candidate(scales[mid])
        if _fits_two_columns(entries=entries, top=top, bottom=bottom, sizes=sizes):
            chosen = {"sizes": sizes, "entries": entries}
            hi = mid - 1  # try a larger scale (lower index)
        else:
            lo = mid + 1  # need a smaller scale

    if chosen:
        return chosen

    # Safety fallback for extremely dense menus.
    fallback_title_font, fallback_dish_font = _make_fonts(14, 12)
    fallback_sizes = {
        "title_size": 14,
        "dish_size": 12,
        "category_step": 18,
        "dish_step": 15,
        "gap_step": 12,
    }
    return {
        "sizes": fallback_sizes,
        "entries": _build_menu_entries(
            menu,
            title_font=fallback_title_font,
            dish_font=fallback_dish_font,
            col_max_px=col_max_px,
        ),
    }


def generate(
    restaurant,
    menu,
    date: datetime,
    preview: str,
    theme: str = "light",
    custom_colours: dict = None,
) -> Image:
    """
    Génère une image du menu d'un restaurant universitaire.

    :param restaurant: Restaurant universitaire.
    :param menu: Menu du restaurant universitaire.
    :param date: Date du menu.
    :param preview: Prévisualisation de l'image.
    :param theme: Thème de l'image.
    :param custom_colours: Couleurs personnalisées (header, content, title, infos).
    :return: L'image du menu.
    """

    default_colours = {
        "light": {
            "header": "#000000",
            "content": "#373737",
            "title": "#333333",
            "infos": "#4F4F4F",
        },
        "purple": {
            "header": "#FFFFFF",
            "content": "#F4EEE0",
            "title": "#F4EEE0",
            "infos": "#F4EEE0",
        },
        "dark": {
            "header": "#FFFFFF",
            "content": "#F4EEE0",
            "title": "#F4EEE0",
            "infos": "#F4EEE0",
        },
    }

    # Use custom colours if provided, otherwise use theme colours
    if custom_colours:
        colours = {
            theme: {
                **default_colours.get(theme, default_colours["light"]),
                **custom_colours,
            }
        }
    else:
        colours = default_colours

    # Assets decodes une seule fois par processus (loadAsset) : on dessine sur
    # une copie du fond, les calques partages ne sont que lus.
    image = loadAsset(f"./assets/images/themes/{theme}/background.png").copy()
    drawer = ImageDraw.Draw(image)

    # Titre

    x = 230
    y = 30
    space = 70

    header_1 = Text(size=60, weight=Weights.BOLD)
    header_1.draw(
        drawer=drawer,
        text=shorten(restaurant.get("nom"), width=34, placeholder="..."),
        colour=colours[theme]["header"],
        x=x,
        y=y,
    )

    header_2 = Text(size=45, weight=Weights.BOLD)
    header_2.draw(
        drawer=drawer,
        text=getCleanDate(date),
        colour=colours[theme]["header"],
        x=x,
        y=y + space,
    )

    # Repas

    ## Contenu

    content_x = 92
    content_x2 = 712
    content_top = 215
    content_bottom = 1000  # 960

    if menu:
        img = loadAsset(f"./assets/images/themes/{theme}/square.png")
        image.paste(img, (35, 168), img)
        image.paste(img, (658, 168), img)

        col_max_px = content_x2 - content_x - 80
        layout = _select_menu_layout(
            menu=_menu_key(menu), top=content_top, bottom=content_bottom, col_max_px=col_max_px
        )
        sizes = layout["sizes"]
        entries = layout["entries"]

        title = Text(size=sizes["title_size"], weight=Weights.EXTRA_BOLD)
        text = Text(size=sizes["dish_size"], weight=Weights.MEDIUM)

        content_y = content_top
        content_column_x = content_x

        for entry in entries:
            if entry["type"] == "category":
                height = sizes["category_step"]
            elif entry["type"] == "dish":
                height = sizes["dish_step"]
            else:
                height = sizes["gap_step"]

            if content_y + height > content_bottom:
                content_column_x = content_x2
                content_y = content_top

            if entry["type"] == "category":
                title.draw(
                    drawer=drawer,
                    text=entry["text"],
                    colour=colours[theme]["content"],
                    x=content_column_x,
                    y=content_y,
                )
            elif entry["type"] == "dish":
                text.draw(
                    drawer=drawer,
                    text=entry["text"],
                    colour=colours[theme]["content"],
                    x=content_column_x,
                    y=content_y,
                )

            content_y += height
    else:
        img = loadAsset(f"./assets/images/themes/{theme}/none.png")
        image.paste(img, (35, 168), img)

        m = "Menu non disponible."
        code = 404

        x = 62
        y = 543

        text = Text(size=50, weight=Weights.EXTRA_BOLD_ITALIC)
        x = (1200 - drawer.textlength(text=m, font=text.font)) / 2 + 50
        text.draw(drawer=drawer, text=m, colour=colours[theme]["title"], x=x, y=y)

        x = 525
        y = 624

        text = Text(size=50, weight=Weights.MEDIUM_ITALIC)
        text.draw(
            drawer=drawer,
            text=f"Erreur {code}",
            colour=colours[theme]["title"],
            x=x,
            y=y,
        )

    # Infos

    ## Image

    if preview:
        img = addCorners(Image.open(BytesIO(preview)).resize((462, 295)), 20)
    else:
        img = loadAssetResized("./assets/images/default_ru.png", (462, 295), radius=20)

    image.paste(img, (1366, 51), img)

    ## Repas

    if menu:
        if menu["type"] == "matin":
            rID = 1
        elif menu["type"] == "midi":
            rID = 2
        elif menu["type"] == "soir":
            rID = 3

        img = loadAssetResized(f"./assets/images/layers/repas-{rID}.png", (100, 100))
        image.paste(img, (1723, 56), img)

    ## Titre

    x = 1475
    y = 390
    y_space = 113

    titles = Text(size=35, weight=Weights.BOLD)

    if restaurant.get("opened"):
        titles.draw(
            drawer=drawer, text="Ouvert !", colour=colours[theme]["title"], x=x, y=y
        )
    else:
        titles.draw(
            drawer=drawer, text="Fermé !", colour=colours[theme]["title"], x=x, y=y
        )

    titles.draw(
        drawer=drawer,
        text="Contact",
        colour=colours[theme]["title"],
        x=x,
        y=y + y_space,
    )
    titles.draw(
        drawer=drawer,
        text="Paiements",
        colour=colours[theme]["title"],
        x=x,
        y=y + y_space * 2,
    )
    titles.draw(
        drawer=drawer,
        text="Localisation",
        colour=colours[theme]["title"],
        x=x,
        y=y + y_space * 3,
    )
    titles.draw(
        drawer=drawer,
        text="Accès",
        colour=colours[theme]["title"],
        x=x,
        y=y + y_space * 4,
    )

    ## Contenu

    x = 1475
    y = 433
    y_space = 113
    space = 25
    short = 34

    text = Text(size=20, weight=Weights.SEMI_BOLD)
    if restaurant.get("opened"):
        if restaurant.get("horaires"):
            horaires = loads(restaurant.get("horaires"))
        else:
            horaires = None

        if horaires:
            t = splitText(horaires[0], 36)

            if len(t) > 1 and not len(horaires) > 0:
                text.draw(
                    drawer=drawer,
                    text=f"• {t[0]}",
                    colour=colours[theme]["infos"],
                    x=x,
                    y=y,
                )

                if len(t) > 2:
                    text.draw(
                        drawer=drawer,
                        text=f"   {t[1][0:33] + '...'}",
                        colour=colours[theme]["infos"],
                        x=x,
                        y=y + space,
                    )
                else:
                    text.draw(
                        drawer=drawer,
                        text=f"   {t[1]}",
                        colour=colours[theme]["infos"],
                        x=x,
                        y=y + space,
                    )
            else:
                text.draw(
                    drawer=drawer,
                    text=f"• {shorten(horaires[0], width=short, placeholder='...')}",
                    colour=colours[theme]["infos"],
                    x=x,
                    y=y,
                )

            if horaires and len(horaires) > 1:
                text.draw(
                    drawer=drawer,
                    text=f"• {shorten(horaires[1], width=short, placeholder='...')}",
                    colour=colours[theme]["infos"],
                    x=x,
                    y=y + space,
                )
        else:
            text.draw(
                drawer=drawer,
                text="• Aucune information disponible.",
                colour=colours[theme]["infos"],
                x=x,
                y=y,
            )

    if restaurant.get("email"):
        text.draw(
            drawer=drawer,
            text=f"• {shorten('Email : ' + restaurant.get('email'), width=short, placeholder='...')}",
            colour=colours[theme]["infos"],
            x=x,
            y=y + y_space,
        )

        if restaurant.get("telephone"):
            text.draw(
                drawer=drawer,
                text=f"• Téléphone : {restaurant.get('telephone')}",
                colour=colours[theme]["infos"],
                x=x,
                y=y + y_space + space,
            )
    else:
        if restaurant.get("telephone"):
            text.draw(
                drawer=drawer,
                text=f"• Téléphone : {restaurant.get('telephone')}",
                colour=colours[theme]["infos"],
                x=x,
                y=y + y_space,
            )

    if not restaurant.get("email") and not restaurant.get("telephone"):
        text.draw(
            drawer=drawer,
            text="• Aucune information disponible.",
            colour=colours[theme]["infos"],
            x=x,
            y=y + y_space,
        )

    if restaurant.get("paiement"):
        paiement = loads(restaurant.get("paiement"))
        if paiement:
            text.draw(
                drawer=drawer,
                text=f"• {paiement[0]}",
                colour=colours[theme]["infos"],
                x=x,
                y=y + y_space * 2,
            )

        if paiement and len(paiement) > 1:
            text.draw(
                drawer=drawer,
                text=f"• {paiement[1]}",
                colour=colours[theme]["infos"],
                x=x,
                y=y + y_space * 2 + space,
            )
    else:
        text.draw(
            drawer=drawer,
            text="• Aucune information disponible.",
            colour=colours[theme]["infos"],
            x=x,
            y=y + y_space * 2,
        )

    text.draw(
        drawer=drawer,
        text=f"• {shorten(restaurant.get('zone'), width=short, placeholder='...')}",
        colour=colours[theme]["infos"],
        x=x,
        y=y + y_space * 3,
    )

    if restaurant.get("adresse"):
        text.draw(
            drawer=drawer,
            text=f"• {shorten(restaurant.get('adresse'), width=short, placeholder='...')}",
            colour=colours[theme]["infos"],
            x=x,
            y=y + y_space * 3 + space,
        )

    if restaurant.get("acces"):
        acces = loads(restaurant.get("acces"))
    else:
        acces = None

    if restaurant.get("pmr"):
        text.draw(
            drawer=drawer,
            text="• Accessible aux PMR",
            colour=colours[theme]["infos"],
            x=x,
            y=y + y_space * 4,
        )

        if acces:
            text.draw(
                drawer=drawer,
                text=f"• {shorten(acces[0], width=short, placeholder='...')}",
                colour=colours[theme]["infos"],
                x=x,
                y=y + y_space * 4 + space,
            )
    else:
        if acces:
            if len(acces) >= 2:
                text.draw(
                    drawer=drawer,
                    text=f"• {shorten(acces[0], width=short, placeholder='...')}",
                    colour=colours[theme]["infos"],
                    x=x,
                    y=y + y_space * 4,
                )

                if acces[1]:
                    text.draw(
                        drawer=drawer,
                        text=f"• {shorten(acces[1], width=short, placeholder='...')}",
                        colour=colours[theme]["infos"],
                        x=x,
                        y=y + y_space * 4 + space,
                    )
            else:
                text.draw(
                    drawer=drawer,
                    text=f"• {shorten(acces[0], width=short, placeholder='...')}",
                    colour=colours[theme]["infos"],
                    x=x,
                    y=y + y_space * 4,
                )
        else:
            text.draw(
                drawer=drawer,
                text="• Aucune information disponible.",
                colour=colours[theme]["infos"],
                x=x,
                y=y + y_space * 4,
            )

    return image

    # Conversion en RGBA pour la transparence des coins
    # return image.convert("RGBA")
