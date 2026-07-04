from app.extensions import db
from app.models.agenda_item_model import AgendaItem
from app.models.attendee_model import Attendee
from app.models.organiser_model import Organiser
from app.models.session_model import Session
from app.models.user_model import User


def get_stats():
    return {
        "stats": {
            "users": User.query.count(),
            "attendees": Attendee.query.count(),
            "organisers": Organiser.query.count(),
            "sessions": Session.query.count(),
            "agenda_items": AgendaItem.query.count(),
        }
    }, 200


def get_all_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return {"users": [user.to_dict() for user in users]}, 200


def get_all_sessions():
    sessions = Session.query.order_by(Session.start_time.asc()).all()
    return {
        "sessions": [s.to_dict(include_booking_count=True) for s in sessions],
    }, 200


def delete_session(session_id):
    session = Session.query.get(session_id)
    if not session:
        return {"error": "Session not found."}, 404

    try:
        db.session.delete(session)
        db.session.commit()
        return {"message": "Session deleted."}, 200
    except Exception:
        db.session.rollback()
        return {"error": "Failed to delete session."}, 500


def set_user_active(user_id, is_active, current_user_id):
    if user_id == current_user_id:
        return {"error": "You cannot deactivate your own account."}, 400

    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found."}, 404

    try:
        user.is_active = bool(is_active)
        db.session.commit()
        return {"message": "User updated.", "user": user.to_dict()}, 200
    except Exception:
        db.session.rollback()
        return {"error": "Failed to update user."}, 500


def delete_user(user_id, current_user_id):
    if user_id == current_user_id:
        return {"error": "You cannot delete your own account."}, 400

    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found."}, 404

    try:
        if user.attendee:
            db.session.delete(user.attendee)
        if user.organiser:
            db.session.delete(user.organiser)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted."}, 200
    except Exception:
        db.session.rollback()
        return {"error": "Failed to delete user."}, 500
