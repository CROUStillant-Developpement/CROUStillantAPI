from .region import Region
from .type_restaurant import TypeRestaurant
from .jours import Jours
from sanic_ext import openapi


@openapi.component
class Restaurant:
    code = openapi.Integer(description="Identifiant du restaurant", example=1)
    region = Region
    type_restaurant = TypeRestaurant
    nom = openapi.String(description="Nom du restaurant", example="Resto U' Cap Sud")
    adresse = openapi.String(
        description="Adresse du restaurant", example="2 avenue Poplawski à PAU"
    )
    latitude = openapi.Float(description="Latitude du restaurant", example=43.313084)
    longitude = openapi.Float(description="Longitude du restaurant", example=-0.367188)
    horaires = openapi.Array(
        items=openapi.String(),
        description="Horaires d'ouverture du restaurant",
        example=[
            "du lundi au vendredi",
            "SELF : 11h15 - 13h45 | 18h-19h30",
            "BAR : 11h30-14h",
            "SANDWICHERIE : 11h15 - 13h45",
            "L'OASIS (restaurant administratif) : 11h30 - 13h45",
        ],
    )
    jours_ouvert = openapi.Array(
        items=Jours,
        description="Jours d'ouverture du restaurant",
    )
    image_url = openapi.String(description="URL de l'image du restaurant", example=None)
    email = openapi.String(description="Adresse email du restaurant", example=None)
    telephone = openapi.String(
        description="Numéro de téléphone du restaurant", example=None
    )
    ispmr = openapi.Boolean(
        description="Le restaurant est-il accessible aux PMR ?", example=True
    )
    zone = openapi.String(description="Zone du restaurant", example="Pau")
    paiement = openapi.Array(
        items=openapi.String(),
        description="Moyens de paiement acceptés par le restaurant",
        example=["Carte bancaire", "IZLY"],
    )
    acces = openapi.String(
        description="Informations sur l'accès au restaurant", example=["Bus 2,4, 6, 13"]
    )
    actif = openapi.Boolean(description="Le restaurant est-il actif ?", example=True)
