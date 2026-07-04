from flask import Blueprint, jsonify, request, send_file

from app.controllers.agenda_controller import (
    add_to_agenda,
    delete_agenda_item,
    download_my_agenda,
    get_my_agenda,
)
from app.middleware import roles_required

agenda_bp = Blueprint("agenda", __name__, url_prefix="/api/agenda")


@agenda_bp.route("", methods=["POST"])
@roles_required("attendee")
def add(current_user=None, **kwargs):
    if not current_user.attendee:
        return jsonify({"error": "Attendee profile not found."}), 403
    data = request.get_json() or {}
    body, status = add_to_agenda(current_user.attendee.id, data)
    return jsonify(body), status


@agenda_bp.route("/my", methods=["GET"])
@roles_required("attendee")
def my_agenda(current_user=None, **kwargs):
    if not current_user.attendee:
        return jsonify({"error": "Attendee profile not found."}), 403
    body, status = get_my_agenda(current_user.attendee.id)
    return jsonify(body), status


@agenda_bp.route("/<int:agenda_item_id>", methods=["DELETE"])
@roles_required("attendee")
def delete(agenda_item_id, current_user=None, **kwargs):
    if not current_user.attendee:
        return jsonify({"error": "Attendee profile not found."}), 403
    body, status = delete_agenda_item(agenda_item_id, current_user.attendee.id)
    return jsonify(body), status


@agenda_bp.route("/my/download", methods=["GET"])
@roles_required("attendee")
def download(current_user=None, **kwargs):
    if not current_user.attendee:
        return jsonify({"error": "Attendee profile not found."}), 403
    buffer, filename = download_my_agenda(current_user.attendee.id)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype="application/pdf",
    )
