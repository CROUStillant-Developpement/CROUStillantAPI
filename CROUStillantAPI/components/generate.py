from ..utils.date import getCleanDate
from ..utils.image import addCorners, download
from ..utils.text import Text, splitText
from ..utils.weights import Weights
from PIL import Image, ImageDraw
from textwrap import shorten
from aiohttp import ClientSession
from datetime import datetime
from json import loads
from asyncio import run


def generate(restaurant, menu, date: datetime, theme: str = "light") -> Image:
    """
    Génère une image du menu d'un restaurant universitaire.

    :param restaurant: Restaurant universitaire.
    :param menu: Menu du restaurant universitaire.
    :param date: Date du menu.
    :param theme: Thème de l'image.
    :return: L'image du menu.
    """

    colours = {
        "light": {
            "header": "#000000",
            "content": "#373737",
            "title": "#333333",
            "infos": "#4F4F4F"
        },
        "purple": {
            "header": "#FFFFFF",
            "content": "#F4EEE0",
            "title": "#F4EEE0",
            "infos": "#F4EEE0"
        },
        "dark": {
            "header": "#FFFFFF",
            "content": "#F4EEE0",
            "title": "#F4EEE0",
            "infos": "#F4EEE0"
        }
    }


    image = Image.open(f'./assets/images/themes/{theme}/background.png')
    drawer = ImageDraw.Draw(image)


    # Titre

    x = 230
    y = 30
    space = 70

    header_1 = Text(size=60, weight=Weights.BOLD)
    header_1.draw(drawer=drawer, text=shorten(restaurant.get("nom"), width=34, placeholder='...'), colour=colours[theme]['header'], x=x, y=y)

    header_2 = Text(size=45, weight=Weights.BOLD)
    header_2.draw(drawer=drawer, text=getCleanDate(date), colour=colours[theme]['header'], x=x, y=y+space)


    # Repas

    ## Contenu

    content_x = 92
    content_x2 = 712
    content_y = 215
    content_y_save = content_y
    content_y_space = 40
    content_space = 50
    content_h_space = 40

    title = Text(size=40, weight=Weights.EXTRA_BOLD)
    text = Text(size=35, weight=Weights.MEDIUM)
    small = Text(size=30, weight=Weights.BOLD_ITALIC)

    if menu:
        img = Image.open(f'./assets/images/themes/{theme}/square.png')
        image.paste(img, (35, 168), img)
        image.paste(img, (658, 168), img)

        stop = False
        moved = False
        count = 0
        for category in menu["categories"]:
            if content_y >= 930 and not moved:
                moved = True
                content_x = content_x2
                content_y = content_y_save
            elif content_y >= 930 and moved:
                total = len([d for c in menu for d in c if d != "" and d != " "])

                if total - count > 0:
                    small.draw(drawer=drawer, text=f"+ {total-count} autres plats non affichés...", colour=colours[theme]['content'], x=content_x, y=content_y)

                stop = True
                break

            title.draw(drawer=drawer, text=shorten(category.get("libelle"), width=25, placeholder='...'), colour=colours[theme]['content'], x=content_x, y=content_y)

            content_y += content_space

            for dish in category["plats"]:
                count += 1
                if dish.get("libelle") != "" and dish.get("libelle") != " " and not (content_y >= 940 and moved):

                    dish_list = splitText(dish.get("libelle"), 27)
                    if len(dish_list) == 1:
                        text.draw(drawer=drawer, text=f"• {dish_list[0]}", colour=colours[theme]['content'], x=content_x, y=content_y)
                    else:
                        if not moved and content_y >= 920:
                            moved = True
                            content_x = content_x2
                            content_y = content_y_save

                        text.draw(drawer=drawer, text=f"• {dish_list[0]}", colour=colours[theme]['content'], x=content_x, y=content_y)
                        content_y += content_y_space
                        text.draw(drawer=drawer, text=f"   {shorten(dish_list[1], width=25, placeholder='')}...", colour=colours[theme]['content'], x=content_x, y=content_y)

                    content_y += content_y_space

                    if moved and content_y >= 930:
                        total = len([d for c in menu for d in c if d != "" and d != " "])

                        if total - count > 0:
                            small.draw(drawer=drawer, text=f"+ {total-count} autres plat{'s' if total-count>1 else ''} non affiché{'s' if total-count>1 else ''}...", colour=colours[theme]['content'], x=content_x, y=content_y)

                        stop = True
                        break
                    elif not moved and content_y >= 995:
                        moved = True
                        content_x = content_x2
                        content_y = content_y_save

            if moved and content_y == content_y_save:
                pass
            else:
                content_y += content_h_space

            if moved and content_y >= 940:
                if not stop:
                    total = len([d for c in menu for d in c if d != "" and d != " "])

                    if total - count > 0:
                        small.draw(drawer=drawer, text=f"+ {total-count} autres plat{'s' if total-count>1 else ''} non affiché{'s' if total-count>1 else ''}...", colour=colours[theme]['content'], x=content_x, y=content_y)
                break
            elif content_y >= 995:
                moved = True
                content_x = content_x2
                content_y = content_y_save
    else:
        img = Image.open(f'./assets/images/themes/{theme}/none.png')
        image.paste(img, (35, 168), img)

        m = "Menu non disponible."
        code = 404

        x = 62
        y = 543

        text = Text(size=50, weight=Weights.EXTRA_BOLD_ITALIC)
        x = (1200 - drawer.textlength(text=m, font=text.font)) / 2 + 50
        text.draw(drawer=drawer, text=m, colour=colours[theme]['title'], x=x, y=y)


        x = 525
        y = 624

        text = Text(size=50, weight=Weights.MEDIUM_ITALIC)
        text.draw(drawer=drawer, text=f"Erreur {code}", colour=colours[theme]['title'], x=x, y=y)


    # Infos

    ## Image

    try:
        async def getImage():
            async with ClientSession() as session:
                return await download(restaurant.get("image_url"), session=session)

        img = run(getImage())
    except:
        img = Image.open("./assets/images/default_ru.png")

    img = img.resize((462, 295))
    img = addCorners(img, 20)
    image.paste(img, (1366, 51), img)


    ## Repas

    if menu:
        if menu["type"] == "matin":
            rID = 1
        elif menu["type"] == "midi":
            rID = 2
        elif menu["type"] == "soir":
            rID = 3

        img = Image.open(f'./assets/images/layers/repas-{rID}.png')
        img = img.resize((100, 100))
        image.paste(img, (1723, 56), img)


    ## Titre

    x = 1475
    y = 390
    y_space = 113

    titles = Text(size=35, weight=Weights.BOLD)

    if restaurant.get("opened"):
        titles.draw(drawer=drawer, text="Ouvert !", colour=colours[theme]['title'], x=x, y=y)
    else:
        titles.draw(drawer=drawer, text="Fermé !", colour=colours[theme]['title'], x=x, y=y)

    titles.draw(drawer=drawer, text="Contact", colour=colours[theme]['title'], x=x, y=y+y_space)
    titles.draw(drawer=drawer, text="Paiements", colour=colours[theme]['title'], x=x, y=y+y_space*2)
    titles.draw(drawer=drawer, text="Localisation", colour=colours[theme]['title'], x=x, y=y+y_space*3)
    titles.draw(drawer=drawer, text="Accès", colour=colours[theme]['title'], x=x, y=y+y_space*4)


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
                text.draw(drawer=drawer, text=f"• {t[0]}", colour=colours[theme]['infos'], x=x, y=y)

                if len(t) > 2:
                    text.draw(drawer=drawer, text=f"   {t[1][0:33]+'...'}", colour=colours[theme]['infos'], x=x, y=y+space)
                else:
                    text.draw(drawer=drawer, text=f"   {t[1]}", colour=colours[theme]['infos'], x=x, y=y+space)
            else:
                text.draw(drawer=drawer, text=f"• {shorten(horaires[0], width=short, placeholder='...')}", colour=colours[theme]['infos'], x=x, y=y)

            if horaires and len(horaires) > 1:
                text.draw(drawer=drawer, text=f"• {shorten(horaires[1], width=short, placeholder='...')}", colour=colours[theme]['infos'], x=x, y=y+space)
        else:
            text.draw(drawer=drawer, text="• Aucune information disponible.", colour=colours[theme]['infos'], x=x, y=y)
    

    if restaurant.get("email"):
        text.draw(drawer=drawer, text=f"• {shorten('Email : ' + restaurant.get('email'), width=short, placeholder='...')}", colour=colours[theme]['infos'], x=x, y=y+y_space)

        if restaurant.get("telephone"):
            text.draw(drawer=drawer, text=f"• Téléphone : {restaurant.get('telephone')}", colour=colours[theme]['infos'], x=x, y=y+y_space+space)
    else:
        if restaurant.get("telephone"):
            text.draw(drawer=drawer, text=f"• Téléphone : {restaurant.get('telephone')}", colour=colours[theme]['infos'], x=x, y=y+y_space)

    if not restaurant.get("email") and not restaurant.get("telephone"):
        text.draw(drawer=drawer, text="• Aucune information disponible.", colour=colours[theme]['infos'], x=x, y=y+y_space)


    if restaurant.get("paiement"):
        paiement = loads(restaurant.get("paiement"))
        if paiement:
            text.draw(drawer=drawer, text=f"• {paiement[0]}", colour=colours[theme]['infos'], x=x, y=y+y_space*2)

        if paiement and len(paiement) > 1:
            text.draw(drawer=drawer, text=f"• {paiement[1]}", colour=colours[theme]['infos'], x=x, y=y+y_space*2+space)
    else:
        text.draw(drawer=drawer, text="• Aucune information disponible.", colour=colours[theme]['infos'], x=x, y=y+y_space*2)


    text.draw(drawer=drawer, text=f"• {shorten(restaurant.get('zone'), width=short, placeholder='...')}", colour=colours[theme]['infos'], x=x, y=y+y_space*3)

    if restaurant.get("adresse"):
        text.draw(drawer=drawer, text=f"• {shorten(restaurant.get('adresse'), width=short, placeholder='...')}", colour=colours[theme]['infos'], x=x, y=y+y_space*3+space)


    if restaurant.get("acces"):
        acces = loads(restaurant.get("acces"))
    else:
        acces = None

    if restaurant.get("pmr"):
        text.draw(drawer=drawer, text="• Accessible aux PMR", colour=colours[theme]['infos'], x=x, y=y+y_space*4)

        if acces:
            text.draw(drawer=drawer, text=f"• {shorten(acces[0], width=short, placeholder='...')}", colour=colours[theme]['infos'], x=x, y=y+y_space*4+space)
    else:
        if acces:
            if len(acces) >= 2:
                text.draw(drawer=drawer, text=f"• {shorten(acces[0], width=short, placeholder='...')}", colour=colours[theme]['infos'], x=x, y=y+y_space*4)

                if acces[1]:
                    text.draw(drawer=drawer, text=f"• {shorten(acces[1], width=short, placeholder='...')}", colour=colours[theme]['infos'], x=x, y=y+y_space*4+space)
            else:
                text.draw(drawer=drawer, text=f"• {shorten(acces[0], width=short, placeholder='...')}", colour=colours[theme]['infos'], x=x, y=y+y_space*4)
        else:
            text.draw(drawer=drawer, text="• Aucune information disponible.", colour=colours[theme]['infos'], x=x, y=y+y_space*4)


    # Conversion en RGBA pour la transparence des coins
    return image.convert("RGBA")
