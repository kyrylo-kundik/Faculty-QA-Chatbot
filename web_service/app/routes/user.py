from datetime import datetime

from flask import Blueprint, request, jsonify

from app import User, db

user_bp = Blueprint("user_bp", __name__)


@user_bp.route("/add", methods=["POST"])
def add_user():
    content = request.json
    print(content)
    tg_id = content["tg_id"]

    user: User = User.query.filter_by(tg_id=tg_id).first()
    if user is not None:
        user.last_active_at = datetime.utcnow()
    else:
        user = User(tg_id=tg_id, first_name=content["first_name"], username=content["username"])

    db.session.add(user)
    db.session.commit()

    return jsonify({"success": True}), 200
