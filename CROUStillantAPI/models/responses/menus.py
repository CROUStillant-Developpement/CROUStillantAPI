from sanic_ext import openapi
from ..components import MenuComponent, DateComponent


class Menus:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    data = openapi.Array(
        description="Liste des menus",
        items=MenuComponent,
    )


class Menu:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    data = MenuComponent


class Dates:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    data = openapi.Array(
        description="Liste des dates",
        items=openapi.Component(DateComponent),
    )
