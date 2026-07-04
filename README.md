# Event Scheduler API

A Flask API for managing conference sessions and personal attendee agendas. Organisers create and manage sessions; attendees browse the public schedule and build a personal agenda with time-clash warnings and capacity checks.

**Base URL:** `http://127.0.0.1:5000`

---

## 1. Project Overview

This API powers an event-scheduling application with two user roles:

| Role          | Capabilities                                                                      |
| ------------- | --------------------------------------------------------------------------------- |
| **Organiser** | Create, update, and delete their own sessions; view booking counts                |
| **Attendee**  | Browse public sessions; add sessions to a personal agenda; download agenda as PDF |

### Technologies Used

| Technology             | Purpose                                                             |
| ---------------------- | ------------------------------------------------------------------- |
| **Flask 3.x**          | Web framework (application factory pattern)                         |
| **Flask-SQLAlchemy**   | ORM integration                                                     |
| **SQLAlchemy 2.x**     | Database models and queries                                         |
| **PyMySQL**            | MySQL database driver (`mysql+pymysql://...`)                       |
| **Flask-JWT-Extended** | JWT Bearer token authentication                                     |
| **python-dotenv**      | Load environment variables from `.env`                              |
| **flask-cors**         | Cross-origin requests (enabled in `run.py`)                         |
| **Werkzeug**           | Password hashing (`generate_password_hash` / `check_password_hash`) |
| **reportlab**          | PDF agenda export                                                   |
| **gunicorn**           | Production WSGI server                                              |

---

## 2. Installation Guide

### Step 1 — Clone the repository

```bash
git clone https://github.com/Thushanika2/event-scheduler-project-api.git
cd event-scheduler-project-api
```

### Step 2 — Create a virtual environment

```bash
python -m venv .venv
```

**Windows:**

```bash
.venv\Scripts\activate
```

**macOS / Linux:**

```bash
source .venv/bin/activate
```

### Step 3 — Install requirements

```bash
pip install -r requirements.txt
```

### Step 4 — Create the MySQL database

```sql
CREATE DATABASE event_scheduler CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Step 5 — Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your values (see [Section 3](#3-environment-variables)).

### Step 6 — Run the server

```bash
python run.py
```

The API starts at **http://127.0.0.1:5000**. Database tables are created automatically on first run via `db.create_all()`.

### Production

```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

---

## 3. Environment Variables

This project reads the following variables from `.env` (see `app/config.py`):

| Variable                           | Required | Default     | Description                              |
| ---------------------------------- | -------- | ----------- | ---------------------------------------- |
| `DB_USER`                          | Yes      | —           | MySQL username                           |
| `DB_PASSWORD`                      | Yes      | —           | MySQL password                           |
| `DB_HOST`                          | Yes      | —           | MySQL host (e.g. `127.0.0.1`)            |
| `DB_NAME`                          | Yes      | —           | Database name (e.g. `event_scheduler`)   |
| `JWT_SECRET_KEY`                   | No       | `change-me` | Secret key for signing JWT tokens        |
| `JWT_ACCESS_TOKEN_EXPIRES_MINUTES` | No       | `60`        | Token expiry in minutes                  |
| `FLASK_DEBUG`                      | No       | `false`     | Set to `true` to enable Flask debug mode |

**Example `.env` file:**

```env
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_NAME=event_scheduler
JWT_SECRET_KEY=change-me-in-production
JWT_ACCESS_TOKEN_EXPIRES_MINUTES=60
FLASK_DEBUG=true
```

> **Note:** This project builds the database URI from `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_NAME`. It does not use `DATABASE_URL`, `FLASK_APP`, `FLASK_ENV`, or `SECRET_KEY`.

---

## 4. API Documentation

### Response Conventions

| Pattern                        | HTTP Status                   | Example                                                            |
| ------------------------------ | ----------------------------- | ------------------------------------------------------------------ |
| Validation errors (multiple)   | `400`                         | `{"errors": ["Email is required."]}`                               |
| Single business/auth error     | `401` / `403` / `404` / `400` | `{"error": "Session not found."}`                                  |
| Create success                 | `201`                         | `{"message": "...", "<entity>": {...}}`                            |
| Read / update / delete success | `200`                         | `{"message": "...", "<entity>": {...}}` or `{"<entities>": [...]}` |

---

## Authentication Endpoints

### Register User (Attendee)

**Method:** `POST`

**Route:** `/api/auth/register`

**Headers:**

```
Content-Type: application/json
```

**Thunder Client Body:**

```json
{
  "email": "jane.attendee@example.com",
  "password": "secret12",
  "role": "attendee",
  "full_name": "Jane Doe",
  "phone": "+94 77 123 4567"
}
```

**Success Response — `201`:**

