from flask import Blueprint, jsonify, request
from services.predict_service import make_prediction

predict_bp = Blueprint('predict', __name__)

@predict_bp.route('/', methods=['POST'], strict_slashes=False)
def predict():
    data = request.json
    return jsonify(make_prediction(data))

