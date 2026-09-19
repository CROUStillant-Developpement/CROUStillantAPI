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


def toFloat(value) -> float | None:
    """
    Convertit une valeur numérique PostgreSQL (NUMERIC -> Decimal) en float.

    :param value: La valeur à convertir
    :return: La valeur en float, ou None
    """
    return float(value) if value is not None else None


def formatDate(value, fmt: str = "%d-%m-%Y %H:%M:%S") -> str | None:
    """
    Formate une date (ou un datetime) PostgreSQL, en conservant None.

    :param value: La date à formater
    :param fmt: Le format de sortie
    :return: La date formatée, ou None
    """
    return value.strftime(fmt) if value is not None else None
