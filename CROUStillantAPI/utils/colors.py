import re


def validate_color(color: str) -> bool:
    """
    Valide qu'une couleur est au format hexadécimal.

    :param color: Couleur à valider (format: #RRGGBB ou #RGB).
    :type color: str

    :return: True si la couleur est valide, False sinon.
    :rtype: bool
    """
    if not color:
        return False

    # Support both #RRGGBB and #RGB formats
    pattern = r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
    return bool(re.match(pattern, color))


def parse_custom_colours(params: dict) -> dict:
    """
    Parse et valide les couleurs personnalisées des paramètres de requête.

    :param params: Paramètres de la requête contenant les couleurs.
    :type params: dict

    :return: Dictionnaire des couleurs personnalisées valides.
    :rtype: dict
    """
    custom_colours = {}
    colour_keys = ["header", "content", "title", "infos"]

    for key in colour_keys:
        color_param = params.get(f"color_{key}")
        if color_param and validate_color(color_param):
            custom_colours[key] = color_param

    return custom_colours if custom_colours else None