```json
{
  "message": "Registration successful.",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "jane.attendee@example.com",
    "role": "attendee",
    "is_active": true,
    "created_at": "2026-07-04T14:00:00"
  }
}
```

**Error Response — `400`:**

```json
{
  "errors": ["Email is required.", "Password must be at least 6 characters."]
}
```

**Error Response — `400` (duplicate email):**

```json
{
  "errors": ["Email is already registered."]
}
```

**Error Response — `500`:**

```json
{
  "error": "Registration failed."
}
```

---

### Register User (Organiser)

**Method:** `POST`

**Route:** `/api/auth/register`

**Headers:**

```
Content-Type: application/json
```

**Thunder Client Body:**

```json
{
  "email": "john.organiser@example.com",
  "password": "secret12",
  "role": "organiser",
  "full_name": "John Smith",
  "organisation": "Tech Events Ltd",
  "phone": "+94 77 987 6543"
}
```

**Success Response — `201`:**

```json
{
  "message": "Registration successful.",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 2,
    "email": "john.organiser@example.com",
    "role": "organiser",
    "is_active": true,
    "created_at": "2026-07-04T14:05:00"
  }
}
```

**Error Response — `400`:**

```json
{
  "errors": ["Organisation is required for organisers."]
}
```

---

### Login

**Method:** `POST`

**Route:** `/api/auth/login`

**Headers:**

```
Content-Type: application/json
```

**Thunder Client Body:**

```json
{
  "email": "jane.attendee@example.com",
  "password": "secret12"
}
```

**Success Response — `200`:**

```json
{
  "message": "Login successful.",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "jane.attendee@example.com",
    "role": "attendee",
    "is_active": true,
    "created_at": "2026-07-04T14:00:00"
  }
}
```

**Error Response — `400`:**

```json
{
  "errors": ["Email and password are required."]
}
```

**Error Response — `401`:**

```json
{
  "error": "Invalid email or password."
}
```

**Error Response — `403`:**

```json
{
  "error": "Account is inactive."
}
```

---

### Logout

**Method:** `POST`

**Route:** `/api/auth/logout`

**Headers:**

```
Content-Type: application/json
Authorization: Bearer <access_token>
```

**Thunder Client Body:** none

**Success Response — `200`:**

```json
{
  "message": "Logout successful."
}
```

**Error Response — `401`:**

```json
{
  "error": "Unauthorized."
}
```

**Error Response — `403`:**

```json
{
  "error": "Forbidden."
}
```

---

### Get Profile

**Method:** `GET`

**Route:** `/api/auth/profile`

**Headers:**

```
Authorization: Bearer <access_token>
```

**Thunder Client Body:** none

**Success Response — `200` (attendee):**

```json
{
  "user": {
    "id": 1,
    "email": "jane.attendee@example.com",
    "role": "attendee",
    "is_active": true,
    "created_at": "2026-07-04T14:00:00",
    "attendee": {
      "id": 1,
      "user_id": 1,
      "full_name": "Jane Doe",
      "phone": "+94 77 123 4567"
    }
  }
}
```

**Success Response — `200` (organiser):**

```json
{
  "user": {
    "id": 2,
    "email": "john.organiser@example.com",
    "role": "organiser",
    "is_active": true,
    "created_at": "2026-07-04T14:05:00",
    "organiser": {
      "id": 1,
      "user_id": 2,
      "full_name": "John Smith",
      "organisation": "Tech Events Ltd",
      "phone": "+94 77 987 6543"
    }
  }
}
```

---

## Attendee Endpoints

### Create Attendee

**Method:** `POST`

**Route:** `/api/attendees`

**Headers:**

```
Content-Type: application/json
```

**Thunder Client Body:**

```json
{
  "email": "bob.attendee@example.com",
  "password": "secret12",
  "full_name": "Bob Wilson",
  "phone": "+94 71 555 1234"
}
```

**Success Response — `201`:**

```json
{
  "message": "Attendee created.",
  "attendee": {
    "id": 2,
    "user_id": 3,
    "full_name": "Bob Wilson",
    "phone": "+94 71 555 1234"
  }
}
```

**Error Response — `400`:**

```json
{
  "errors": ["Email is already registered."]
}
```

**Error Response — `500`:**

```json
{
  "error": "Failed to create attendee."
}
```

---

### Get Attendee

**Method:** `GET`

**Route:** `/api/attendees/:id`

**Headers:**

```
Authorization: Bearer <access_token>
```

**Thunder Client Body:** none

> Requires role `attendee`. The authenticated user must own the profile (`attendee_id` must match).

**Success Response — `200`:**

```json
{
  "attendee": {
    "id": 1,
    "user_id": 1,
    "full_name": "Jane Doe",
    "phone": "+94 77 123 4567"
  }
}
```

