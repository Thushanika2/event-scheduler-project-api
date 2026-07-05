"""Seed organiser profiles linked to organiser user accounts."""

from app.extensions import db
from app.models.organiser_model import Organiser
from app.models.user_model import User
from seeders.base import SeedResult, flush_session

ORGANISERS = [
    {
        "email": "john.smith@techevents.lk",
        "full_name": "John Smith",
        "organisation": "Tech Events Ltd",
        "phone": "+94 77 987 6543",
    },
    {
        "email": "sara.perera@eventco.lk",
        "full_name": "Sara Perera",
        "organisation": "EventCo Lanka",
        "phone": "+94 76 444 5555",
    },
]


def seed_organisers() -> SeedResult:
    """Create organiser profiles for seeded organiser users."""

    result = SeedResult(name="organisers")

    for entry in ORGANISERS:
        email = entry["email"]

        user = User.query.filter_by(email=email, role="organiser").first()
        if not user:
            result.record_skip(
                f"Organiser user not found, skipping profile: {email}"
            )
            continue

        existing = Organiser.query.filter_by(user_id=user.id).first()
        if existing:
            result.record_skip(
                f"Organiser profile already exists: {entry['full_name']} ({email})"
            )
            continue

        organiser = Organiser(
            user_id=user.id,
            full_name=entry["full_name"],
            organisation=entry["organisation"],
            phone=entry["phone"],
        )
        db.session.add(organiser)
        flush_session()

        result.record_insert(
            f"Organiser created: {entry['full_name']} - {entry['organisation']}"
        )

    return result
