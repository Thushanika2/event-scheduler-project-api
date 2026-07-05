"""Seed user accounts (admin, organisers, attendees)."""

from app.extensions import db
from app.models.user_model import User
from seeders.base import SeedResult, flush_session

# Default password for all seeded accounts (hashed via User.set_password).
DEFAULT_PASSWORD = "password123"

USERS = [
    {
        "email": "admin@agendaflow.demo",
        "role": "admin",
    },
    {
        "email": "john.smith@techevents.lk",
        "role": "organiser",
    },
    {
        "email": "sara.perera@eventco.lk",
        "role": "organiser",
    },
    {
        "email": "jane.doe@example.com",
        "role": "attendee",
    },
    {
        "email": "bob.wilson@example.com",
        "role": "attendee",
    },
    {
        "email": "priya.fernando@example.com",
        "role": "attendee",
    },
]


def seed_users() -> SeedResult:
    """Create user accounts if they do not already exist (matched by email)."""

    result = SeedResult(name="users")

    for entry in USERS:
        email = entry["email"]
        role = entry["role"]

        existing = User.query.filter_by(email=email).first()
        if existing:
            result.record_skip(f"User already exists: {email} ({role})")
            continue

        user = User(email=email, role=role, is_active=True)
        user.set_password(DEFAULT_PASSWORD)
        db.session.add(user)
        flush_session()

        result.record_insert(f"User created: {email} ({role})")

    return result
