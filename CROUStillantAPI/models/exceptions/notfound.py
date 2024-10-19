from sanic_ext import openapi


class NotFound:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=False,
    )
    message = openapi.String(
        description="Message de retour",
        example="La ressource demandée n'existe pas."
    )
