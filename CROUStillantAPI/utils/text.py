from .weights import Weights
from .fonts import make_font
from PIL import ImageFont, ImageDraw
from functools import lru_cache


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

    Le plus long prefixe qui tient est trouve par dichotomie (~log2(n) mesures
    au lieu d'une mesure par caractere) : la largeur d'un prefixe croit avec
    sa longueur.
    """
    if font.getlength(text) <= max_width:
        return text
    placeholder_width = font.getlength(placeholder)

    # Plus grand k tel que text[:k] + placeholder tient (text[:0] tient toujours)
    lo, hi = 0, len(text) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if font.getlength(text[:mid]) + placeholder_width > max_width:
            hi = mid - 1
        else:
            lo = mid
    return text[:lo].rstrip() + placeholder


@lru_cache(maxsize=8192)
def shorten_px_cached(text: str, size: int, weight: str, max_width: int, placeholder: str = "...") -> str:
    """
    shorten_px memoise, pour la police Inter (size, weight).

    Le resultat ne depend que de ces parametres : il est reutilise d'une
    requete a l'autre (les memes libelles reviennent pour chaque theme, repas
    et jour), sans aucune mesure de texte.
    """
    return shorten_px(text, make_font(size, weight), max_width, placeholder)


@lru_cache(maxsize=8192)
def split_px_cached(text: str, size: int, weight: str, max_width: int) -> tuple[str, ...]:
    """
    split_px memoise, pour la police Inter (size, weight). Voir shorten_px_cached.
    """
    return tuple(split_px(text, make_font(size, weight), max_width))


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
