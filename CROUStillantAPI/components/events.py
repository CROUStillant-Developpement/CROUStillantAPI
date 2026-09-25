import asyncio
import json

from asyncpg import Connection, Pool, connect
from datetime import date, datetime
from os import environ
from sanic import Sanic

from .cache import RESTAURANTS_TAG, Cache


# Canal PostgreSQL sur lequel les nouveaux événements sont notifiés (payload : ID de l'événement)
CHANNEL = "evenement"

# Types d'événements existants
TYPES = (
    "menu.created",
    "menu.updated",
    "menu.deleted",
    "restaurant.created",
    "restaurant.updated",
    "restaurant.actif",
    "restaurant.opened",
)

# Profondeur maximale du rattrapage des événements manqués (Last-Event-ID)
HISTORY_DAYS = 7

# Nombre maximum d'événements renvoyés lors d'un rattrapage
HISTORY_LIMIT = 5000

# Nombre maximum d'événements en attente pour un client : au-delà, il est déconnecté
# (il se reconnectera et rattrapera les événements manqués via Last-Event-ID)
QUEUE_SIZE = 1000

# Intervalle de vérification de la connexion LISTEN (secondes)
HEALTHCHECK_INTERVAL = 30


def serialize(row: dict) -> dict:
    """
    Convertit un événement de la base de données en dictionnaire sérialisable.

    :param row: L'événement
    :return: L'événement sérialisable
    """
    donnees = row.get("donnees")
    if isinstance(donnees, str):
        donnees = json.loads(donnees)

    creation: datetime = row.get("creation")
    menuDate: date | None = row.get("date")

    return {
        "id": row.get("id"),
        "type": row.get("type"),
        "code": row.get("rid"),
        "date": menuDate.strftime("%d-%m-%Y") if menuDate else None,
        "menu": row.get("mid"),
        "donnees": donnees,
        "creation": creation.strftime("%d-%m-%Y %H:%M:%S"),
    }


class Subscription:
    """
    Abonnement d'un client au flux d'événements.
    """

    def __init__(self, rids: set[int] | None, types: set[str] | None) -> None:
        """
        :param rids: Restaurants suivis (``None`` : tous)
        :param types: Types d'événements suivis (``None`` : tous)
        """
        self.rids = rids
        self.types = types
        self.queue: asyncio.Queue[dict | None] = asyncio.Queue(maxsize=QUEUE_SIZE)
        self.closed = False

    def matches(self, event: dict) -> bool:
        """
        Vérifie si un événement correspond aux filtres de l'abonnement.
        """
        if self.types is not None and event["type"] not in self.types:
            return False
        if self.rids is not None and event["code"] not in self.rids:
            return False
        return True

    def push(self, event: dict) -> None:
        """
        Ajoute un événement à la file du client, ou le déconnecte si elle est pleine.
        """
        if self.closed or not self.matches(event):
            return

        try:
            self.queue.put_nowait(event)
        except asyncio.QueueFull:
            self.close()

    def close(self) -> None:
        """
        Termine l'abonnement : le flux du client se termine après les événements en attente.
        """
        if self.closed:
            return

        self.closed = True

        # Libère une place si besoin pour garantir la réception du signal de fin
        if self.queue.full():
            self.queue.get_nowait()
        self.queue.put_nowait(None)


