from io import BytesIO
from PIL import Image, ImageDraw


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
    mask = Image.new('L', image.size, 255)
    corner = Image.new('L', (radius * 2, radius * 2), 0)
    draw = ImageDraw.Draw(corner)
    draw.ellipse((0, 0, radius * 2, radius * 2), fill=255)
    
    mask.paste(corner.crop((0, 0, radius, radius)), (0, 0))
    mask.paste(corner.crop((0, radius, radius, radius * 2)), (0, image.size[1] - radius))
    mask.paste(corner.crop((radius, 0, radius * 2, radius)), (image.size[0] - radius, 0))
    mask.paste(corner.crop((radius, radius, radius * 2, radius * 2)), (image.size[0] - radius, image.size[1] - radius))

    image.putalpha(mask)
    return image


def saveImageToBuffer(image: Image, compression_level: int = 1) -> BytesIO:
    """
    Sauvegarde une image dans un buffer avec un niveau de compression spécifié.

    :param image: PIL Image object.
    :param compression_level: Compression level (0-9).
    :return: BytesIO object.
    """
    buffer = BytesIO()
    image.save(buffer, format='PNG', compression_level=compression_level)
    buffer.seek(0)
    return buffer
