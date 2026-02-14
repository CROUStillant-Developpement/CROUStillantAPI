from sanic_ext import openapi


class Status:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    message = openapi.String(
        description="Message de retour", example="L'API est en ligne."
    )
