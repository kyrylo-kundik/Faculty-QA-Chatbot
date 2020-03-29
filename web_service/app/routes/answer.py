from flask import Blueprint, jsonify, abort, request

from app import Answer, db

answer_bp = Blueprint("answer_bp", __name__)


@answer_bp.route("/<answer_id>", methods=["PUT"])
def update_answer(answer_id):
    answer: Answer = Answer.query.filter_by(id=answer_id).first()

    if not answer:
        abort(404)
    else:
        content = request.json
        answer.rating = content["rating"]
        answer.msg_id = content["msg_id"]

        db.session.add(answer)
        db.session.commit()

        return jsonify({"success": True})
