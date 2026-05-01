import logging


class Logger:
    """
    La classe Logger permet de gérer les logs de l'application.
    """

    def __init__(self, file: str) -> None:
        """
        Initialisation du logger
        """
        self.file = file

        self.logger = logging.getLogger(f"CROUStillant - {self.file}")
        self.logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler()
        dt_fmt = '%Y-%m-%d %H:%M:%S'
        formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.logger.info("Logger initialisé !")

    def info(self, message: str) -> None:
        """
        Inscrire un message d'information

        :param message: The message
        """
        self.logger.info(message)

    def warning(self, message: str) -> None:
        """
        Inscrire un message d'avertissement

        :param message: The message
        """
        self.logger.warning(message)

    def error(self, message: str) -> None:
        """
        Inscrire un message d'erreur

        :param message: The message
        """
        self.logger.error(message)

    def critical(self, message: str) -> None:
        """
        Inscrire un message critique

        :param message: The message
        """
        self.logger.critical(message)

    def debug(self, message: str) -> None:
        """
        Inscrire un message de débogage

        :param message: The message
        """
        self.logger.debug(message)
