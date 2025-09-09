from sanic.exceptions import SanicException


class ServerErrorException(SanicException):
    status_code = 500

    @property
    def message(self):
        if self.extra["message"]:
            return "Une erreur s'est produite lors du traitement de votre requête. Nous nous excusons pour la gêne occasionnée, notre équipe est sur le coup !"
        else:
            return self.extra["message"]
