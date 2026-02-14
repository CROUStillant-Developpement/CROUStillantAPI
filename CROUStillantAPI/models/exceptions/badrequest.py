from sanic_ext import openapi


class BadRequest:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=False,
    )
    message = openapi.String(
        description="Message de retour", example="La requête est incorrecte."
    )
