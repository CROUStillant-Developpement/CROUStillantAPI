from sanic.request import Request
from sanic.response import JSONResponse, json


class Response:
    """
    Classe pour les réponses
    """
    def __init__(self, request: Request) -> None:
        """
        Initialisation de la classe

        :param request: Request
        """
        self.request = request


    def generate(self) -> None:
        """
        Génère la réponse
        """
        raise NotImplementedError


class JSON(Response):
    """
    Classe pour les réponses JSON
    """
    def __init__(self, request: Request, success: bool = True, data: dict = None, status: int = 200, message: str = None) -> None:
        """
        Initialisation de la classe

        :param request: Request
        :param data: dict
        :param success: bool
        :param status: int
        :param message: str
        """
        super().__init__(request)
        self.data = data
        self.success = success
        self.status = status
        self.message = message


    def generate(self) -> JSONResponse:
        """
        Génère la réponse

        :return: JSONResponse
        """
        if not self.data and not self.message:
            return json(
                {
                    "success": self.success,
                    "message": "Quelque chose s'est mal passé... Veuillez réessayer plus tard. Si le problème persiste, contactez nous !"
                },
                status=self.status
            )

        if self.message:
            return json(
                {
                    "success": self.success,
                    "message": self.message
                },
                status=self.status
            )

        return json(
                {
                "success": self.success,
                "data": self.data
            },
            status=self.status
        )
