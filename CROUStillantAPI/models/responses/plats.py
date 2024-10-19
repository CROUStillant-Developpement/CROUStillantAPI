from sanic_ext import openapi
from ..components import PlatComponent


class Plats:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    data = openapi.Array(
        items=PlatComponent,
        description="Liste des plats",
    )


class Plat:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    data = PlatComponent
