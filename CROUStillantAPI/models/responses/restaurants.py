from sanic_ext import openapi
from ..components import RestaurantComponent


class Restaurants:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    data = openapi.Array(
        items=RestaurantComponent,
        description="Liste des restaurants",
    )


class Restaurant:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    data = RestaurantComponent


class Data:
    code = openapi.Integer(
        description="Code de retour",
        example=1502,
    )
    ajout = openapi.String(
        description="Date d'ajout du restaurant dans la base de données",
        example="2024-10-19 18:44:31",
    )
    modifie = openapi.String(
        description="Dernière mise à jour du restaurant dans la base de données",
        example="2024-10-19 19:44:31",
    )
    nb = openapi.Integer(
        description="Nombre de fois que le restaurant a été mis à jour", 
        example=1,
    )


class RestaurantInfo:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    data = Data
