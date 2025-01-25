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
