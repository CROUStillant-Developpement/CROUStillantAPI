import json

from croustillant_classifier import occurrence_type


# Les 14 allergènes majeurs (règlement UE 1169/2011), mêmes identifiants que la table ALLERGENE
ALLERGENES = {
    1: ("GLUTEN", "Céréales contenant du gluten"),
    2: ("CRUSTACES", "Crustacés"),
    3: ("OEUFS", "Œufs"),
    4: ("POISSONS", "Poissons"),
    5: ("ARACHIDES", "Arachides"),
    6: ("SOJA", "Soja"),
    7: ("LAIT", "Lait"),
    8: ("FRUITS_A_COQUE", "Fruits à coque"),
    9: ("CELERI", "Céleri"),
    10: ("MOUTARDE", "Moutarde"),
    11: ("SESAME", "Graines de sésame"),
    12: ("SULFITES", "Dioxyde de soufre et sulfites"),
    13: ("LUPIN", "Lupin"),
    14: ("MOLLUSQUES", "Mollusques"),
}


def format_allergenes(ids: list[int] | None) -> list[dict]:
    """
    Convertit les identifiants d'allergènes déclarés dans un libellé en objets lisibles.

    Ces allergènes sont écrits par le restaurant du CROUS lui-même ("(1.3.7)") : ils font
    autorité et sont donc marqués vérifiés, contrairement aux allergènes déduits.

    :param ids: Les identifiants (ALLERGENE.IDALLERGENE)
    :return: Les allergènes
    """
    return [
        {"code": ALLERGENES[i][0], "libelle": ALLERGENES[i][1], "source": "CROUS", "verifie": True}
        for i in sorted(set(ids or []))
        if i in ALLERGENES
    ]


def format_analyse(row, tpcat: str | None = None) -> dict | None:
    """
    Formate l'analyse d'un plat (colonnes `PLAT_ANALYSE_COLUMNS`, voir `entities/plats.py`).

    Le type d'un composant est celui du plat canonique, éventuellement réinterprété par la
    catégorie du menu où il est servi (une pizza servie en « Entrées » est une entrée).

    :param row: La ligne retournée par la base de données
    :param tpcat: La catégorie du menu (None hors menu)
    :return: L'analyse, ou None si le plat n'a pas encore été analysé
    """
    if row.get("nature") is None:
        return None

    composants = row.get("composants") or []
    if isinstance(composants, str):
        composants = json.loads(composants)

    composants = [
        {
            "code": c["code"],
            "libelle": c["libelle"],
            "type": occurrence_type(c["type"], tpcat, main_component=i == 0),
            "type_defaut": c["type"],
            "vegetarien": c["vegetarien"],
        }
        for i, c in enumerate(composants)
    ]

    return {
        "nature": row.get("nature"),
        "type_info": row.get("type_info"),
        "libelle": row.get("libelle_net"),
        "type": composants[0]["type"] if composants else None,
        "points": row.get("points"),
        "prix": list(row.get("prix") or []),
        "allergenes_declares": format_allergenes(row.get("allergenes")),
        # le plat entier est végétarien si tous ses composants le sont
        # ("Cordon bleu, falafel (vg)" ne l'est pas, même s'il mentionne VG)
        "vegetarien": all(c["vegetarien"] for c in composants) if composants else bool(row.get("vegetarien")),
        "origines": list(row.get("origines") or []),
        "labels": list(row.get("labels") or []),
        "composants": composants,
    }
