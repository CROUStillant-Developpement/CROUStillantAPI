from .weights import Weights
from PIL import ImageFont, ImageDraw


class Text:
    def __init__(self, size: int, weight: Weights = Weights.REGULAR) -> None:
        """
          /$$$$$$$$ /$$$$$$$$ /$$   /$$ /$$$$$$$$\n
         |__  $$__/| $$_____/| $$  / $$|__  $$__/\n
            | $$   | $$      |  $$/ $$/   | $$   \n
            | $$   | $$$$$    \  $$$$/    | $$   \n
            | $$   | $$__/     >$$  $$    | $$   \n
            | $$   | $$       /$$/\  $$   | $$   \n
            | $$   | $$$$$$$$| $$  \ $$   | $$   \n
            |__/   |________/|__/  |__/   |__/   \n
                                                 \n

        :param size: Taille du texte
        :param weight: Poids du texte
        """
        if not isinstance(weight, Weights):
            raise TypeError(f"weight doit être de type Weights, pas {weight.__class__.__name__}")

        self.size = size
        self.weight = weight.value

        self.font = ImageFont.truetype("./assets/fonts/Inter-VariableFont.ttf", self.size)
        self.font.set_variation_by_name(self.weight)


    def draw(self, drawer: ImageDraw, text: str, colour: str, x: int, y: int) -> None:
        """
        Dessine un texte sur une image.

        :param drawer: ImageDraw
        :param text: Texte à dessiner
        :param colour: Couleur du texte
        :param x: Position X du texte
        :param y: Position Y du texte
        """
        drawer.text((x, y), text, fill=colour, font=self.font)


def splitText(text: str, maximum: int) -> list:
    """
    Sépare un texte en plusieurs lignes en fonction d'une taille maximale.

    :param text: Texte à séparer.
    :type text: str

    :param maximum: Taille maximale d'une ligne.
    :type maximum: int

    :return: Liste des lignes.
    :rtype: list
    """
    words = text.split()
    char = " "

    if "http" in text.lower():
        words = text.lower().replace("http://", "").replace("https://", "").split("/")
        char = "/"

    lines = []
    line = words[0] + char

    for word in words[1:]:
        if len(line) + len(word) + 1 <= maximum:
            line += char + word
        else:
            lines.append(clean(line))
            line = word

    # On ajoute la dernière ligne et on supprime les doubles espaces
    lines.append(clean(line))
    return lines


def clean(text: str) -> str:
    """
    Formatte une chaîne de charactères 

    :param: Texte à formatter
    :type: str

    :return: Texte formatté
    :rtype: str
    """
    formats = {
        "   "  : " ",
        "  "   : " ",
        "   )" : ")",
        "  )"  : ")",
        "   (" : " (",
        "  ("  : " (",
        "   :" : " :",
        "  :"  : " :",
        "   ," : ",",
        "  ,"  : ",",
        "( "   : "(",
        " )"   : ")",
        " ,"   : ",",
        " €"   : "€"
    }

    for format in formats:
        text = text.replace(format, formats[format])

    return text.strip()
