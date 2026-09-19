from functools import lru_cache
from io import BytesIO
from PIL import Image, ImageDraw


@lru_cache(maxsize=None)
def loadAsset(path: str) -> Image.Image:
    """
    Charge et decode une image des assets une seule fois par processus.

    L'image retournee est partagee entre les requetes (et les threads) : elle
    ne doit jamais etre modifiee. Pour dessiner dessus, travailler sur une
    copie (``loadAsset(path).copy()``).

    :param path: Chemin de l'image
    :return: L'image decodee
    """
    image = Image.open(path)
    image.load()
    return image


@lru_cache(maxsize=None)
def loadAssetResized(path: str, size: tuple[int, int], radius: int = 0) -> Image.Image:
    """
    Charge une image des assets deja redimensionnee (et arrondie si besoin),
    une seule fois par processus. Meme regle que loadAsset : ne pas modifier.

    :param path: Chemin de l'image
    :param size: Taille (largeur, hauteur)
    :param radius: Rayon des coins arrondis (0 : aucun)
    :return: L'image transformee
    """
    image = loadAsset(path).resize(size)
    if radius:
        image = addCorners(image, radius)
    return image


def addCorners(image: Image, radius: int):
    """
    Ajoute des coins arrondis à une image.

    :param image: Image à modifier.
    :type image: Image

    :param radius: Rayon des coins.
    :type radius: int

    :return: Image modifiée.
    :rtype: Image
    """
    mask = Image.new("L", image.size, 255)
    corner = Image.new("L", (radius * 2, radius * 2), 0)
    draw = ImageDraw.Draw(corner)
    draw.ellipse((0, 0, radius * 2, radius * 2), fill=255)

    mask.paste(corner.crop((0, 0, radius, radius)), (0, 0))
    mask.paste(
        corner.crop((0, radius, radius, radius * 2)), (0, image.size[1] - radius)
    )
    mask.paste(
        corner.crop((radius, 0, radius * 2, radius)), (image.size[0] - radius, 0)
    )
    mask.paste(
        corner.crop((radius, radius, radius * 2, radius * 2)),
        (image.size[0] - radius, image.size[1] - radius),
    )

    image.putalpha(mask)
    return image


def saveImageToBuffer(image: Image, compression_level: int = 3) -> BytesIO:
    """
    Sauvegarde une image dans un buffer avec un niveau de compression spécifié.

    Niveau 3 par défaut : avec zlib-ng (Pillow 12), il réduit une image de menu
    d'environ un tiers par rapport au niveau 1 pour quelques millisecondes de
    plus ; au-delà, le gain de taille est faible et le coût double.

    :param image: PIL Image object.
    :param compression_level: Compression level (0-9).
    :return: BytesIO object.
    """
    buffer = BytesIO()
    image.save(buffer, format="PNG", compress_level=compression_level)
    buffer.seek(0)
    return buffer