**Error Response — `403`:**

```json
{
  "error": "Forbidden."
}
```

**Error Response — `404`:**

```json
{
  "error": "Attendee not found."
}
```

---

### Update Attendee

**Method:** `PUT`

**Route:** `/api/attendees/:id`

**Headers:**

```
Content-Type: application/json
Authorization: Bearer <access_token>
```

**Thunder Client Body:**

```json
{
  "full_name": "Jane Doe Updated",
  "phone": "+94 77 999 8888"
}
```

**Success Response — `200`:**

```json
{
  "message": "Attendee updated.",
  "attendee": {
    "id": 1,
    "user_id": 1,
    "full_name": "Jane Doe Updated",
    "phone": "+94 77 999 8888"
  }
}
```

**Error Response — `400`:**

```json
{
  "errors": ["Full name is required."]
}
```

**Error Response — `404`:**

```json
{
  "error": "Attendee not found."
}
```

---

### Delete Attendee

**Method:** `DELETE`

**Route:** `/api/attendees/:id`

**Headers:**

```
Authorization: Bearer <access_token>
```

**Thunder Client Body:** none

**Success Response — `200`:**

```json
{
  "message": "Attendee deleted."
}
```

**Error Response — `404`:**

```json
{
  "error": "Attendee not found."
}
```

**Error Response — `500`:**

```json
{
  "error": "Failed to delete attendee."
}
```

---

## Organiser Endpoints

### Create Organiser

**Method:** `POST`

**Route:** `/api/organisers`

**Headers:**

```
Content-Type: application/json
```

**Thunder Client Body:**

```json
{
  "email": "sara.organiser@example.com",
  "password": "secret12",
  "full_name": "Sara Perera",
  "organisation": "EventCo",
  "phone": "+94 76 444 5555"
}
```

**Success Response — `201`:**

```json
{
  "message": "Organiser created.",
  "organiser": {
    "id": 2,
    "user_id": 4,
    "full_name": "Sara Perera",
    "organisation": "EventCo",
    "phone": "+94 76 444 5555"
  }
}
```

**Error Response — `400`:**

```json
{
  "errors": ["Organisation is required."]
}
```

**Error Response — `500`:**

```json
{
  "error": "Failed to create organiser."
}
```

---

### Get Organiser

**Method:** `GET`

**Route:** `/api/organisers/:id`

**Headers:**

```
Authorization: Bearer <access_token>
```

**Thunder Client Body:** none

> Requires role `organiser`. The authenticated user must own the profile.

**Success Response — `200`:**

```json
{
  "organiser": {
    "id": 1,
    "user_id": 2,
    "full_name": "John Smith",
    "organisation": "Tech Events Ltd",
    "phone": "+94 77 987 6543"
  }
}
```

**Error Response — `403`:**

```json
{
  "error": "Forbidden."
}
```

**Error Response — `404`:**

```json
{
  "error": "Organiser not found."
}
```

---

### Update Organiser

**Method:** `PUT`

**Route:** `/api/organisers/:id`

**Headers:**

```
Content-Type: application/json
Authorization: Bearer <access_token>
```

**Thunder Client Body:**

```json
{
  "full_name": "John Smith Updated",
  "organisation": "Tech Events International",
  "phone": "+94 77 111 2222"
}
```

**Success Response — `200`:**

```json
{
  "message": "Organiser updated.",
  "organiser": {
    "id": 1,
    "user_id": 2,
    "full_name": "John Smith Updated",
    "organisation": "Tech Events International",
    "phone": "+94 77 111 2222"
  }
}
```

**Error Response — `400`:**

```json
{
  "errors": ["Full name is required.", "Organisation is required."]
}
```

**Error Response — `404`:**

```json
{
  "error": "Organiser not found."
}
```

---

### Delete Organiser

**Method:** `DELETE`

**Route:** `/api/organisers/:id`

**Headers:**

```
Authorization: Bearer <access_token>
```

**Thunder Client Body:** none

**Success Response — `200`:**

```json
{
  "message": "Organiser deleted."
}
```

**Error Response — `404`:**

```json
{
  "error": "Organiser not found."
}
```

**Error Response — `500`:**

```json
{
  "error": "Failed to delete organiser."
}
```

---

## Session Endpoints

### List Sessions (Public)

**Method:** `GET`

**Route:** `/api/sessions`

**Headers:** none required

**Query Parameters (all optional):**

| Parameter    | Example               | Description                             |
| ------------ | --------------------- | --------------------------------------- |
| `track`      | `Web Development`     | Filter by exact track name              |
| `start_time` | `2026-07-10T09:00:00` | Sessions starting on or after this time |
| `end_time`   | `2026-07-10T18:00:00` | Sessions ending on or before this time  |

