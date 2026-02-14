def getBoolFromString(b: str | bool) -> bool:
    """
    Convertit une chaîne de caractères en booléen.

    :param b: Chaîne de caractères
    :return: Booléen
    """
    if isinstance(b, bool):
        return b

    if b.lower() == "true":
        return True
    elif b.lower() == "false":
        return False
    else:
        return None


def getIntFromString(i: str | int) -> int:
    """
    Convertit une chaîne de caractères en entier.

    :param i: Chaîne de caractères
    :return: Entier
    """
    if isinstance(i, int):
        return i

    try:
        return int(i)
    except ValueError:
        return 0
