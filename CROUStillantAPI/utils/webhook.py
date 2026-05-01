import asyncio
import hashlib
from datetime import datetime
from pytz import timezone
from aiohttp import ClientSession
from ..utils.logger import Logger
import discord


PARIS_TZ = timezone("Europe/Paris")


class ErrorBatchView(discord.ui.LayoutView):
    """
    Vue Discord pour notifier un lot d'erreurs 500.

    Construit un :class:`discord.ui.Container` composé d'une section d'en-tête,
    d'un affichage par erreur (détails de la requête + type d'exception) et d'un pied de page.
    """

    def __init__(self, errors: list[dict], year: int) -> None:
        """
        Initialise la vue avec la liste des erreurs à afficher.

        :param errors: Liste des erreurs à afficher. Chaque entrée doit contenir les clés
            ``request_id``, ``method``, ``path``, ``args``, ``type`` et ``message``.
        :type errors: list[dict]
        :param year: Année courante affichée dans le pied de page.
        :type year: int
        """
        super().__init__()

        items = [
            discord.ui.Section(
                f"## \U0001f6a8 {len(errors)} erreur(s) 500 détectée(s)",
                accessory=discord.ui.Thumbnail(media="https://croustillant.menu/logo.png"),
            ),
            discord.ui.Separator(),
        ]

        for i, err in enumerate(errors):
            lines = [
                f"**`{err['method']} {err['path']}`** — `{err['type']}`",
                f"`{err['message']}`",
                f"- ID : `{err['request_id']}`",
            ]
            if err["args"]:
                lines.append(f"- Args : `{err['args']}`")

            items.append(discord.ui.TextDisplay(content="\n".join(lines)))
            if i < len(errors) - 1:
                items.append(discord.ui.Separator())

        items.append(discord.ui.Separator())
        items.append(
            discord.ui.TextDisplay(
                content=f"-# *CROUStillant API • {year} | Tous droits réservés.*"
            )
        )

        self.add_item(discord.ui.Container(*items))


class ErrorWebhook:
    """
    Envoie les erreurs 500 vers un webhook Discord par lot, en évitant les doublons.

    Les erreurs sont collectées en mémoire et envoyées périodiquement via
    :meth:`run_background_flush`. Chaque erreur unique (même type + même message)
    n'est transmise qu'une seule fois par fenêtre de flush.
    """

    def __init__(
        self, session: ClientSession, url: str, logger: Logger, flush_interval: int = 60
    ) -> None:
        """
        Initialise le gestionnaire de webhook.

        :param session: Session HTTP partagée de l'application.
        :type session: ClientSession
        :param url: URL du webhook Discord.
        :type url: str
        :param logger: Logger de l'application pour les erreurs internes.
        :type logger: Logger
        :param flush_interval: Intervalle en secondes entre chaque envoi automatique.
        :type flush_interval: int
        """
        self._session = session
        self._url = url
        self._logger = logger
        self._flush_interval = flush_interval
        self._buffer: list[dict] = []
        self._seen: set[str] = set()
        self._lock = asyncio.Lock()

    def _fingerprint(self, exception: Exception) -> str:
        """
        Calcule une empreinte unique pour une exception donnée.

        L'empreinte est basée sur le nom du type et le message de l'exception,
        ce qui permet de dédupliquer les erreurs identiques au sein d'une même fenêtre de flush.

        :param exception: L'exception à identifier.
        :type exception: Exception
        :return: Hash MD5 hexadécimal de l'exception.
        :rtype: str
        """
        key = f"{type(exception).__name__}:{str(exception)}"
        return hashlib.md5(key.encode()).hexdigest()

    async def collect(self, request, exception: Exception) -> None:
        """
        Ajoute une erreur au tampon si elle n'a pas déjà été signalée dans la fenêtre courante.

        Seuls le type, le message de l'exception et les métadonnées de la requête (ID, méthode,
        chemin, arguments) sont conservés — aucun détail de traceback n'est transmis au webhook.

        :param request: Requête Sanic ayant déclenché l'exception.
        :param exception: L'exception à enregistrer.
        :type exception: Exception
        """
        fingerprint = self._fingerprint(exception)
        async with self._lock:
            if fingerprint in self._seen:
                return
            self._seen.add(fingerprint)

            args = dict(getattr(request, "args", {}))

            self._buffer.append(
                {
                    "request_id": getattr(request.ctx, "request_id", "unknown"),
                    "method": getattr(request, "method", "unknown"),
                    "path": getattr(request, "path", "unknown"),
                    "args": str(args) if args else "",
                    "type": type(exception).__name__,
                    "message": str(exception)[:256],
                }
            )

    async def flush(self) -> None:
        """
        Envoie toutes les erreurs en attente vers le webhook et vide le tampon.

        Les erreurs vues (``_seen``) sont réinitialisées à chaque flush afin d'éviter
        une croissance mémoire non bornée. Le fenêtre de déduplication correspond donc
        à un intervalle de flush. Si le tampon est vide, la méthode retourne immédiatement.
        """
        async with self._lock:
            if not self._buffer:
                return
            errors = self._buffer.copy()
            self._buffer.clear()
            self._seen.clear()

        now = datetime.now(PARIS_TZ)
        webhook = discord.Webhook.from_url(self._url, session=self._session)

        for i in range(0, len(errors), 10):
            chunk = errors[i : i + 10]
            view = ErrorBatchView(errors=chunk, year=now.year)
            await webhook.send(view=view)

    async def run_background_flush(self) -> None:
        """
        Tâche de fond qui appelle :meth:`flush` à intervalle régulier.

        Destinée à être enregistrée comme tâche Sanic via ``app.add_task``.
        Les erreurs levées lors du flush sont capturées via le logger de l'application
        afin de ne pas interrompre la boucle.
        """
        while True:
            await asyncio.sleep(self._flush_interval)
            try:
                await self.flush()
            except Exception as exc:
                self._logger.error(f"[ErrorWebhook] Erreur lors du flush : {exc}")
