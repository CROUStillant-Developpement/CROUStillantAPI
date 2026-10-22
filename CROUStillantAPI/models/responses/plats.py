from sanic_ext import openapi
from ..components import (
    PlatComponent,
    PlatComponentWithTotal,
    PlatCanoniqueComponent,
    AnalyseResultatComponent,
)


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


class PlatsWithTotal:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    data = openapi.Array(
        items=PlatComponentWithTotal,
        description="Liste des plats",
    )


class PlatCanonique:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    data = PlatCanoniqueComponent


class AnalysePlat:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    data = AnalyseResultatComponent
