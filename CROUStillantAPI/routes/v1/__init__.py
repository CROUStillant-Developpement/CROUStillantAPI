from .regions.v1_regions import bp as RouteRegions
from .restaurants.v1_restaurants import bp as RouteRestaurants
from .service.v1_service import bp as RouteService
from .plats.v1_plats import bp as RoutePlats
from .misc.v1_misc import bp as RouteMisc
from .taches.v1_taches import bp as RouteTaches
from .interne.v1_interne import bp as RouteInterne

# Meta données de la version
__version__ = "1.0.0"
__author__ = "CROUStillant Développement (github.com/CROUStillant-Developpement)"
__description__ = "/v1 pour l'API de CROUStillant"
__routes__ = [
    RouteRegions,
    RouteRestaurants,
    RouteService,
    RoutePlats,
    RouteMisc,
    RouteTaches,
    RouteInterne,
]


__all__ = ["__version__", "__author__", "__description__", "__routes__"]
