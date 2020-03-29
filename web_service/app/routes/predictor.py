from flask import Blueprint, jsonify

from app import Predictor

predictor_bp = Blueprint("predictor_bp", __name__)


@predictor_bp.route("/all")
def get_all_predictors():
    return jsonify({"predictors": [predictor.name for predictor in Predictor.query.all()]})