**Example URL:**

```
GET http://127.0.0.1:5000/api/sessions?track=Web%20Development&start_time=2026-07-10T09:00:00
```

**Thunder Client Body:** none

**Success Response — `200`:**

```json
{
  "sessions": [
    {
      "id": 1,
      "organiser_id": 1,
      "title": "Intro to React",
      "speaker": "Alice Chen",
      "track": "Web Development",
      "room": "Hall A",
      "start_time": "2026-07-10T09:00:00",
      "end_time": "2026-07-10T10:30:00",
      "capacity": 50,
      "booking_count": 12,
      "is_full": false
    }
  ]
}
```

---

### Get Session (Public)

**Method:** `GET`

**Route:** `/api/sessions/:id`

**Headers:** none required

**Thunder Client Body:** none

**Success Response — `200`:**

```json
{
  "session": {
    "id": 1,
    "organiser_id": 1,
    "title": "Intro to React",
    "speaker": "Alice Chen",
    "track": "Web Development",
    "room": "Hall A",
    "start_time": "2026-07-10T09:00:00",
    "end_time": "2026-07-10T10:30:00",
    "capacity": 50,
    "booking_count": 12,
    "is_full": false
  }
}
```

**Error Response — `404`:**

```json
{
  "error": "Session not found."
}
```

---

### Create Session

**Method:** `POST`

**Route:** `/api/sessions`

**Headers:**

```
Content-Type: application/json
Authorization: Bearer <access_token>
```

> Requires role `organiser`.

**Thunder Client Body:**

```json
{
  "title": "Intro to React",
  "speaker": "Alice Chen",
  "track": "Web Development",
  "room": "Hall A",
  "start_time": "2026-07-10T09:00:00",
  "end_time": "2026-07-10T10:30:00",
  "capacity": 50
}
```

**Success Response — `201`:**

```json
{
  "message": "Session created.",
  "session": {
    "id": 1,
    "organiser_id": 1,
    "title": "Intro to React",
    "speaker": "Alice Chen",
    "track": "Web Development",
    "room": "Hall A",
    "start_time": "2026-07-10T09:00:00",
    "end_time": "2026-07-10T10:30:00",
    "capacity": 50,
    "booking_count": 0,
    "is_full": false
  }
}
```

**Error Response — `400`:**

```json
{
  "errors": ["Title is required.", "End time must be after start time."]
}
```

**Error Response — `403`:**

```json
{
  "error": "Organiser profile not found."
}
```

**Error Response — `500`:**

```json
{
  "error": "Failed to create session."
}
```

---

### Update Session

**Method:** `PUT`

**Route:** `/api/sessions/:id`

**Headers:**

```
Content-Type: application/json
Authorization: Bearer <access_token>
```

> Requires role `organiser`. Only the session owner can update.

**Thunder Client Body:**

```json
{
  "title": "Intro to React (Updated)",
  "speaker": "Alice Chen",
  "track": "Web Development",
  "room": "Hall A",
  "start_time": "2026-07-10T09:00:00",
  "end_time": "2026-07-10T10:30:00",
  "capacity": 60
}
```

**Success Response — `200`:**

```json
{
  "message": "Session updated.",
  "session": {
    "id": 1,
    "organiser_id": 1,
    "title": "Intro to React (Updated)",
    "speaker": "Alice Chen",
    "track": "Web Development",
    "room": "Hall A",
    "start_time": "2026-07-10T09:00:00",
    "end_time": "2026-07-10T10:30:00",
    "capacity": 60,
    "booking_count": 12,
    "is_full": false
  }
}
```

**Error Response — `403`:**

```json
{
  "error": "Forbidden."
}
```

**Error Response — `404`:**

```json
{
  "error": "Session not found."
}
```

---

### Delete Session

**Method:** `DELETE`

**Route:** `/api/sessions/:id`

**Headers:**

```
Authorization: Bearer <access_token>
```

> Requires role `organiser`. Only the session owner can delete.

**Thunder Client Body:** none

**Success Response — `200`:**

```json
{
  "message": "Session deleted."
}
```

**Error Response — `403`:**

```json
{
  "error": "Forbidden."
}
```

**Error Response — `404`:**

```json
{
  "error": "Session not found."
}
```

---

### Get Organiser Sessions

**Method:** `GET`

**Route:** `/api/organiser/sessions`

**Headers:**

```
Authorization: Bearer <access_token>
```

> Requires role `organiser`.

**Thunder Client Body:** none

**Success Response — `200`:**

```json
{
  "sessions": [
    {
      "id": 1,
      "organiser_id": 1,
      "title": "Intro to React",
      "speaker": "Alice Chen",
      "track": "Web Development",
      "room": "Hall A",
      "start_time": "2026-07-10T09:00:00",
      "end_time": "2026-07-10T10:30:00",
      "capacity": 50,
      "booking_count": 12,
      "is_full": false
    }
  ]
}
```

