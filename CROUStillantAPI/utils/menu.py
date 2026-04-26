def build_menu_structure(rows: list) -> dict[str, dict]:
    """
    Convertit une liste de lignes plates (asyncpg) en une structure imbriquée
    date → repas → catégories → plats.

    :param rows: Les lignes retournées par la requête SQL du menu.
    :type rows: list
    :return: Un dictionnaire ordonné dont les clés sont des dates au format ``DD-MM-YYYY``
             et les valeurs sont les menus structurés correspondants.
    :rtype: dict[str, dict]
    """
    menu_per_day: dict[str, dict] = {}

    for row in rows:
        date = row.get("date").strftime("%d-%m-%Y")

        day_menu = menu_per_day.setdefault(
            date, {"code": row.get("mid"), "date": date, "repas": []}
        )

        repas_list = day_menu["repas"]
        if not repas_list or row.get("tpr") != repas_list[-1]["type"]:
            repas_list.append(
                {"code": row.get("rpid"), "type": row.get("tpr"), "categories": []}
            )

        categories_list = repas_list[-1]["categories"]
        if not categories_list or row.get("tpcat") != categories_list[-1]["libelle"]:
            categories_list.append(
                {
                    "code": row.get("catid"),
                    "libelle": row.get("tpcat"),
                    "ordre": row.get("cat_ordre") + 1,
                    "plats": [],
                }
            )

        if row.get("platid") is not None:
            categories_list[-1]["plats"].append(
                {
                    "code": row.get("platid"),
                    "ordre": row.get("plat_ordre") + 1,
                    "libelle": row.get("plat"),
                }
            )

    return menu_per_day
