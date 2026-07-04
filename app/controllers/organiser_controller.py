from app.extensions import db
from app.models.organiser_model import Organiser
from app.models.user_model import User


def _validate_organiser_payload(data, organiser_id=None):
    errors = []
    full_name = (data.get("full_name") or "").strip()
    organisation = (data.get("organisation") or "").strip()

    if not full_name:
        errors.append("Full name is required.")
    if not organisation:
        errors.append("Organisation is required.")

    if organiser_id is None:
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


def create_organiser(data):
    errors = _validate_organiser_payload(data)
    if errors:
        return {"errors": errors}, 400

    try:
        user = User(email=data["email"].strip(), role="organiser")
        user.set_password(data["password"])
        db.session.add(user)
        db.session.flush()

        organiser = Organiser(
            user_id=user.id,
            full_name=data["full_name"].strip(),
            organisation=data["organisation"].strip(),
            phone=(data.get("phone") or "").strip() or None,
        )
        db.session.add(organiser)
        db.session.commit()

        return {"message": "Organiser created.", "organiser": organiser.to_dict()}, 201
    except Exception:
        db.session.rollback()
        return {"error": "Failed to create organiser."}, 500


def get_organiser(organiser_id):
    organiser = Organiser.query.get(organiser_id)
    if not organiser:
        return {"error": "Organiser not found."}, 404
    return {"organiser": organiser.to_dict()}, 200


def update_organiser(organiser_id, data):
    organiser = Organiser.query.get(organiser_id)
    if not organiser:
        return {"error": "Organiser not found."}, 404

    errors = _validate_organiser_payload(data, organiser_id=organiser_id)
    if errors:
        return {"errors": errors}, 400

    try:
        organiser.full_name = data["full_name"].strip()
        organiser.organisation = data["organisation"].strip()
        organiser.phone = (data.get("phone") or "").strip() or None
        db.session.commit()
        return {"message": "Organiser updated.", "organiser": organiser.to_dict()}, 200
    except Exception:
        db.session.rollback()
        return {"error": "Failed to update organiser."}, 500


def delete_organiser(organiser_id):
    organiser = Organiser.query.get(organiser_id)
    if not organiser:
        return {"error": "Organiser not found."}, 404

    try:
        user = organiser.user
        db.session.delete(organiser)
        if user:
            db.session.delete(user)
        db.session.commit()
        return {"message": "Organiser deleted."}, 200
    except Exception:
        db.session.rollback()
        return {"error": "Failed to delete organiser."}, 500
