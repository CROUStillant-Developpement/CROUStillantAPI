from .regions.v1_regions import bp as RouteRegions
from .restaurants.v1_restaurants import bp as RouteRestaurants
from .service.v1_service import bp as RouteService
from .plats.v1_plats import bp as RoutePlats
from .misc.v1_misc import bp as RouteMisc
from .taches.v1_taches import bp as RouteTaches
from .interne.v1_interne import bp as RouteInterne
from .monitoring.v1_monitoring import bp as RouteMonitoring


__all__ = [
    "RouteRegions",
    "RouteRestaurants",
    "RouteService",
    "RoutePlats",
    "RouteMisc",
    "RouteTaches",
    "RouteInterne",
    "RouteMonitoring"
]
