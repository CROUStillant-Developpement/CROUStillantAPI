from sanic_ext import openapi
from ..components import TypeRestaurantComponent


class TypesRestaurants:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    data = openapi.Array(
        items=TypeRestaurantComponent,
        description="Liste des restaurants",
    )
