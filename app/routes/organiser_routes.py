from flask import Blueprint, jsonify, request

from app.controllers.organiser_controller import (
    create_organiser,
    delete_organiser,
    get_organiser,
    update_organiser,
)
from app.middleware import roles_required

organisers_bp = Blueprint("organisers", __name__, url_prefix="/api/organisers")


@organisers_bp.route("", methods=["POST"])
def create():
    data = request.get_json() or {}
    body, status = create_organiser(data)
    return jsonify(body), status


@organisers_bp.route("/<int:organiser_id>", methods=["GET"])
@roles_required("organiser")
def get_one(organiser_id, current_user=None, **kwargs):
    if not current_user.organiser or current_user.organiser.id != organiser_id:
        return jsonify({"error": "Forbidden."}), 403
    body, status = get_organiser(organiser_id)
    return jsonify(body), status


@organisers_bp.route("/<int:organiser_id>", methods=["PUT"])
@roles_required("organiser")
def update(organiser_id, current_user=None, **kwargs):
    if not current_user.organiser or current_user.organiser.id != organiser_id:
        return jsonify({"error": "Forbidden."}), 403
    data = request.get_json() or {}
    body, status = update_organiser(organiser_id, data)
    return jsonify(body), status


@organisers_bp.route("/<int:organiser_id>", methods=["DELETE"])
@roles_required("organiser")
def delete(organiser_id, current_user=None, **kwargs):
    if not current_user.organiser or current_user.organiser.id != organiser_id:
        return jsonify({"error": "Forbidden."}), 403
    body, status = delete_organiser(organiser_id)
    return jsonify(body), status
