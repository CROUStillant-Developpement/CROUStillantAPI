from .plat import Plat, PlatTrie
from sanic_ext import openapi


@openapi.component
class Categorie:
    code = openapi.String(
        description="Identifiant de la catégorie",
        example=1,
    )
    libelle = openapi.String(
        description="Libellé de la catégorie",
        example="Entrées",
    )
    plats = openapi.Array(
        description="Liste des plats de la catégorie",
        items=Plat,
    )


@openapi.component
class CategorieTriee:
    code = openapi.String(
        description="Identifiant de la catégorie",
        example=1,
    )
    libelle = openapi.String(
        description="Libellé de la catégorie",
        example="Entrées",
    )
    ordre = openapi.Integer(
        description="Ordre de la catégorie dans le menu",
        example=1,
    )
    plats = openapi.Array(
        description="Liste des plats de la catégorie",
        items=PlatTrie,
    )
