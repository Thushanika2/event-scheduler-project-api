from flask import Blueprint, jsonify, request

from app.controllers.admin_controller import (
    delete_session,
    delete_user,
    get_all_sessions,
    get_all_users,
    get_stats,
    set_user_active,
)
from app.middleware import roles_required

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.route("/stats", methods=["GET"])
@roles_required("admin")
def stats(current_user=None, **kwargs):
    body, status = get_stats()
    return jsonify(body), status


@admin_bp.route("/users", methods=["GET"])
@roles_required("admin")
def users(current_user=None, **kwargs):
    body, status = get_all_users()
    return jsonify(body), status


@admin_bp.route("/users/<int:user_id>", methods=["PUT"])
@roles_required("admin")
def update_user(user_id, current_user=None, **kwargs):
    data = request.get_json() or {}
    if "is_active" not in data:
        return jsonify({"errors": ["is_active is required."]}), 400
    body, status = set_user_active(user_id, data["is_active"], current_user.id)
    return jsonify(body), status


@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
@roles_required("admin")
def remove_user(user_id, current_user=None, **kwargs):
    body, status = delete_user(user_id, current_user.id)
    return jsonify(body), status


@admin_bp.route("/sessions", methods=["GET"])
@roles_required("admin")
def sessions(current_user=None, **kwargs):
    body, status = get_all_sessions()
    return jsonify(body), status


@admin_bp.route("/sessions/<int:session_id>", methods=["DELETE"])
@roles_required("admin")
def remove_session(session_id, current_user=None, **kwargs):
    body, status = delete_session(session_id)
    return jsonify(body), status
