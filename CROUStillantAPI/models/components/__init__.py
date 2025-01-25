from .region import Region as RegionComponent
from .restaurant import Restaurant as RestaurantComponent
from .type_restaurant import TypeRestaurant as TypeRestaurantComponent
from .plat import Plat as PlatComponent, PlatWithTotal as PlatComponentWithTotal
from .menu import Menu as MenuComponent, Date as DateComponent
from .tache import Tache as TacheComponent, TacheWithRestaurants as TacheWithRestaurantsComponent
from .changelog import ChangeLog as ChangeLogComponent


__all__ = [
    "RegionComponent",
    "RestaurantComponent",
    "TypeRestaurantComponent",
    "PlatComponent",
    "PlatComponentWithTotal",
    "MenuComponent",
    "DateComponent",
    "TacheComponent",
    "TacheWithRestaurantsComponent",
    "ChangeLogComponent",
]
