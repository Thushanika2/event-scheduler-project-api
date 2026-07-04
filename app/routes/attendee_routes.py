from flask import Blueprint, jsonify, request

from app.controllers.attendee_controller import (
    create_attendee,
    delete_attendee,
    get_attendee,
    update_attendee,
)
from app.middleware import roles_required

attendees_bp = Blueprint("attendees", __name__, url_prefix="/api/attendees")


@attendees_bp.route("", methods=["POST"])
def create():
    data = request.get_json() or {}
    body, status = create_attendee(data)
    return jsonify(body), status


@attendees_bp.route("/<int:attendee_id>", methods=["GET"])
@roles_required("attendee")
def get_one(attendee_id, current_user=None, **kwargs):
    if not current_user.attendee or current_user.attendee.id != attendee_id:
        return jsonify({"error": "Forbidden."}), 403
    body, status = get_attendee(attendee_id)
    return jsonify(body), status


@attendees_bp.route("/<int:attendee_id>", methods=["PUT"])
@roles_required("attendee")
def update(attendee_id, current_user=None, **kwargs):
    if not current_user.attendee or current_user.attendee.id != attendee_id:
        return jsonify({"error": "Forbidden."}), 403
    data = request.get_json() or {}
    body, status = update_attendee(attendee_id, data)
    return jsonify(body), status


@attendees_bp.route("/<int:attendee_id>", methods=["DELETE"])
@roles_required("attendee")
def delete(attendee_id, current_user=None, **kwargs):
    if not current_user.attendee or current_user.attendee.id != attendee_id:
        return jsonify({"error": "Forbidden."}), 403
    body, status = delete_attendee(attendee_id)
    return jsonify(body), status
