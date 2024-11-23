from .repas import Repas
from sanic_ext import openapi


@openapi.component
class Menu:
    code = openapi.String(
        description="Identifiant du menu",
        example=1,
    )
    date = openapi.String(
        description="Date du menu",
        example="21-10-2024",
    )
    repas = openapi.Array(
        description="Liste des repas du menu",
        items=Repas,
    )


@openapi.component
class Date:
    code = openapi.String(
        description="Identifiant du menu",
        example=1,
    )
    date = openapi.String(
        description="Date du menu",
        example="21-10-2024",
    )
