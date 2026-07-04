from datetime import datetime

from app.extensions import db
from app.models.session_model import Session


def _parse_datetime(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except (ValueError, AttributeError):
        return None


def _validate_session_payload(data, session_id=None):
    errors = []
    title = (data.get("title") or "").strip()
    speaker = (data.get("speaker") or "").strip()
    track = (data.get("track") or "").strip()
    room = (data.get("room") or "").strip()
    start_time = _parse_datetime(data.get("start_time"))
    end_time = _parse_datetime(data.get("end_time"))
    capacity = data.get("capacity")

    if not title:
        errors.append("Title is required.")
    if not speaker:
        errors.append("Speaker is required.")
    if not track:
        errors.append("Track is required.")
    if not room:
        errors.append("Room is required.")
    if not start_time:
        errors.append("Valid start time is required.")
    if not end_time:
        errors.append("Valid end time is required.")
    if start_time and end_time and start_time >= end_time:
        errors.append("End time must be after start time.")
    if capacity is None:
        errors.append("Capacity is required.")
    else:
        try:
            capacity = int(capacity)
            if capacity < 1:
                errors.append("Capacity must be at least 1.")
        except (TypeError, ValueError):
            errors.append("Capacity must be a valid integer.")

    return errors


def create_session(data, organiser_id):
    errors = _validate_session_payload(data)
    if errors:
        return {"errors": errors}, 400

    try:
        session = Session(
            organiser_id=organiser_id,
            title=data["title"].strip(),
            speaker=data["speaker"].strip(),
            track=data["track"].strip(),
            room=data["room"].strip(),
            start_time=_parse_datetime(data["start_time"]),
            end_time=_parse_datetime(data["end_time"]),
            capacity=int(data["capacity"]),
        )
        db.session.add(session)
        db.session.commit()
        return {"message": "Session created.", "session": session.to_dict(include_booking_count=True)}, 201
    except Exception:
        db.session.rollback()
        return {"error": "Failed to create session."}, 500


def get_sessions(track=None, start_time=None, end_time=None):
    query = Session.query

    if track:
        query = query.filter(Session.track == track.strip())

    parsed_start = _parse_datetime(start_time) if start_time else None
    parsed_end = _parse_datetime(end_time) if end_time else None

    if parsed_start:
        query = query.filter(Session.start_time >= parsed_start)
    if parsed_end:
        query = query.filter(Session.end_time <= parsed_end)

    sessions = query.order_by(Session.start_time.asc()).all()
    return {
        "sessions": [s.to_dict(include_booking_count=True) for s in sessions],
    }, 200


def get_session(session_id):
    session = Session.query.get(session_id)
    if not session:
        return {"error": "Session not found."}, 404
    return {"session": session.to_dict(include_booking_count=True)}, 200


def get_organiser_sessions(organiser_id):
    sessions = (
        Session.query.filter_by(organiser_id=organiser_id)
        .order_by(Session.start_time.asc())
        .all()
    )
    return {
        "sessions": [s.to_dict(include_booking_count=True) for s in sessions],
    }, 200


def get_session_popularity(session_id):
    session = Session.query.get(session_id)
    if not session:
        return {"error": "Session not found."}, 404

    booking_count = len(session.agenda_items)
    return {
        "session_id": session.id,
        "title": session.title,
        "capacity": session.capacity,
        "booking_count": booking_count,
        "is_full": booking_count >= session.capacity,
        "spots_remaining": max(0, session.capacity - booking_count),
    }, 200


def update_session(session_id, data, organiser_id):
    session = Session.query.get(session_id)
    if not session:
        return {"error": "Session not found."}, 404
    if session.organiser_id != organiser_id:
        return {"error": "Forbidden."}, 403

    errors = _validate_session_payload(data, session_id=session_id)
    if errors:
        return {"errors": errors}, 400

    try:
        session.title = data["title"].strip()
        session.speaker = data["speaker"].strip()
        session.track = data["track"].strip()
        session.room = data["room"].strip()
        session.start_time = _parse_datetime(data["start_time"])
        session.end_time = _parse_datetime(data["end_time"])
        session.capacity = int(data["capacity"])
        db.session.commit()
        return {"message": "Session updated.", "session": session.to_dict(include_booking_count=True)}, 200
    except Exception:
        db.session.rollback()
        return {"error": "Failed to update session."}, 500


def delete_session(session_id, organiser_id):
    session = Session.query.get(session_id)
    if not session:
        return {"error": "Session not found."}, 404
    if session.organiser_id != organiser_id:
        return {"error": "Forbidden."}, 403

    try:
        db.session.delete(session)
        db.session.commit()
        return {"message": "Session deleted."}, 200
    except Exception:
        db.session.rollback()
        return {"error": "Failed to delete session."}, 500