**Error Response — `403`:**

```json
{
  "error": "Organiser profile not found."
}
```

---

### Get Session Popularity (Public)

**Method:** `GET`

**Route:** `/api/sessions/:id/popularity`

**Headers:** none required

**Thunder Client Body:** none

**Success Response — `200`:**

```json
{
  "session_id": 1,
  "title": "Intro to React",
  "capacity": 50,
  "booking_count": 12,
  "is_full": false,
  "spots_remaining": 38
}
```

**Error Response — `404`:**

```json
{
  "error": "Session not found."
}
```

---

## Agenda Endpoints

### Add Session to Agenda

**Method:** `POST`

**Route:** `/api/agenda`

**Headers:**

```
Content-Type: application/json
Authorization: Bearer <access_token>
```

> Requires role `attendee`.

**Thunder Client Body:**

```json
{
  "session_id": 1
}
```

**Success Response — `201` (no clash):**

```json
{
  "message": "Session added to agenda.",
  "agenda_item": {
    "id": 1,
    "attendee_id": 1,
    "session_id": 1,
    "added_at": "2026-07-04T14:30:00",
    "session": {
      "id": 1,
      "organiser_id": 1,
      "title": "Intro to React",
      "speaker": "Alice Chen",
      "track": "Web Development",
      "room": "Hall A",
      "start_time": "2026-07-10T09:00:00",
      "end_time": "2026-07-10T10:30:00",
      "capacity": 50,
      "booking_count": 13,
      "is_full": false
    }
  }
}
```

**Success Response — `201` (with clash warning):**

```json
{
  "message": "Session added to agenda.",
  "agenda_item": {
    "id": 2,
    "attendee_id": 1,
    "session_id": 2,
    "added_at": "2026-07-04T14:31:00",
    "session": {
      "id": 2,
      "organiser_id": 1,
      "title": "Advanced TypeScript",
      "speaker": "Bob Lee",
      "track": "Web Development",
      "room": "Hall B",
      "start_time": "2026-07-10T09:30:00",
      "end_time": "2026-07-10T11:00:00",
      "capacity": 30,
      "booking_count": 1,
      "is_full": false
    }
  },
  "warning": "Time clash detected with: Intro to React"
}
```

**Error Response — `400`:**

```json
{
  "errors": ["Session ID is required."]
}
```

**Error Response — `400` (duplicate):**

```json
{
  "error": "Session is already in your agenda."
}
```

**Error Response — `400` (full):**

```json
{
  "error": "Session is full."
}
```

**Error Response — `404`:**

```json
{
  "error": "Session not found."
}
```

---

### Get My Agenda

**Method:** `GET`

**Route:** `/api/agenda/my`

**Headers:**

```
Authorization: Bearer <access_token>
```

> Requires role `attendee`. Results sorted by session start time ascending.

**Thunder Client Body:** none

**Success Response — `200`:**

```json
{
  "agenda_items": [
    {
      "id": 1,
      "attendee_id": 1,
      "session_id": 1,
      "added_at": "2026-07-04T14:30:00",
      "session": {
        "id": 1,
        "organiser_id": 1,
        "title": "Intro to React",
        "speaker": "Alice Chen",
        "track": "Web Development",
        "room": "Hall A",
        "start_time": "2026-07-10T09:00:00",
        "end_time": "2026-07-10T10:30:00",
        "capacity": 50,
        "booking_count": 13,
        "is_full": false
      }
    }
  ]
}
```

**Error Response — `403`:**

```json
{
  "error": "Attendee profile not found."
}
```

---

### Remove from Agenda

**Method:** `DELETE`

**Route:** `/api/agenda/:id`

**Headers:**

```
Authorization: Bearer <access_token>
```

> Requires role `attendee`. Only the agenda item owner can delete.

**Thunder Client Body:** none

**Success Response — `200`:**

```json
{
  "message": "Session removed from agenda."
}
```

**Error Response — `403`:**

```json
{
  "error": "Forbidden."
}
```

**Error Response — `404`:**

```json
{
  "error": "Agenda item not found."
}
```

---

### Download Agenda PDF

**Method:** `GET`

**Route:** `/api/agenda/my/download`

**Headers:**

```
Authorization: Bearer <access_token>
```

> Requires role `attendee`. Returns a PDF file, not JSON.

**Thunder Client Body:** none

**Success Response — `200`:**

- Content-Type: `application/pdf`
- Filename: `agenda_{attendee_id}.pdf`

---

## 5. Protected Routes

Routes marked with a lock require a valid JWT in the `Authorization` header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

