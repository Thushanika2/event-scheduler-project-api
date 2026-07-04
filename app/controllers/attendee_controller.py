from app.extensions import db
from app.models.attendee_model import Attendee
from app.models.user_model import User


def _validate_attendee_payload(data, attendee_id=None):
    errors = []
    full_name = (data.get("full_name") or "").strip()

    if not full_name:
        errors.append("Full name is required.")

    if attendee_id is None:
        email = (data.get("email") or "").strip()
        password = data.get("password") or ""
        if not email:
            errors.append("Email is required.")
        if not password:
            errors.append("Password is required.")
        elif len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if email and User.query.filter_by(email=email).first():
            errors.append("Email is already registered.")

    return errors


def create_attendee(data):
    errors = _validate_attendee_payload(data)
    if errors:
        return {"errors": errors}, 400

    try:
        user = User(email=data["email"].strip(), role="attendee")
        user.set_password(data["password"])
        db.session.add(user)
        db.session.flush()

        attendee = Attendee(
            user_id=user.id,
            full_name=data["full_name"].strip(),
            phone=(data.get("phone") or "").strip() or None,
        )
        db.session.add(attendee)
        db.session.commit()

        return {"message": "Attendee created.", "attendee": attendee.to_dict()}, 201
    except Exception:
        db.session.rollback()
        return {"error": "Failed to create attendee."}, 500


def get_attendee(attendee_id):
    attendee = Attendee.query.get(attendee_id)
    if not attendee:
        return {"error": "Attendee not found."}, 404
    return {"attendee": attendee.to_dict()}, 200


def update_attendee(attendee_id, data):
    attendee = Attendee.query.get(attendee_id)
    if not attendee:
        return {"error": "Attendee not found."}, 404

    errors = _validate_attendee_payload(data, attendee_id=attendee_id)
    if errors:
        return {"errors": errors}, 400

    try:
        attendee.full_name = data["full_name"].strip()
        attendee.phone = (data.get("phone") or "").strip() or None
        db.session.commit()
        return {"message": "Attendee updated.", "attendee": attendee.to_dict()}, 200
    except Exception:
        db.session.rollback()
        return {"error": "Failed to update attendee."}, 500


def delete_attendee(attendee_id):
    attendee = Attendee.query.get(attendee_id)
    if not attendee:
        return {"error": "Attendee not found."}, 404

    try:
        user = attendee.user
        db.session.delete(attendee)
        if user:
            db.session.delete(user)
        db.session.commit()
        return {"message": "Attendee deleted."}, 200
    except Exception:
        db.session.rollback()
        return {"error": "Failed to delete attendee."}, 500
