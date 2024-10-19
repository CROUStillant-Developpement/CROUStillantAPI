from .categorie import CategorieTriee
from sanic_ext import openapi
from enum import Enum


class TypeRepas(Enum):
    matin = "matin"
    midi = "midi"
    soir = "soir"


@openapi.component
class Repas:
    code = openapi.String(
        description="Identifiant du repas",
        example=1,
    )
    type = openapi.String(
        description="Type du repas",
        example="matin",
        enum=TypeRepas,
    )
    categories = openapi.Array(
        description="Liste des catégories du repas",
        items=CategorieTriee,
    )
