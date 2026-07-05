"""Seed conference sessions linked to organiser profiles."""

from datetime import datetime
from typing import Optional

from app.extensions import db
from app.models.organiser_model import Organiser
from app.models.session_model import Session
from app.models.user_model import User
from seeders.base import SeedResult, flush_session

SESSIONS = [
    {
        "organiser_email": "john.smith@techevents.lk",
        "title": "Intro to React",
        "speaker": "Alice Chen",
        "track": "Web Development",
        "room": "Hall A",
        "start_time": datetime(2026, 7, 10, 9, 0, 0),
        "end_time": datetime(2026, 7, 10, 10, 30, 0),
        "capacity": 50,
    },
    {
        "organiser_email": "john.smith@techevents.lk",
        "title": "Building REST APIs with Flask",
        "speaker": "Mohamed Hassan",
        "track": "Backend",
        "room": "Hall B",
        "start_time": datetime(2026, 7, 10, 11, 0, 0),
        "end_time": datetime(2026, 7, 10, 12, 30, 0),
        "capacity": 40,
    },
    {
        "organiser_email": "john.smith@techevents.lk",
        "title": "Panel: Future of Web Development",
        "speaker": "Various Speakers",
        "track": "Web Development",
        "room": "Main Hall",
        "start_time": datetime(2026, 7, 10, 14, 0, 0),
        "end_time": datetime(2026, 7, 10, 15, 30, 0),
        "capacity": 100,
    },
    {
        "organiser_email": "sara.perera@eventco.lk",
        "title": "Cloud Architecture on AWS",
        "speaker": "Nimal Jayawardena",
        "track": "DevOps",
        "room": "Room 201",
        "start_time": datetime(2026, 7, 10, 9, 0, 0),
        "end_time": datetime(2026, 7, 10, 10, 30, 0),
        "capacity": 35,
    },
    {
        "organiser_email": "sara.perera@eventco.lk",
        "title": "Kubernetes for Beginners",
        "speaker": "Lisa Wong",
        "track": "DevOps",
        "room": "Room 201",
        "start_time": datetime(2026, 7, 10, 11, 0, 0),
        "end_time": datetime(2026, 7, 10, 12, 30, 0),
        "capacity": 30,
    },
    {
        "organiser_email": "sara.perera@eventco.lk",
        "title": "UX Design Workshop",
        "speaker": "Emma Clarke",
        "track": "Design",
        "room": "Studio 1",
        "start_time": datetime(2026, 7, 10, 14, 0, 0),
        "end_time": datetime(2026, 7, 10, 16, 0, 0),
        "capacity": 25,
    },
]


def _find_organiser(email: str) -> Optional[Organiser]:
    user = User.query.filter_by(email=email, role="organiser").first()
    if not user:
        return None
    return Organiser.query.filter_by(user_id=user.id).first()


def _session_exists(organiser_id: int, title: str, start_time: datetime) -> bool:
    return (
        Session.query.filter_by(
            organiser_id=organiser_id,
            title=title,
            start_time=start_time,
        ).first()
        is not None
    )


def seed_sessions() -> SeedResult:
    """Create conference sessions for seeded organisers."""

    result = SeedResult(name="sessions")

    for entry in SESSIONS:
        organiser = _find_organiser(entry["organiser_email"])
        if not organiser:
            result.record_skip(
                f"Organiser not found for session '{entry['title']}' "
                f"({entry['organiser_email']})"
            )
            continue

        if _session_exists(organiser.id, entry["title"], entry["start_time"]):
            result.record_skip(
                f"Session already exists: {entry['title']} "
                f"({entry['start_time'].strftime('%Y-%m-%d %H:%M')})"
            )
            continue

        session = Session(
            organiser_id=organiser.id,
            title=entry["title"],
            speaker=entry["speaker"],
            track=entry["track"],
            room=entry["room"],
            start_time=entry["start_time"],
            end_time=entry["end_time"],
            capacity=entry["capacity"],
        )
        db.session.add(session)
        flush_session()

        result.record_insert(
            f"Session created: {entry['title']} - {entry['track']} / {entry['room']}"
        )

    return result
