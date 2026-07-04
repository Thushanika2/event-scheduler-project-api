from datetime import datetime

from flask_jwt_extended import create_access_token

from app.extensions import db
from app.models.attendee_model import Attendee
from app.models.organiser_model import Organiser
from app.models.user_model import User


def _validate_register_payload(data):
    errors = []
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""
    role = (data.get("role") or "attendee").strip()
    full_name = (data.get("full_name") or "").strip()

    if not email:
        errors.append("Email is required.")
    if not password:
        errors.append("Password is required.")
    elif len(password) < 6:
        errors.append("Password must be at least 6 characters.")
    if role not in ("attendee", "organiser", "admin"):
        errors.append("Role must be 'attendee', 'organiser', or 'admin'.")
    if role != "admin" and not full_name:
        errors.append("Full name is required.")
    if role == "organiser" and not (data.get("organisation") or "").strip():
        errors.append("Organisation is required for organisers.")

    if email and User.query.filter_by(email=email).first():
        errors.append("Email is already registered.")
    if role == "admin" and User.query.filter_by(role="admin").count() >= 1:
        errors.append(
            "An administrator account already exists. Admin registration is disabled."
        )

    return errors


def register_user(data):
    errors = _validate_register_payload(data)
    if errors:
        return {"errors": errors}, 400

    try:
        role = data.get("role", "attendee")
        user = User(email=data["email"].strip(), role=role)
        user.set_password(data["password"])
        db.session.add(user)
        db.session.flush()

        if role == "organiser":
            organiser = Organiser(
                user_id=user.id,
                full_name=data["full_name"].strip(),
                organisation=data["organisation"].strip(),
                phone=(data.get("phone") or "").strip() or None,
            )
            db.session.add(organiser)
        elif role == "attendee":
            attendee = Attendee(
                user_id=user.id,
                full_name=data["full_name"].strip(),
                phone=(data.get("phone") or "").strip() or None,
            )
            db.session.add(attendee)

        db.session.commit()

        access_token = create_access_token(identity=str(user.id))
        return {
            "message": "Registration successful.",
            "access_token": access_token,
            "user": user.to_dict(),
        }, 201
    except Exception:
        db.session.rollback()
        return {"error": "Registration failed."}, 500


def login_user(data):
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    if not email or not password:
        return {"errors": ["Email and password are required."]}, 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return {"error": "Invalid email or password."}, 401

    if not user.is_active:
        return {"error": "Account is inactive."}, 403

    access_token = create_access_token(identity=str(user.id))
    return {
        "message": "Login successful.",
        "access_token": access_token,
        "user": user.to_dict(),
    }, 200


def admin_registration_available():
    available = User.query.filter_by(role="admin").count() == 0
    return {"available": available}, 200


def logout_user():
    return {"message": "Logout successful."}, 200


def get_profile(user):
    profile_data = user.to_dict()
    if user.role == "organiser" and user.organiser:
        profile_data["organiser"] = user.organiser.to_dict()
    elif user.role == "attendee" and user.attendee:
        profile_data["attendee"] = user.attendee.to_dict()
    return {"user": profile_data}, 200
