# TP CI/CD — Python Full-Stack Application

A two-service Python web application (backend REST API + frontend web UI) backed by a MySQL database, fully containerised with Docker Compose and ready for VS Code Dev Containers.

---

## Table of Contents

- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [With Docker Compose](#with-docker-compose)
  - [With VS Code Dev Container](#with-vs-code-dev-container)
- [Services](#services)
  - [Backend](#backend)
  - [Frontend](#frontend)
  - [Database](#database)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Dependencies](#dependencies)
- [Development Notes](#development-notes)

---

## Project Structure

```
tp-ci-cd-ak/
├── .devcontainer/
│   └── devcontainer.json        # VS Code Dev Container configuration
├── backend-tp_ci_cd/
│   ├── app.py                   # Flask REST API
│   ├── Dockerfile               # Backend container image
│   └── .dockerignore
├── frontend-tp_ci_cd/
│   ├── app.py                   # Flask web UI
│   ├── Dockerfile               # Frontend container image
│   └── .dockerignore
├── docker-compose.yml           # Orchestrates all three services
├── requirements.txt             # Shared Python dependencies
└── ReadMe.md
```

---

## Tech Stack

| Layer     | Technology              |
|-----------|-------------------------|
| Backend   | Python 3.12 · Flask 3   |
| Frontend  | Python 3.12 · Flask 3   |
| Database  | MySQL 8.4               |
| ORM       | Flask-SQLAlchemy 3      |
| Container | Docker · Docker Compose |
| Dev Env   | VS Code Dev Containers  |

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) ≥ 24
- [Docker Compose](https://docs.docker.com/compose/) v2 (`docker compose`)
- *(optional)* [VS Code](https://code.visualstudio.com/) + [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

---

## Getting Started

### With Docker Compose

```bash
# Clone the repository
git clone <repository-url>
cd tp-ci-cd-ak

# Build images and start all services
docker compose up --build

# Run in detached mode
docker compose up --build -d

# Stop all services
docker compose down

# Stop and remove volumes (deletes database data)
docker compose down -v
```

Once running:

| Service  | URL                        |
|----------|----------------------------|
| Frontend | http://localhost:5001       |
| Backend  | http://localhost:5000       |
| MySQL    | localhost:3306             |

### With VS Code Dev Container

1. Open the repository folder in VS Code.
2. When prompted *"Reopen in Container"*, click **Reopen in Container**.  
   Alternatively, open the Command Palette (`Ctrl+Shift+P`) and run **Dev Containers: Reopen in Container**.
3. VS Code will start all Docker Compose services and attach to the `backend` container.
4. Port `5001` (frontend) is automatically opened in the browser; ports `5000` and `3306` are forwarded.

---

## Services

### Backend

- **Image built from:** `backend-tp_ci_cd/Dockerfile`
- **Port:** `5000`
- **Entry point:** `backend-tp_ci_cd/app.py`

A Flask REST API that manages `Item` records stored in MySQL. It exposes a health-check endpoint and a full CRUD interface for items. On startup, SQLAlchemy automatically creates the `items` table if it does not exist.

The backend waits for the `db` service to pass its healthcheck before starting, ensuring the database is ready to accept connections.

### Frontend

- **Image built from:** `frontend-tp_ci_cd/Dockerfile`
- **Port:** `5001`
- **Entry point:** `frontend-tp_ci_cd/app.py`

A Flask web application that communicates with the backend via HTTP (`requests`). It displays a live list of items, shows the backend health status, and allows users to add or delete items through an HTML form.

### Database

- **Image:** `mysql:8.4`
- **Port:** `3306`
- **Credentials (dev):**

  | Parameter | Value        |
  |-----------|--------------|
  | Database  | `appdb`      |
  | User      | `appuser`    |
  | Password  | `apppassword`|
  | Root pw   | `rootpassword`|

- Data is persisted in the named Docker volume `db_data`.

---

## Environment Variables

### Backend (`backend` service)

| Variable       | Default                                              | Description                    |
|----------------|------------------------------------------------------|--------------------------------|
| `DATABASE_URL` | `mysql+pymysql://appuser:apppassword@db:3306/appdb`  | SQLAlchemy connection string   |
| `FLASK_DEBUG`  | `true`                                               | Enable Flask debug/reload mode |

### Frontend (`frontend` service)

| Variable      | Default                  | Description                        |
|---------------|--------------------------|------------------------------------|
| `BACKEND_URL` | `http://backend:5000`    | Base URL of the backend API        |
| `FLASK_DEBUG` | `true`                   | Enable Flask debug/reload mode     |
| `SECRET_KEY`  | `change-me-in-production`| Flask session secret key           |

> **Note:** Override these values with a `.env` file or by editing `docker-compose.yml` for production deployments.

---

## API Reference

Base URL: `http://localhost:5000`

| Method   | Endpoint              | Description              | Request Body                          |
|----------|-----------------------|--------------------------|---------------------------------------|
| `GET`    | `/api/health`         | Health check             | —                                     |
| `GET`    | `/api/items`          | List all items           | —                                     |
| `POST`   | `/api/items`          | Create a new item        | `{ "name": "...", "description": "..." }` |
| `DELETE` | `/api/items/<id>`     | Delete an item by ID     | —                                     |

#### Example: create an item

```bash
curl -X POST http://localhost:5000/api/items \
  -H "Content-Type: application/json" \
  -d '{"name": "My item", "description": "Optional description"}'
```

#### Example: list all items

```bash
curl http://localhost:5000/api/items
```

---

## Dependencies

All Python packages are pinned in the shared [requirements.txt](requirements.txt) and installed into both service images at build time.

| Package             | Version  | Purpose                              |
|---------------------|----------|--------------------------------------|
| `flask`             | 3.0.3    | Web framework (backend & frontend)   |
| `flask-sqlalchemy`  | 3.1.1    | ORM / database abstraction layer     |
| `PyMySQL`           | 1.1.1    | Pure-Python MySQL driver             |
| `python-dotenv`     | 1.0.1    | Load environment variables from `.env`|
| `requests`          | 2.31.0   | HTTP client (frontend → backend)     |
| `cryptography`      | 42.0.5   | Required by PyMySQL for SSL support  |

---

## Development Notes

- **Hot reload** — Both service containers mount their source folders as volumes (`./backend-tp_ci_cd:/app` and `./frontend-tp_ci_cd:/app`), so code changes are reflected immediately without rebuilding the image (Flask debug mode handles the reload).
- **Shared dependencies** — `requirements.txt` is mounted into both containers at `/app/requirements.txt`. Adding a new package there and restarting the container (`docker compose restart backend`) is enough during development.
- **Database reset** — Run `docker compose down -v` to wipe the `db_data` volume and start with a fresh database.
- **Production checklist** — Before deploying to production, change `SECRET_KEY`, `MYSQL_ROOT_PASSWORD`, `MYSQL_PASSWORD`, and set `FLASK_DEBUG=false`.
