from sanic.exceptions import SanicException


class RatelimitException(SanicException):
    status_code = 429
    
    @property
    def message(self):
        return f"Vous avez envoyé trop de requêtes. Veuillez réessayer dans {self.extra['cooldown']} secondes."
