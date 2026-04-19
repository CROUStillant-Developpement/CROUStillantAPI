from .region import Region
from .type_restaurant import TypeRestaurant
from sanic_ext import openapi


@openapi.component
class RestaurantStatus:
    code = openapi.Integer(description="Identifiant du restaurant", example=1)
    nom = openapi.String(description="Nom du restaurant", example="Resto U' Cap Sud")
    region = Region
    type_restaurant = TypeRestaurant
    ouvert = openapi.Boolean(description="Le restaurant est-il ouvert ?", example=True)
    actif = openapi.Boolean(description="Le restaurant est-il actif ?", example=True)
