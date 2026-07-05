# AgendaFlow API — Flask + MySQL + JWT

REST API built with Flask, SQLAlchemy ORM, MySQL, and JWT authentication. Manages **conference sessions**, **personal agendas**, and **user profiles** for organisers, attendees, and an admin.

Protected routes require:

```
Authorization: Bearer <access_token>
```

---

## Setup

```bash
# 1. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create a .env file in the project root
cp .env.example .env             # then fill in your credentials

# 4. Create the database in MySQL
mysql -u root -p -e "CREATE DATABASE event_scheduler CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 5. Run the app (tables are created automatically on first start)
python run.py
```

## Environment Variables (`.env`)

| Variable                           | Description                    | Default      |
| ---------------------------------- | ------------------------------ | ------------ |
| `DB_USER`                          | MySQL username                 | —            |
| `DB_PASSWORD`                      | MySQL password                 | —            |
| `DB_HOST`                          | MySQL host                     | —            |
| `DB_NAME`                          | Database name                  | —            |
| `JWT_SECRET_KEY`                   | Secret key for JWT signing     | `change-me`  |
| `JWT_ACCESS_TOKEN_EXPIRES_MINUTES` | Token expiry in minutes        | `60`         |
| `FLASK_DEBUG`                      | Enable debug mode              | `false`      |

---

## API Testing

Base URL: `http://localhost:5000`

---

### Auth

#### GET `/api/auth/admin-registration-status` — Check if admin signup is open

No request body needed.

**Success response `200`**
```json
{
  "available": true
}
```

---

#### POST `/api/auth/register` — Register attendee

```json
{
  "email": "jane.attendee@example.com",
  "password": "secret12",
  "role": "attendee",
  "full_name": "Jane Doe",
  "phone": "+94 77 123 4567"
}
```

**Success response `201`**
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

**Validation error `400`**
```json
{
  "errors": [
    "Email is required.",
    "Password must be at least 6 characters."
  ]
}
```

**Duplicate email `400`**
```json
{
  "errors": ["Email is already registered."]
}
```

---

#### POST `/api/auth/register` — Register organiser

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

**Success response `201`**
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

**Validation error `400`**
```json
{
  "errors": ["Organisation is required for organisers."]
}
```

---

#### POST `/api/auth/register` — Register admin (first account only)

```json
{
  "email": "admin@example.com",
  "password": "secret12",
  "role": "admin"
}
```

**Success response `201`**
```json
{
  "message": "Registration successful.",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 3,
    "email": "admin@example.com",
    "role": "admin",
    "is_active": true,
    "created_at": "2026-07-04T14:10:00"
  }
}
```

**Admin already exists `400`**
```json
{
  "errors": [
    "An administrator account already exists. Admin registration is disabled."
  ]
}
```

---

#### POST `/api/auth/login` — Login

```json
{
  "email": "jane.attendee@example.com",
  "password": "secret12"
}
```

**Success response `200`**
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

**Invalid credentials `401`**
```json
{
  "error": "Invalid email or password."
}
```

**Inactive account `403`**
```json
{
  "error": "Account is inactive."
}
```

---

#### POST `/api/auth/logout` — Logout

Requires Bearer token.

No request body needed.

**Success response `200`**
```json
{
  "message": "Logout successful."
}
```

---

#### GET `/api/auth/profile` — Get current user profile

Requires Bearer token.

No request body needed.

**Success response `200` (attendee)**
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

---

### Sessions

#### GET `/api/sessions` — List all sessions (public)

Optional query params: `track`, `start_time`, `end_time`

Example: `GET /api/sessions?track=Web%20Development&start_time=2026-07-10T09:00:00`

No request body needed.

**Success response `200`**
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

#### GET `/api/sessions/1` — Get one session (public)

No request body needed.

**Success response `200`**
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

**Not found `404`**
```json
{
  "error": "Session not found."
}
```

---

#### POST `/api/sessions` — Create a session

Requires organiser Bearer token.

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

**More sample session payloads**

```json
{
  "title": "Advanced TypeScript",
  "speaker": "Bob Lee",
  "track": "Web Development",
  "room": "Hall B",
  "start_time": "2026-07-10T09:30:00",
  "end_time": "2026-07-10T11:00:00",
  "capacity": 30
}
```

```json
{
  "title": "Cloud Architecture Patterns",
  "speaker": "Sara Perera",
  "track": "DevOps",
  "room": "Room 201",
  "start_time": "2026-07-10T11:00:00",
  "end_time": "2026-07-10T12:30:00",
  "capacity": 40
}
```

**Success response `201`**
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

**Validation error `400`**
```json
{
  "errors": [
    "Title is required.",
    "End time must be after start time."
  ]
}
```

---

#### PUT `/api/sessions/1` — Update a session

Requires organiser Bearer token (must own the session).

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

**Success response `200`**
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

**Forbidden `403`**
```json
{
  "error": "Forbidden."
}
```

---

#### DELETE `/api/sessions/1` — Delete a session

Requires organiser Bearer token (must own the session).

No request body needed.

**Success response `200`**
```json
{
  "message": "Session deleted."
}
```

---

#### GET `/api/sessions/1/popularity` — Session booking stats (public)

No request body needed.

**Success response `200`**
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

---

#### GET `/api/organiser/sessions` — List own sessions

Requires organiser Bearer token.

No request body needed.

**Success response `200`**
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

### Agenda

#### POST `/api/agenda` — Add session to personal agenda

Requires attendee Bearer token.

