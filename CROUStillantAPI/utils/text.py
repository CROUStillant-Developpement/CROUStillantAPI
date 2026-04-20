from .weights import Weights
from .fonts import make_font
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
            raise TypeError(
                f"weight doit être de type Weights, pas {weight.__class__.__name__}"
            )

        self.size = size
        self.weight = weight.value

        self.font = make_font(self.size, self.weight)

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


def shorten_px(text: str, font, max_width: int, placeholder: str = "...") -> str:
    """
    Truncate *text* so its rendered pixel width fits within *max_width*,
    appending *placeholder* when truncation occurs.
    """
    if font.getlength(text) <= max_width:
        return text
    placeholder_width = font.getlength(placeholder)
    result = ""
    for char in text:
        if font.getlength(result + char) + placeholder_width > max_width:
            break
        result += char
    return result.rstrip() + placeholder


def split_px(text: str, font, max_width: int) -> list[str]:
    """
    Split *text* into lines whose rendered pixel width stays within *max_width*.
    Splits on spaces when possible; force-splits within a word if it alone is
    wider than *max_width*.
    """
    words = text.split()
    lines = []
    line = ""

    for word in words:
        candidate = (line + " " + word).strip()
        if font.getlength(candidate) <= max_width:
            line = candidate
        else:
            if line:
                lines.append(clean(line))
            if font.getlength(word) > max_width:
                current = ""
                for char in word:
                    if font.getlength(current + char) > max_width:
                        lines.append(clean(current))
                        current = char
                    else:
                        current += char
                line = current
            else:
                line = word

    if line:
        lines.append(clean(line))
    return lines


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
    Formatte une chaîne de caractères en supprimant les doubles espaces et les espaces avant les parenthèses, les deux points et les virgules.

    :param: Texte à formatter
    :type: str

    :return: Texte formatté
    :rtype: str
    """
    formats = {
        "   ": " ",
        "  ": " ",
        "   )": ")",
        "  )": ")",
        "   (": " (",
        "  (": " (",
        "   :": " :",
        "  :": " :",
        "   ,": ",",
        "  ,": ",",
        "( ": "(",
        " )": ")",
        " ,": ",",
        " €": "€",
    }

    for format in formats:
        text = text.replace(format, formats[format])

    return text.strip()
