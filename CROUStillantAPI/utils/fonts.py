from PIL import ImageFont
from collections import OrderedDict
from threading import local

_FONT_PATH = "./assets/fonts/Inter-VariableFont.ttf"

# Nombre maximal de polices gardees en cache PAR THREAD. Une image de menu
# utilise ~15 couples (taille, poids) ; au-dela, les moins recemment utilises
# sont liberes. Chaque police coute ~0,5 Mo (tables de variation de la police
# Inter chargees par FreeType).
_CACHE_SIZE = 24

# Cache par thread : un objet FreeTypeFont ne doit pas etre utilise par
# plusieurs threads a la fois (la generation d'images tourne dans le
# ThreadPoolExecutor de l'application).
_local = local()


def make_font(size: int, weight_name: str) -> ImageFont.FreeTypeFont:
    """
    Retourne la police Inter a la taille et au poids demandes.

    Les polices sont mises en cache par thread : les recreer a chaque appel
    coutait le chargement de la police variable et, surtout, repartait d'un
    cache de glyphes FreeType vide (mesure de texte ~10 fois plus lente).

    :param size: Taille de la police
    :param weight_name: Nom de la variation (voir Weights)
    :return: La police
    """
    cache: OrderedDict | None = getattr(_local, "fonts", None)
    if cache is None:
        cache = _local.fonts = OrderedDict()

    key = (size, weight_name)
    font = cache.get(key)

    if font is None:
        # Chargement par chemin (et non via BytesIO) : FreeType lit le fichier
        # lui-meme, sans garder une copie des 785 Ko par police.
        font = ImageFont.truetype(_FONT_PATH, size)
        font.set_variation_by_name(weight_name)
        cache[key] = font

        if len(cache) > _CACHE_SIZE:
            cache.popitem(last=False)
    else:
        cache.move_to_end(key)

    return font
