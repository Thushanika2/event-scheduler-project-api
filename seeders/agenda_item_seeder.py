"""Seed personal agenda items linking attendees to sessions."""

from typing import Optional

from app.extensions import db
from app.models.agenda_item_model import AgendaItem
from app.models.attendee_model import Attendee
from app.models.session_model import Session
from app.models.user_model import User
from seeders.base import SeedResult, flush_session

# Each entry maps an attendee email to a session title (must match session_seeder).
AGENDA_ITEMS = [
    {
        "attendee_email": "jane.doe@example.com",
        "session_title": "Intro to React",
    },
    {
        "attendee_email": "jane.doe@example.com",
        "session_title": "Building REST APIs with Flask",
    },
    {
        "attendee_email": "jane.doe@example.com",
        "session_title": "Cloud Architecture on AWS",
    },
    {
        "attendee_email": "bob.wilson@example.com",
        "session_title": "Intro to React",
    },
    {
        "attendee_email": "bob.wilson@example.com",
        "session_title": "Kubernetes for Beginners",
    },
    {
        "attendee_email": "priya.fernando@example.com",
        "session_title": "Panel: Future of Web Development",
    },
    {
        "attendee_email": "priya.fernando@example.com",
        "session_title": "UX Design Workshop",
    },
]


def _find_attendee(email: str) -> Optional[Attendee]:
    user = User.query.filter_by(email=email, role="attendee").first()
    if not user:
        return None
    return Attendee.query.filter_by(user_id=user.id).first()


def _find_session(title: str) -> Optional[Session]:
    return Session.query.filter_by(title=title).first()


def seed_agenda_items() -> SeedResult:
    """Create agenda bookings for seeded attendees and sessions."""

    result = SeedResult(name="agenda_items")

    for entry in AGENDA_ITEMS:
        attendee = _find_attendee(entry["attendee_email"])
        if not attendee:
            result.record_skip(
                f"Attendee not found for agenda item: {entry['attendee_email']}"
            )
            continue

        session = _find_session(entry["session_title"])
        if not session:
            result.record_skip(
                f"Session not found for agenda item: {entry['session_title']}"
            )
            continue

        existing = AgendaItem.query.filter_by(
            attendee_id=attendee.id,
            session_id=session.id,
        ).first()
        if existing:
            result.record_skip(
                f"Agenda item already exists: {entry['attendee_email']} -> "
                f"{entry['session_title']}"
            )
            continue

        agenda_item = AgendaItem(
            attendee_id=attendee.id,
            session_id=session.id,
        )
        db.session.add(agenda_item)
        flush_session()

        result.record_insert(
            f"Agenda item created: {entry['attendee_email']} -> "
            f"{entry['session_title']}"
        )

    return result
