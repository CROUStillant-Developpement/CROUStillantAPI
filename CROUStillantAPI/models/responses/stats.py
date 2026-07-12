from sanic_ext import openapi


class Data:
    regions = openapi.Integer(
        description="Nombre de régions",
        example=26,
    )
    restaurants = openapi.Integer(
        description="Nombre de restaurants",
        example=982,
    )
    restaurants_actifs = openapi.Integer(
        description="Nombre de restaurants actifs",
        example=962,
    )
    types_restaurants = openapi.Integer(
        description="Nombre de types de restaurants",
        example=16,
    )
    menus = openapi.Integer(
        description="Nombre de menus",
        example=5084,
    )
    repas = openapi.Integer(
        description="Nombre de repas",
        example=6818,
    )
    categories = openapi.Integer(
        description="Nombre de catégories",
        example=19776,
    )
    plats = openapi.Integer(
        description="Nombre de plats",
        example=6184,
    )
    compositions = openapi.Integer(
        description="Nombre de compositions",
        example=77694,
    )


class Stats:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    data = Data


class RegionStat:
    code = openapi.Integer(
        description="Identifiant de la région",
        example=1,
    )
    libelle = openapi.String(
        description="Libellé de la région",
        example="Aix-Marseille - Avignon",
    )
    nb_restaurants = openapi.Integer(
        description="Nombre de restaurants dans la région",
        example=42,
    )
    nb_restaurants_actifs = openapi.Integer(
        description="Nombre de restaurants actifs dans la région",
        example=39,
    )
    nb_restaurants_avec_menu = openapi.Integer(
        description="Nombre de restaurants actifs ayant publié au moins un menu sur l'année scolaire en cours",
        example=19,
    )
    nb_repas = openapi.Integer(
        description="Nombre de repas servis sur l'année scolaire en cours",
        example=12000,
    )
    nb_categories = openapi.Integer(
        description="Nombre de catégories sur l'année scolaire en cours",
        example=36000,
    )
    nb_plats = openapi.Integer(
        description="Nombre de plats servis sur l'année scolaire en cours",
        example=250000,
    )
    plats_uniques = openapi.Integer(
        description="Nombre de plats distincts servis sur l'année scolaire en cours",
        example=620,
    )


class StatsByRegion:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    data = openapi.Array(
        items=RegionStat,
        description="Statistiques par région",
    )