| Route                                | Required Role             | Additional Rule              |
| ------------------------------------ | ------------------------- | ---------------------------- |
| `POST /api/auth/logout`              | `organiser` or `attendee` | Active account               |
| `GET /api/auth/profile`              | `organiser` or `attendee` | Active account               |
| `GET/PUT/DELETE /api/attendees/:id`  | `attendee`                | Must own profile             |
| `GET/PUT/DELETE /api/organisers/:id` | `organiser`               | Must own profile             |
| `POST/PUT/DELETE /api/sessions`      | `organiser`               | PUT/DELETE: must own session |
| `GET /api/organiser/sessions`        | `organiser`               | Must have organiser profile  |
| `POST/GET/DELETE /api/agenda/*`      | `attendee`                | DELETE: must own agenda item |

The `@roles_required` decorator (`app/middleware.py`) checks:

1. Valid JWT present
2. User exists and `is_active` is `true`
3. User role is in the allowed list

---

## 6. Thunder Client Testing

### Step-by-step guide

1. **Start the API**

   ```bash
   python run.py
   ```

2. **Register or login first** — call one of these before any protected route:
   - `POST http://127.0.0.1:5000/api/auth/register` (organiser recommended first to create sessions)
   - `POST http://127.0.0.1:5000/api/auth/login`

3. **Copy the `access_token`** from the JSON response.

4. **Add the Bearer token in Thunder Client:**
   - Open the **Auth** tab → select **Bearer Token**
   - Paste the token value (without the word `Bearer`)
   - Or add a header manually:

     ```
     Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
     ```

5. **Set Content-Type for POST/PUT requests:**

   ```
   Content-Type: application/json
   ```

6. **Paste the JSON body** from the endpoint documentation above into the **Body → JSON** tab.

### Recommended test sequence

| Step | Method | Route                     | Role                                         |
| ---- | ------ | ------------------------- | -------------------------------------------- |
| 1    | POST   | `/api/auth/register`      | organiser                                    |
| 2    | POST   | `/api/sessions`           | organiser token                              |
| 3    | POST   | `/api/sessions`           | organiser token (second overlapping session) |
| 4    | POST   | `/api/auth/register`      | attendee                                     |
| 5    | GET    | `/api/sessions`           | public (no token)                            |
| 6    | POST   | `/api/agenda`             | attendee token                               |
| 7    | POST   | `/api/agenda`             | attendee token (expect `warning`)            |
| 8    | GET    | `/api/agenda/my`          | attendee token                               |
| 9    | GET    | `/api/agenda/my/download` | attendee token (PDF)                         |

### Example — first request (register organiser)

**URL:** `POST http://127.0.0.1:5000/api/auth/register`

**Body:**

```json
{
  "email": "john.organiser@example.com",
  "password": "secret12",
  "role": "organiser",
  "full_name": "John Smith",
  "organisation": "Tech Events Ltd"
}
```

**Response:**

```json
{
  "message": "Registration successful.",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "john.organiser@example.com",
    "role": "organiser",
    "is_active": true,
    "created_at": "2026-07-04T14:00:00"
  }
}
```

Copy `access_token` → paste into Thunder Client **Bearer Token** field for all subsequent protected requests.

---

## 7. Project Structure

```
event-scheduler-project-api/
├── .env.example              # Environment variable template
├── requirements.txt          # Python dependencies
├── run.py                      # Entry point; enables CORS
└── app/
    ├── __init__.py             # Application factory (create_app)
    ├── config.py               # Config class from env vars
    ├── extensions.py           # Shared db + jwt instances
    ├── utils.py                # utc_now() helper
    ├── middleware.py           # roles_required decorator
    ├── models/
    │   ├── user_model.py
    │   ├── attendee_model.py
    │   ├── organiser_model.py
    │   ├── session_model.py
    │   └── agenda_item_model.py
    ├── controllers/
    │   ├── auth_controller.py
    │   ├── attendee_controller.py
    │   ├── organiser_controller.py
    │   ├── session_controller.py
    │   └── agenda_controller.py
    └── routes/
        ├── __init__.py         # register_blueprints()
        ├── auth_routes.py
        ├── attendee_routes.py
        ├── organiser_routes.py
        ├── session_routes.py
        └── agenda_routes.py
```

**Architecture pattern:**

- **Routes** — thin handlers; parse request, call controller, return JSON
- **Controllers** — validation, business logic, database operations
- **Models** — SQLAlchemy models with `to_dict()` serialization
- **Middleware** — JWT + role enforcement

---

## 8. Database Models

### users

