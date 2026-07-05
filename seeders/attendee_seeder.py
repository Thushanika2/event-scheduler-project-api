"""Seed attendee profiles linked to attendee user accounts."""

from app.extensions import db
from app.models.attendee_model import Attendee
from app.models.user_model import User
from seeders.base import SeedResult, flush_session

ATTENDEES = [
    {
        "email": "jane.doe@example.com",
        "full_name": "Jane Doe",
        "phone": "+94 77 123 4567",
    },
    {
        "email": "bob.wilson@example.com",
        "full_name": "Bob Wilson",
        "phone": "+94 71 555 1234",
    },
    {
        "email": "priya.fernando@example.com",
        "full_name": "Priya Fernando",
        "phone": "+94 75 321 9876",
    },
]


def seed_attendees() -> SeedResult:
    """Create attendee profiles for seeded attendee users."""

    result = SeedResult(name="attendees")

    for entry in ATTENDEES:
        email = entry["email"]

        user = User.query.filter_by(email=email, role="attendee").first()
        if not user:
            result.record_skip(
                f"Attendee user not found, skipping profile: {email}"
            )
            continue

        existing = Attendee.query.filter_by(user_id=user.id).first()
        if existing:
            result.record_skip(
                f"Attendee profile already exists: {entry['full_name']} ({email})"
            )
            continue

        attendee = Attendee(
            user_id=user.id,
            full_name=entry["full_name"],
            phone=entry["phone"],
        )
        db.session.add(attendee)
        flush_session()

        result.record_insert(f"Attendee created: {entry['full_name']} ({email})")

    return result
