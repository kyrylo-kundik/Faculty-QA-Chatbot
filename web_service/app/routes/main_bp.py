from flask import Blueprint, current_app, jsonify, request, abort

main_bp = Blueprint("main_bp", __name__)


@main_bp.route("/")
def hello_world():
    return "hello world"


@main_bp.route("/healthCheck")
def health_check():
    return jsonify({"success": True})


@main_bp.route("/search")
def perform_search():
    predictor = request.args.get("predictor")
    query = request.args.get("query")

    try:
        return jsonify(current_app.predictors_table[predictor](query))
    except KeyError:
        abort(404)
