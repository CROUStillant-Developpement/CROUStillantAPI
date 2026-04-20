from PIL import ImageFont
from io import BytesIO

_FONT_PATH = "./assets/fonts/Inter-VariableFont.ttf"
_data: bytes | None = None


def make_font(size: int, weight_name: str) -> ImageFont.FreeTypeFont:
    global _data
    if _data is None:
        with open(_FONT_PATH, "rb") as f:
            _data = f.read()
    font = ImageFont.truetype(BytesIO(_data), size)
    font.set_variation_by_name(weight_name)
    return font
