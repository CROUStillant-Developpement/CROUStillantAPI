from sanic_ext import openapi
from ..components import TacheComponent, TacheWithRestaurantsComponent


class Taches:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    data = openapi.Array(
        description="Liste des tâches",
        items=TacheComponent
    )


class Tache:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    data = TacheWithRestaurantsComponent
