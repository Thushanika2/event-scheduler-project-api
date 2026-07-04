from flask import Blueprint, jsonify, request

from app.controllers.auth_controller import (
    admin_registration_available,
    get_profile,
    login_user,
    logout_user,
    register_user,
)
from app.middleware import roles_required

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/admin-registration-status", methods=["GET"])
def admin_registration_status():
    body, status = admin_registration_available()
    return jsonify(body), status


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    body, status = register_user(data)
    return jsonify(body), status


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    body, status = login_user(data)
    return jsonify(body), status


@auth_bp.route("/logout", methods=["POST"])
@roles_required("organiser", "attendee", "admin")
def logout(**kwargs):
    body, status = logout_user()
    return jsonify(body), status


@auth_bp.route("/profile", methods=["GET"])
@roles_required("organiser", "attendee", "admin")
def profile(current_user=None, **kwargs):
    body, status = get_profile(current_user)
    return jsonify(body), status
