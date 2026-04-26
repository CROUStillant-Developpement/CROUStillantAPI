<div align="center">
<img src="https://croustillant.menu/logo.png" alt="CROUStillant Logo"/>
  
# CROUStillant API
CROUStillant est un projet qui a pour but de fournir les menus des restaurants universitaires en France et en Outre-Mer.

</div>

# 📖 • Sommaire

- [🚀 • Présentation](#--présentation)
- [🛠️ • Technologies](#️--technologies)
- [📦 • Installation](#--installation)
- [⚙️ • Variables d'environnement](#️--variables-denvironnement)
- [📡 • Endpoints](#--endpoints)
- [📃 • Crédits](#--crédits)
- [📝 • License](#--license)

# 🚀 • Présentation

Ce dépôt contient l'API REST du projet CROUStillant. Elle expose toutes les données stockées en base (régions, restaurants, menus, plats) et est consommée par les différentes interfaces du projet (site web, bot Discord, application mobile, etc.).

Fonctionnalités principales :
- Liste et détails des restaurants universitaires (filtres par région, type, PMR, zone, statut d'ouverture)
- Menus et plats par restaurant et par date
- Widgets HTML intégrables (iframes) et exports d'images PNG des menus
- Rate limiting par IP / clé API avec buckets dynamiques
- Mise en cache Redis avec en-têtes `X-Cache` / `Cache-Control`
- Documentation OpenAPI interactive (Scalar UI) disponible à la racine

# 🛠️ • Technologies

| Composant | Technologie |
|---|---|
| Framework web | [Sanic](https://sanic.dev/) `>=24.12` |
| Base de données | [PostgreSQL](https://www.postgresql.org/) via [asyncpg](https://github.com/MagicStack/asyncpg) `>=0.30` |
| Cache | [Redis](https://redis.io/) via [redis-py](https://github.com/redis/redis-py) `>=5.2` |
| Client HTTP | [aiohttp](https://docs.aiohttp.org/) `>=3.11` |
| Templates | [Jinja2](https://jinja.palletsprojects.com/) `>=3.1` |
| Génération d'images | [Pillow](https://pillow.readthedocs.io/) `>=11.1` |
| Documentation API | [sanic-ext](https://github.com/PaulBayfield/sanic-ext) (fork) + [Scalar](https://scalar.com/) |
| Gestionnaire de paquets | [uv](https://github.com/astral-sh/uv) |
| Conteneurisation | [Docker](https://www.docker.com/) + [Docker Compose](https://docs.docker.com/compose/) |

# 📦 • Installation

### Avec Docker (recommandé)

Vous aurez besoin de [Docker](https://www.docker.com/) et de [Docker Compose](https://docs.docker.com/compose/).

```bash
git clone https://github.com/CROUStillant-Developpement/CROUStillantAPI
cd CROUStillantAPI
git submodule update --init --recursive
```

Créez un fichier `.env` à la racine du projet (voir [Variables d'environnement](#️--variables-denvironnement)), puis lancez :

```bash
docker-compose up
```

L'API sera disponible sur `http://localhost:5000`.

---

### En local (développement)

Vous aurez besoin de [Python 3.11+](https://www.python.org/) et de [uv](https://github.com/astral-sh/uv).

```bash
git clone https://github.com/CROUStillant-Developpement/CROUStillantAPI
cd CROUStillantAPI
git submodule update --init --recursive
uv sync
```

Créez un fichier `.env` à la racine du projet (voir ci-dessous), puis lancez :

```bash
uv run __main__.py
```

L'API sera disponible sur `http://localhost:5000` (ou le port défini dans `API_PORT`).

# ⚙️ • Variables d'environnement

Créez un fichier `.env` à la racine du projet en vous basant sur `.env.example` :

```env
# API
API_HOST=localhost
API_PORT=5000
API_DOMAIN=http://localhost:5000
API_DEBUG=False

# PostgreSQL
POSTGRES_DATABASE=CROUStillant
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
```

| Variable | Description | Valeur par défaut |
|---|---|---|
| `API_HOST` | Adresse d'écoute du serveur | `localhost` |
| `API_PORT` | Port d'écoute du serveur | `5000` |
| `API_DOMAIN` | URL publique de l'API (utilisée dans la doc OpenAPI) | `http://localhost:5000` |
| `API_DEBUG` | Active le mode debug Sanic (désactive le cache) | `False` |
| `POSTGRES_DATABASE` | Nom de la base de données | `CROUStillant` |
| `POSTGRES_USER` | Utilisateur PostgreSQL | — |
| `POSTGRES_PASSWORD` | Mot de passe PostgreSQL | — |
| `POSTGRES_HOST` | Hôte PostgreSQL | `localhost` |
| `POSTGRES_PORT` | Port PostgreSQL | `5432` |
| `REDIS_HOST` | Hôte Redis | `localhost` |
| `REDIS_PORT` | Port Redis | `6379` |

# 📡 • Endpoints

La documentation interactive complète est disponible à la racine de l'API (ex : `http://localhost:5000`).

| Préfixe | Description |
|---|---|
| `GET /v1/restaurants` | Liste des restaurants (filtres : région, type, PMR, zone, ouverture) |
| `GET /v1/restaurants/{code}` | Détails d'un restaurant |
| `GET /v1/restaurants/{code}/menu` | Menus à venir d'un restaurant |
| `GET /v1/restaurants/{code}/menu/{date}` | Menu d'un restaurant à une date donnée |
| `GET /v1/restaurants/{code}/menu/{date}/image` | Menu sous forme d'image PNG |
| `GET /v1/restaurants/{code}/menu/iframe` | Widget HTML du menu (aujourd'hui) |
| `GET /v1/restaurants/{code}/menu/{date}/iframe` | Widget HTML du menu (date précise) |
| `GET /v1/restaurants/{code}/iframe` | Widget HTML d'informations du restaurant |
| `GET /v1/restaurants/{code}/preview` | Image de prévisualisation du restaurant |
| `GET /v1/restaurants/status` | Statut d'ouverture de tous les restaurants |
| `GET /v1/regions` | Liste des régions |
| `GET /v1/regions/{code}` | Détails d'une région |
| `GET /v1/regions/{code}/restaurants` | Restaurants d'une région |
| `GET /v1/plats` | 100 derniers plats ajoutés |
| `GET /v1/plats/{code}` | Détails d'un plat |
| `GET /v1/plats/top` | Top 100 des plats les plus populaires |
| `GET /v1/taches` | Liste des tâches de mise à jour |
| `GET /v1/taches/{id}` | Détails d'une tâche |

# 📃 • Crédits

- [CROUStillant Développement](https://croustillant.menu/fr/about#team) - L'équipe de CROUStillant Développement

# 📝 • License

CROUStillant sous licence [Apache 2.0](LICENSE).

```
Copyright 2024 CROUStillant Développement

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