| Field        | Type        | Constraints                         |
| ------------ | ----------- | ----------------------------------- |
| `id`         | Integer     | Primary key, autoincrement          |
| `email`      | String(255) | Unique, not null                    |
| `password`   | String(255) | Hashed, not null                    |
| `role`       | Enum        | `organiser` or `attendee`, not null |
| `is_active`  | Boolean     | Default `true`, not null            |
| `created_at` | DateTime    | Default `utc_now`, not null         |

### organisers

| Field          | Type        | Constraints                       |
| -------------- | ----------- | --------------------------------- |
| `id`           | Integer     | Primary key, autoincrement        |
| `user_id`      | Integer     | FK → `users.id`, unique, not null |
| `full_name`    | String(255) | Not null                          |
| `organisation` | String(255) | Not null                          |
| `phone`        | String(50)  | Nullable                          |

### attendees

| Field       | Type        | Constraints                       |
| ----------- | ----------- | --------------------------------- |
| `id`        | Integer     | Primary key, autoincrement        |
| `user_id`   | Integer     | FK → `users.id`, unique, not null |
| `full_name` | String(255) | Not null                          |
| `phone`     | String(50)  | Nullable                          |

### sessions

| Field          | Type        | Constraints                    |
| -------------- | ----------- | ------------------------------ |
| `id`           | Integer     | Primary key, autoincrement     |
| `organiser_id` | Integer     | FK → `organisers.id`, not null |
| `title`        | String(255) | Not null                       |
| `speaker`      | String(255) | Not null                       |
| `track`        | String(100) | Not null                       |
| `room`         | String(100) | Not null                       |
| `start_time`   | DateTime    | Not null                       |
| `end_time`     | DateTime    | Not null                       |
| `capacity`     | Integer     | Not null                       |

### agenda_items

| Field         | Type     | Constraints                   |
| ------------- | -------- | ----------------------------- |
| `id`          | Integer  | Primary key, autoincrement    |
| `attendee_id` | Integer  | FK → `attendees.id`, not null |
| `session_id`  | Integer  | FK → `sessions.id`, not null  |
| `added_at`    | DateTime | Default `utc_now`, not null   |

**Unique constraint:** `(attendee_id, session_id)` — one booking per attendee per session.

### Relationships

```
Users
├── Attendee ─── Agenda Items ─── Sessions ─── Organiser
└── Organiser ── Sessions
```

---

## 9. Validation Rules

### Auth — Register (`auth_controller.py`)

| Field          | Rule                                                      |
| -------------- | --------------------------------------------------------- |
| `email`        | Required; must not already exist                          |
| `password`     | Required; minimum 6 characters                            |
| `role`         | Must be `attendee` or `organiser`; defaults to `attendee` |
| `full_name`    | Required                                                  |
| `organisation` | Required when `role` is `organiser`                       |
| `phone`        | Optional                                                  |

### Auth — Login

| Field      | Rule     |
| ---------- | -------- |
| `email`    | Required |
| `password` | Required |

### Attendee — Create

| Field       | Rule                             |
| ----------- | -------------------------------- |
| `email`     | Required; must not already exist |
| `password`  | Required; minimum 6 characters   |
| `full_name` | Required                         |
| `phone`     | Optional                         |

### Attendee — Update

| Field       | Rule     |
| ----------- | -------- |
| `full_name` | Required |
| `phone`     | Optional |

### Organiser — Create

| Field          | Rule                             |
| -------------- | -------------------------------- |
| `email`        | Required; must not already exist |
| `password`     | Required; minimum 6 characters   |
| `full_name`    | Required                         |
| `organisation` | Required                         |
| `phone`        | Optional                         |

### Organiser — Update

| Field          | Rule     |
| -------------- | -------- |
| `full_name`    | Required |
| `organisation` | Required |
| `phone`        | Optional |

### Session — Create / Update

| Field        | Rule                                                   |
| ------------ | ------------------------------------------------------ |
| `title`      | Required                                               |
| `speaker`    | Required                                               |
| `track`      | Required                                               |
| `room`       | Required                                               |
| `start_time` | Required; ISO 8601 format (e.g. `2026-07-10T09:00:00`) |
| `end_time`   | Required; must be after `start_time`                   |
| `capacity`   | Required; integer ≥ 1                                  |

### Agenda — Add

| Field        | Rule                                                  |
| ------------ | ----------------------------------------------------- |
| `session_id` | Required                                              |
| —            | Session must exist                                    |
| —            | Must not already be in attendee's agenda              |
| —            | Session must not be at capacity                       |
| —            | Time clash returns `warning` but still saves the item |

---

## 10. Error Codes