```json
{
  "session_id": 1
}
```

**Success response `201`**
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

**Time clash warning `201`**
```json
{
  "message": "Session added to agenda.",
  "agenda_item": { "...": "..." },
  "warning": "Time clash detected with: Intro to React"
}
```

**Session full `400`**
```json
{
  "error": "Session is full."
}
```

**Already booked `400`**
```json
{
  "error": "Session is already in your agenda."
}
```

---

#### GET `/api/agenda/my` — Get my agenda

Requires attendee Bearer token.

No request body needed.

**Success response `200`**
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

---

#### DELETE `/api/agenda/1` — Remove session from agenda

Requires attendee Bearer token (must own the agenda item).

No request body needed.

**Success response `200`**
```json
{
  "message": "Session removed from agenda."
}
```

**Not found `404`**
```json
{
  "error": "Agenda item not found."
}
```

---

#### GET `/api/agenda/my/download` — Download agenda as PDF

Requires attendee Bearer token.

No request body needed.

**Success response `200`**

Returns `application/pdf` file: `agenda_{attendee_id}.pdf`

---

### Attendees

#### POST `/api/attendees` — Create attendee

```json
{
  "email": "bob.attendee@example.com",
  "password": "secret12",
  "full_name": "Bob Wilson",
  "phone": "+94 71 555 1234"
}
```

**Success response `201`**
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

---

#### GET `/api/attendees/1` — Get attendee profile

Requires attendee Bearer token (must own profile).

No request body needed.

**Success response `200`**
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

---

#### PUT `/api/attendees/1` — Update attendee profile

Requires attendee Bearer token (must own profile).

```json
{
  "full_name": "Jane Doe Updated",
  "phone": "+94 77 999 8888"
}
```

**Success response `200`**
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

---

#### DELETE `/api/attendees/1` — Delete attendee

Requires attendee Bearer token (must own profile).

No request body needed.

**Success response `200`**
```json
{
  "message": "Attendee deleted."
}
```

---

### Organisers

#### POST `/api/organisers` — Create organiser

```json
{
  "email": "sara.organiser@example.com",
  "password": "secret12",
  "full_name": "Sara Perera",
  "organisation": "EventCo",
  "phone": "+94 76 444 5555"
}
```

**Success response `201`**
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

**Validation error `400`**
```json
{
  "errors": ["Organisation is required."]
}
```

---

#### GET `/api/organisers/1` — Get organiser profile

Requires organiser Bearer token (must own profile).

No request body needed.

**Success response `200`**
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

---

#### PUT `/api/organisers/1` — Update organiser profile

Requires organiser Bearer token (must own profile).

```json
{
  "full_name": "John Smith Updated",
  "organisation": "Tech Events International",
  "phone": "+94 77 111 2222"
}
```

**Success response `200`**
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

---

#### DELETE `/api/organisers/1` — Delete organiser

Requires organiser Bearer token (must own profile).

No request body needed.

**Success response `200`**
```json
{
  "message": "Organiser deleted."
}
```

---

### Admin

#### GET `/api/admin/stats` — Dashboard statistics

Requires admin Bearer token.

No request body needed.

**Success response `200`**
```json
{
  "stats": {
    "users": 10,
    "attendees": 7,
    "organisers": 2,
    "sessions": 15,
    "agenda_items": 42
  }
}
```

---

#### GET `/api/admin/users` — List all users

Requires admin Bearer token.

No request body needed.

**Success response `200`**
```json
{
  "users": [
    {
      "id": 1,
      "email": "jane.attendee@example.com",
      "role": "attendee",
      "is_active": true,
      "created_at": "2026-07-04T14:00:00"
    }
  ]
}
```

---

#### PUT `/api/admin/users/1` — Activate or deactivate a user

Requires admin Bearer token.

```json
{
  "is_active": false
}
```

**Success response `200`**
```json
{
  "message": "User updated.",
  "user": {
    "id": 1,
    "email": "jane.attendee@example.com",
    "role": "attendee",
    "is_active": false,
    "created_at": "2026-07-04T14:00:00"
  }
}
```

**Cannot deactivate self `400`**
```json
{
  "error": "You cannot deactivate your own account."
}
```

---

#### DELETE `/api/admin/users/1` — Delete a user

Requires admin Bearer token.

No request body needed.

**Success response `200`**
```json
{
  "message": "User deleted."
}
```

---

#### GET `/api/admin/sessions` — List all sessions

Requires admin Bearer token.

No request body needed.

**Success response `200`**
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

#### DELETE `/api/admin/sessions/1` — Delete any session

Requires admin Bearer token.

No request body needed.

**Success response `200`**
```json
{
  "message": "Session deleted."
}
```

---

## Project Structure

```
event-scheduler-project-api/
├── .env                        # local DB credentials (not committed)
├── .env.example                # template for .env
├── requirements.txt
├── run.py                      # entry point — starts the server
└── app/
    ├── __init__.py             # create_app() factory + JWT setup
    ├── config.py               # loads DB + JWT config from .env
    ├── extensions.py           # SQLAlchemy + JWT instances
    ├── middleware.py           # roles_required decorator
    ├── utils.py                # shared helpers (utc_now, etc.)
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
    │   ├── agenda_controller.py
    │   └── admin_controller.py
    └── routes/
        ├── auth_routes.py
        ├── attendee_routes.py
        ├── organiser_routes.py
        ├── session_routes.py
        ├── agenda_routes.py
        └── admin_routes.py
```