class EventBroker:
    """
    Diffuse les événements de la base de données (table EVENEMENT) aux clients connectés.

    Une connexion dédiée écoute les notifications PostgreSQL (``LISTEN evenement``).
    Elle se connecte directement à PostgreSQL (``POSTGRES_LISTEN_HOST``) : pgbouncer en
    mode ``transaction`` ne relaie pas les notifications. À chaque notification, les
    nouveaux événements sont lus dans l'ordre, le cache des restaurants concernés est
    invalidé, puis les événements sont transmis aux abonnés.
    """

    def __init__(self, app: Sanic) -> None:
        """
        :param app: Instance de l'application Sanic
        """
        self.app = app
        self.subscriptions: set[Subscription] = set()
        self.lastId: int | None = None
        self.wakeup = asyncio.Event()
        self.connected = False

    @property
    def pool(self) -> Pool:
        return self.app.ctx.pool

    @property
    def cache(self) -> Cache:
        return self.app.ctx.cache

    def start(self) -> None:
        """
        Démarre l'écoute des notifications et la diffusion des événements.
        """
        self.app.add_task(self.listen(), name="evenements_listen")
        self.app.add_task(self.dispatch(), name="evenements_dispatch")

    def subscribe(self, rids: set[int] | None, types: set[str] | None) -> Subscription:
        """
        Abonne un client au flux d'événements.
        """
        subscription = Subscription(rids, types)
        self.subscriptions.add(subscription)
        return subscription

    def unsubscribe(self, subscription: Subscription) -> None:
        """
        Désabonne un client.
        """
        subscription.closed = True
        self.subscriptions.discard(subscription)

    async def history(
        self, since: int, rids: set[int] | None, types: set[str] | None
    ) -> list[dict]:
        """
        Récupère les événements postérieurs à ``since`` (au plus ``HISTORY_DAYS`` jours).

        :param since: ID du dernier événement reçu par le client
        :param rids: Restaurants suivis (``None`` : tous)
        :param types: Types d'événements suivis (``None`` : tous)
        :return: Les événements, du plus ancien au plus récent
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            rows = await connection.fetch(
                f"""
                    SELECT ID, TYPE, RID, DATE, MID, DONNEES, CREATION
                    FROM EVENEMENT
                    WHERE ID > $1
                        AND CREATION >= NOW() - INTERVAL '{HISTORY_DAYS} days'
                        AND ($2::int[] IS NULL OR RID = ANY($2::int[]))
                        AND ($3::text[] IS NULL OR TYPE = ANY($3::text[]))
                    ORDER BY ID
                    LIMIT {HISTORY_LIMIT}
                """,
                since,
                list(rids) if rids is not None else None,
                list(types) if types is not None else None,
            )

        return [serialize(dict(row)) for row in rows]

    async def listen(self) -> None:
        """
        Maintient la connexion LISTEN, et se reconnecte en cas de coupure.
        """
        while True:
            try:
                await self._listenOnce()
            except asyncio.CancelledError:
                raise
            except Exception as e:
                self.connected = False
                self.app.ctx.logs.error(
                    f"[Événements] Connexion LISTEN perdue, nouvelle tentative dans 5 secondes... ({e})"
                )
                await asyncio.sleep(5)

    async def _listenOnce(self) -> None:
        """
        Écoute les notifications jusqu'à la perte de la connexion.
        """
        connection = await connect(
            database=environ["POSTGRES_DATABASE"],
            user=environ["POSTGRES_USER"],
            password=environ["POSTGRES_PASSWORD"],
            host=environ.get("POSTGRES_LISTEN_HOST") or environ["POSTGRES_HOST"],
            port=environ.get("POSTGRES_LISTEN_PORT") or environ["POSTGRES_PORT"],
        )

        disconnected = asyncio.Event()
        connection.add_termination_listener(lambda _connection: disconnected.set())

        try:
            await connection.add_listener(CHANNEL, self._onNotification)

            if self.lastId is None:
                # Premier démarrage : seuls les événements à venir sont diffusés en direct
                self.lastId = await connection.fetchval(
                    "SELECT COALESCE(MAX(ID), 0) FROM EVENEMENT"
                )

            self.connected = True
            self.app.ctx.logs.info(
                f"[Événements] Écoute des notifications (dernier événement : {self.lastId})"
            )

            # Diffuse les événements éventuellement survenus pendant une coupure
            self.wakeup.set()

            while not disconnected.is_set():
                try:
                    await asyncio.wait_for(
                        disconnected.wait(), timeout=HEALTHCHECK_INTERVAL
                    )
                except TimeoutError:
                    # Requête de test : détecte une connexion abandonnée en silence
                    await connection.execute("SELECT 1;")

            raise ConnectionError("La connexion PostgreSQL a été fermée par le serveur")
        finally:
            self.connected = False
            try:
                if not connection.is_closed():
                    await connection.close()
            except Exception:
                pass

    def _onNotification(self, _connection, _pid: int, _channel: str, _payload: str) -> None:
        """
        Callback des notifications : les événements sont lus et diffusés par :meth:`dispatch`.
        """
        self.wakeup.set()

    async def dispatch(self) -> None:
        """
        Lit les nouveaux événements et les diffuse, à chaque notification.
        """
        while True:
            await self.wakeup.wait()
            self.wakeup.clear()

            if self.lastId is None:
                continue

            try:
                await self._dispatchPending()
            except asyncio.CancelledError:
                raise
            except Exception as e:
                self.app.ctx.logs.error(f"[Événements] Erreur lors de la diffusion : {e}")
                await asyncio.sleep(1)
                self.wakeup.set()

    async def _dispatchPending(self) -> None:
        """
        Diffuse tous les événements postérieurs au dernier événement diffusé.
        """
        while True:
            async with self.pool.acquire() as connection:
                connection: Connection

                rows = await connection.fetch(
                    """
                        SELECT ID, TYPE, RID, DATE, MID, DONNEES, CREATION
                        FROM EVENEMENT
                        WHERE ID > $1
                        ORDER BY ID
                        LIMIT 1000
                    """,
                    self.lastId,
                )

            if not rows:
                return

            events = [serialize(dict(row)) for row in rows]

            await self._invalidate(events)

            for event in events:
                for subscription in list(self.subscriptions):
                    subscription.push(event)

            self.lastId = events[-1]["id"]

    async def _invalidate(self, events: list[dict]) -> None:
        """
        Invalide le cache des restaurants concernés par les événements.
        """
        tags = set()
        for event in events:
            if event["code"] is None:
                continue

            tags.add(Cache.restaurantTag(event["code"]))
            if event["type"].startswith("restaurant."):
                tags.add(RESTAURANTS_TAG)

        if tags:
            deleted = await self.cache.invalidate(*tags)
            self.app.ctx.logs.debug(
                f"[Événements] {len(events)} événement(s), {deleted} réponse(s) invalidée(s) du cache"
            )

    def close(self) -> None:
        """
        Termine tous les abonnements (arrêt du serveur).
        """
        for subscription in list(self.subscriptions):
            subscription.close()