| HTTP Status | When Used                                                                           | Response Shape                            |
| ----------- | ----------------------------------------------------------------------------------- | ----------------------------------------- |
| **200**     | Successful GET, PUT, DELETE                                                         | `{"message": "..."}` or entity object     |
| **201**     | Successful POST (create)                                                            | `{"message": "...", "<entity>": {...}}`   |
| **400**     | Validation failure or business rule                                                 | `{"errors": [...]}` or `{"error": "..."}` |
| **401**     | Missing/invalid JWT, wrong credentials, inactive user treated as unauthorized       | `{"error": "..."}`                        |
| **403**     | Wrong role, not owner, inactive account (login), organiser/attendee profile missing | `{"error": "Forbidden."}`                 |
| **404**     | Entity not found                                                                    | `{"error": "<Entity> not found."}`        |
| **500**     | Server/database operation failure                                                   | `{"error": "..."}`                        |
| **503**     | MySQL connection error                                                              | `{"error": "Database connection error."}` |

### Common error messages

| Message                                | Cause                                    |
| -------------------------------------- | ---------------------------------------- |
| `"Unauthorized."`                      | Invalid or missing JWT; inactive user    |
| `"Forbidden."`                         | Wrong role or not the resource owner     |
| `"Invalid email or password."`         | Login credentials incorrect              |
| `"Account is inactive."`               | User `is_active` is `false`              |
| `"Session is full."`                   | Agenda booking exceeds session capacity  |
| `"Session is already in your agenda."` | Duplicate agenda entry                   |
| `"Time clash detected with: ..."`      | Warning (not an error); item still added |

---

## 11. Authentication Flow

```
Register (POST /api/auth/register)
        ↓
  User + Profile created
  access_token returned
        ↓
Login (POST /api/auth/login)          ← alternative entry point
        ↓
  access_token returned
        ↓
Add header: Authorization: Bearer <access_token>
        ↓
Access protected routes
  (sessions, agenda, profile, etc.)
        ↓
Logout (POST /api/auth/logout)
```

**Token details:**

- Signed with `JWT_SECRET_KEY`
- Identity claim (`sub`) = user ID (string)
- Expires after `JWT_ACCESS_TOKEN_EXPIRES_MINUTES` (default: 60 minutes)
- User lookup via `@jwt.user_lookup_loader` in `app/__init__.py`

---

## 12. Sample API Flow

### Organiser flow — manage sessions

```
Register Organiser (POST /api/auth/register)
        ↓
Create Session (POST /api/sessions)
        ↓
Get All Sessions (GET /api/sessions)
        ↓
Get My Sessions (GET /api/organiser/sessions)
        ↓
Update Session (PUT /api/sessions/:id)
        ↓
Get Session Popularity (GET /api/sessions/:id/popularity)
        ↓
Delete Session (DELETE /api/sessions/:id)
```

### Attendee flow — build agenda

```
Register Attendee (POST /api/auth/register)
        ↓
Browse Schedule (GET /api/sessions)
        ↓
Add to Agenda (POST /api/agenda)
        ↓
Add Overlapping Session (POST /api/agenda)  → receives warning
        ↓
View My Agenda (GET /api/agenda/my)
        ↓
Download PDF (GET /api/agenda/my/download)
        ↓
Remove Session (DELETE /api/agenda/:id)
```

---

## 13. Notes

### HTTP methods

This API uses **POST**, **GET**, **PUT**, and **DELETE** only. There are **no PATCH** endpoints.

### Default values

| Item                  | Default                              |
| --------------------- | ------------------------------------ |
| User role on register | `attendee`                           |
| User `is_active`      | `true`                               |
| JWT expiry            | 60 minutes                           |
| JWT secret            | `change-me` (override in production) |
| Flask debug           | `false`                              |

### Filtering and sorting

| Feature                 | Details                                         |
| ----------------------- | ----------------------------------------------- |
| Session list filter     | Query params: `track`, `start_time`, `end_time` |
| Session list sort       | Ordered by `start_time` ascending               |
| Organiser sessions sort | Ordered by `start_time` ascending               |
| Agenda list sort        | Ordered by session `start_time` ascending       |

### Pagination

Not implemented. All list endpoints return full result sets.

### Capacity and booking

- `booking_count` and `is_full` are included when sessions are serialized with `include_booking_count=True`
- A session is full when `booking_count >= capacity`
- Agenda add is rejected with `"Session is full."` when at capacity

### Time clash detection

- Overlap check: `session_a.start < session_b.end AND session_b.start < session_a.end`
- Clash returns a `warning` string in the response but **still saves** the agenda item

### Date/time format

- Accepts ISO 8601 strings (e.g. `2026-07-10T09:00:00` or with `Z` suffix)
- Stored and returned as ISO format via `.isoformat()`

### CORS

Enabled globally in `run.py` via `flask-cors` for frontend integration.

### Related repository

Frontend (Next.js): [event-scheduler-project-client](https://github.com/Thushanika2/event-scheduler-project-client)
