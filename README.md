# Event Scheduler API

Flask REST API for the event-scheduler application.

## Prerequisites

- Python 3.12+
- MySQL 8+

## Setup

1. Create and activate a virtual environment:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create the MySQL database:

```sql
CREATE DATABASE event_scheduler CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

4. Copy environment variables:

```bash
cp .env.example .env
```

Edit `.env` with your database credentials and JWT secret.

5. Run the API:

```bash
python run.py
```

The server starts at `http://127.0.0.1:5000`.

## API Endpoints

### Auth
- `POST /api/auth/register` — Register (attendee or organiser)
- `POST /api/auth/login` — Login
- `POST /api/auth/logout` — Logout (authenticated)
- `GET /api/auth/profile` — Profile (authenticated)

### Attendees
- `POST /api/attendees` — Create (public)
- `GET /api/attendees/:id` — Get (owner)
- `PUT /api/attendees/:id` — Update (owner)
- `DELETE /api/attendees/:id` — Delete (owner)

### Organisers
- `POST /api/organisers` — Create (public)
- `GET /api/organisers/:id` — Get (owner)
- `PUT /api/organisers/:id` — Update (owner)
- `DELETE /api/organisers/:id` — Delete (owner)

### Sessions
- `GET /api/sessions` — List (public, filter by track/time)
- `GET /api/sessions/:id` — Get (public)
- `POST /api/sessions` — Create (organiser)
- `PUT /api/sessions/:id` — Update (organiser owner)
- `DELETE /api/sessions/:id` — Delete (organiser owner)
- `GET /api/organiser/sessions` — My sessions (organiser)
- `GET /api/sessions/:id/popularity` — Popularity stats (public)

### Agenda
- `POST /api/agenda` — Add session (attendee, clash warning)
- `GET /api/agenda/my` — My agenda (attendee)
- `DELETE /api/agenda/:id` — Remove (attendee owner)
- `GET /api/agenda/my/download` — Download PDF (attendee)

## Production

```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```
