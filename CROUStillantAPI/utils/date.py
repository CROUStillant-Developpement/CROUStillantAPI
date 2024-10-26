from datetime import datetime


def getCleanDate(date: datetime) -> str:
    """
    Renvoie une date formatée.

    :param date: Date à formater.
    :type date: datetime

    :return: Date formatée.
    :rtype: str
    """
    jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    mois = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]

    return f"{jours[int(date.strftime('%w'))-1].title()} {date.day} {mois[int(date.strftime('%m'))-1]} {date.year}"
