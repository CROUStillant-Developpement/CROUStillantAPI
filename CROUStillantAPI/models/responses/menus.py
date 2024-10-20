from sanic_ext import openapi
from ..components import MenuComponent


class Menus:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    data = openapi.Object(
        description="Données de la réponse",
        properties= {
            "2024-10-19": openapi.Component(MenuComponent),
        }
    )


class Menu:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    data = MenuComponent
