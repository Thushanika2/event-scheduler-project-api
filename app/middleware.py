from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from app.models.user_model import User


def roles_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user or not user.is_active:
                return jsonify({"error": "Unauthorized."}), 401
            if user.role not in roles:
                return jsonify({"error": "Forbidden."}), 403
            return fn(current_user=user, *args, **kwargs)

        return wrapper

    return decorator
