from .repas import Repas
from sanic_ext import openapi


@openapi.component
class Tache:
    id = openapi.String(
        description="Identifiant de la tâche",
        example=1,
    )
    debut = openapi.String(
        description="Date de début de la tâche",
        example="21-10-2024 00:00:00",
    )
    debut_regions = openapi.Integer(
        description="Nombre de régions récupérées au début de la tâche",
        example=100,
    )
    debut_restaurants = openapi.Integer(
        description="Nombre de restaurants récupérés au début de la tâche",
        example=100,
    )
    debut_types_restaurants = openapi.Integer(
        description="Nombre de types de restaurants récupérés au début de la tâche",
        example=100,
    )
    debut_menus = openapi.Integer(
        description="Nombre de menus récupérés au début de la tâche",
        example=100,
    )
    debut_repas = openapi.Integer(
        description="Nombre de repas récupérés au début de la tâche",
        example=100,
    )
    debut_categories = openapi.Integer(
        description="Nombre de catégories récupérées au début de la tâche",
        example=100,
    )
    debut_plats = openapi.Integer(
        description="Nombre de plats récupérés au début de la tâche",
        example=100,
    )
    debut_compositions = openapi.Integer(
        description="Nombre de compositions récupérées au début de la tâche",
        example=100,
    )
    fin = openapi.String(
        description="Date de fin de la tâche",
        example="21-10-2024 00:00:00",
    )
    fin_regions = openapi.Integer(
        description="Nombre de régions récupérées à la fin de la tâche",
        example=100,
    )
    fin_restaurants = openapi.Integer(
        description="Nombre de restaurants récupérés à la fin de la tâche",
        example=100,
    )
    fin_types_restaurants = openapi.Integer(
        description="Nombre de types de restaurants récupérés à la fin de la tâche",
        example=100,
    )
    fin_menus = openapi.Integer(
        description="Nombre de menus récupérés à la fin de la tâche",
        example=100,
    )
    fin_repas = openapi.Integer(
        description="Nombre de repas récupérés à la fin de la tâche",
        example=100,
    )
    fin_categories = openapi.Integer(
        description="Nombre de catégories récupérées à la fin de la tâche",
        example=100,
    )
    fin_plats = openapi.Integer(
        description="Nombre de plats récupérés à la fin de la tâche",
        example=100,
    )
    fin_compositions = openapi.Integer(
        description="Nombre de compositions récupérées à la fin de la tâche",
        example=100,
    )
    requetes = openapi.Integer(
        description="Nombre de requêtes effectuées",
        example=900,
    )


class TacheWithRestaurants:
    id = openapi.String(
        description="Identifiant de la tâche",
        example=1,
    )
    debut = openapi.String(
        description="Date de début de la tâche",
        example="21-10-2024 00:00:00",
    )
    debut_regions = openapi.Integer(
        description="Nombre de régions récupérées au début de la tâche",
        example=100,
    )
    debut_restaurants = openapi.Integer(
        description="Nombre de restaurants récupérés au début de la tâche",
        example=100,
    )
    debut_types_restaurants = openapi.Integer(
        description="Nombre de types de restaurants récupérés au début de la tâche",
        example=100,
    )
    debut_menus = openapi.Integer(
        description="Nombre de menus récupérés au début de la tâche",
        example=100,
    )
    debut_repas = openapi.Integer(
        description="Nombre de repas récupérés au début de la tâche",
        example=100,
    )
    debut_categories = openapi.Integer(
        description="Nombre de catégories récupérées au début de la tâche",
        example=100,
    )
    debut_plats = openapi.Integer(
        description="Nombre de plats récupérés au début de la tâche",
        example=100,
    )
    debut_compositions = openapi.Integer(
        description="Nombre de compositions récupérées au début de la tâche",
        example=100,
    )
    fin = openapi.String(
        description="Date de fin de la tâche",
        example="21-10-2024 00:00:00",
    )
    fin_regions = openapi.Integer(
        description="Nombre de régions récupérées à la fin de la tâche",
        example=100,
    )
    fin_restaurants = openapi.Integer(
        description="Nombre de restaurants récupérés à la fin de la tâche",
        example=100,
    )
    fin_types_restaurants = openapi.Integer(
        description="Nombre de types de restaurants récupérés à la fin de la tâche",
        example=100,
    )
    fin_menus = openapi.Integer(
        description="Nombre de menus récupérés à la fin de la tâche",
        example=100,
    )
    fin_repas = openapi.Integer(
        description="Nombre de repas récupérés à la fin de la tâche",
        example=100,
    )
    fin_categories = openapi.Integer(
        description="Nombre de catégories récupérées à la fin de la tâche",
        example=100,
    )
    fin_plats = openapi.Integer(
        description="Nombre de plats récupérés à la fin de la tâche",
        example=100,
    )
    fin_compositions = openapi.Integer(
        description="Nombre de compositions récupérées à la fin de la tâche",
        example=100,
    )
    requetes = openapi.Integer(
        description="Nombre de requêtes effectuées",
        example=900,
    )
    restaurants = openapi.Array(
        description="Identifiants des restaurants analysés",
        items=openapi.Integer,
        example=[1, 2, 3],
    )
