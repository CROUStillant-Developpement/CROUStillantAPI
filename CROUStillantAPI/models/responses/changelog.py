from sanic_ext import openapi
from ..components import ChangeLogComponent


class ChangeLog:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    data = ChangeLogComponent
