from .stats import Stats
from .regions import Regions
from .restaurants import Restaurants
from .types_restaurants import TypesRestaurants
from .plats import Plats
from .menus import Menus
from .taches import Taches
from asyncpg import Pool


class Entities:
    def __init__(self, pool: Pool) -> None:
        self.pool = pool

        self.stats = Stats(pool)
        self.regions = Regions(pool)
        self.restaurants = Restaurants(pool)
        self.types_restaurants = TypesRestaurants(pool)
        self.plats = Plats(pool)
        self.menus = Menus(pool)
        self.taches = Taches(pool)
