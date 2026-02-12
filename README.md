# Used Machine Pipeline

Produktionsnahes MVP zur Steuerung einer Gebrauchtmaschinen-Pipeline mit 4 Status über drei Aufbereitungsstandorte (Passau, Andernach, Welzow).

## Stack

- Backend: FastAPI + SQLAlchemy + Alembic
- Datenbank: PostgreSQL
- Frontend: React + Vite + TypeScript + MUI
- Auth: JWT Login (Admin / SiteUser)
- Container: Docker + Docker Compose

## Quickstart

```bash
docker-compose up --build
```

Services:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Swagger: http://localhost:8000/docs

## Login-Daten (Seed)

- `admin` / `admin123`
- `passau_user` / `site123`
- `andernach_user` / `site123`
- `welzow_user` / `site123`

## API Endpoints

- `POST /auth/login`
- `GET /machines`
- `POST /machines`
- `PUT /machines/{id}`
- `GET /dashboard/operations`
- `GET /dashboard/site-worklist`
- `GET /dashboard/period-summary?days=30`

## Geschäftslogik

- Statusvalidierung inkl. Pflichtfeldern beim Übergang.
- Chronologische Datumsvalidierung.
- KPI-Berechnung pro Maschine inkl. Ampellogik (GREEN < 30, YELLOW 30-45, RED > 45 Tage).
- Operatives Dashboard mit Transport-, Intake- und Werkstatt-Transparenzblöcken.
- Zeitraum-Übersicht im Dashboard (7/30/90 Tage) mit aggregierten Arrival-/Completion- und Durchlauf-KPIs.
- Standort-Arbeitsliste mit Priorisierung (Rot, Gelb, Marktwert, Alter).
- SiteUser darf nur Maschinen des eigenen `refurb_site` ändern.

## Projektstruktur

- `backend/app`: FastAPI App, Modelle, Services, API Router
- `backend/alembic`: Migrationen
- `backend/scripts/seed.py`: Seed-Daten
- `frontend/src`: React UI

## Hinweise

- Die Backend-Start-Command führt automatisch Migration + Seed aus.
- Passe sensible Konfigurationen über `.env` an.
