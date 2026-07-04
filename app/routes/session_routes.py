from flask import Blueprint, jsonify, request

from app.controllers.session_controller import (
    create_session,
    delete_session,
    get_organiser_sessions,
    get_session,
    get_session_popularity,
    get_sessions,
    update_session,
)
from app.middleware import roles_required

sessions_bp = Blueprint("sessions", __name__, url_prefix="/api/sessions")


@sessions_bp.route("", methods=["GET"])
def list_sessions():
    track = request.args.get("track")
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")
    body, status = get_sessions(track=track, start_time=start_time, end_time=end_time)
    return jsonify(body), status


@sessions_bp.route("/<int:session_id>", methods=["GET"])
def get_one(session_id):
    body, status = get_session(session_id)
    return jsonify(body), status


@sessions_bp.route("", methods=["POST"])
@roles_required("organiser")
def create(current_user=None, **kwargs):
    if not current_user.organiser:
        return jsonify({"error": "Organiser profile not found."}), 403
    data = request.get_json() or {}
    body, status = create_session(data, current_user.organiser.id)
    return jsonify(body), status


@sessions_bp.route("/<int:session_id>", methods=["PUT"])
@roles_required("organiser")
def update(session_id, current_user=None, **kwargs):
    if not current_user.organiser:
        return jsonify({"error": "Organiser profile not found."}), 403
    data = request.get_json() or {}
    body, status = update_session(session_id, data, current_user.organiser.id)
    return jsonify(body), status


@sessions_bp.route("/<int:session_id>", methods=["DELETE"])
@roles_required("organiser")
def delete(session_id, current_user=None, **kwargs):
    if not current_user.organiser:
        return jsonify({"error": "Organiser profile not found."}), 403
    body, status = delete_session(session_id, current_user.organiser.id)
    return jsonify(body), status


@sessions_bp.route("/<int:session_id>/popularity", methods=["GET"])
def popularity(session_id):
    body, status = get_session_popularity(session_id)
    return jsonify(body), status


organiser_sessions_bp = Blueprint(
    "organiser_sessions", __name__, url_prefix="/api/organiser"
)


@organiser_sessions_bp.route("/sessions", methods=["GET"])
@roles_required("organiser")
def organiser_sessions(current_user=None, **kwargs):
    if not current_user.organiser:
        return jsonify({"error": "Organiser profile not found."}), 403
    body, status = get_organiser_sessions(current_user.organiser.id)
    return jsonify(body), status
