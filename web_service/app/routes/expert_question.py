from flask import Blueprint, request, abort, jsonify

from app import ExpertQuestion, db

expert_question_bp = Blueprint("expert_question_bp", __name__)


@expert_question_bp.route("/add", methods=["POST"])
def add_expert_question():
    content = request.json

    try:
        exp_q = ExpertQuestion(
            question_text=content["text"],
            question_msg_id=int(content["msg_id"]),
            expert_question_chat_id=int(content["expert_chat_id"]),
            expert_question_msg_id=int(content["expert_msg_id"])
        )
    except (KeyError, ValueError):
        abort(400)
        return

    db.session.add(exp_q)
    db.session.commit()

    return jsonify({"success": True}), 200


@expert_question_bp.route("/update", methods=["PUT"])
def update_expert_question():
    msg_id = request.args.get("msg_id")
    chat_id = request.args.get("chat_id")

    exp_q: ExpertQuestion = ExpertQuestion.query.filter_by(
        expert_question_chat_id=chat_id,
        expert_question_msg_id=msg_id,
    ).first()

    if not exp_q:
        abort(404)
        return

    content = request.json
    try:
        exp_q.expert_answer_msg_id = int(content["msg_id"])
        exp_q.expert_answer_text = content["text"]
        exp_q.expert_user_fk = int(content["tg_id"])
    except (KeyError, ValueError):
        abort(400)
        return

    db.session.add(exp_q)
    db.session.commit()

    return jsonify({"success": True, "expert_question": exp_q.serialize}), 200
