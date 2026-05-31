from flask import Blueprint, jsonify
from services.dashboard_service import get_dashboard_metrics

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/', methods=['GET'], strict_slashes=False)
def dashboard():
    return jsonify(get_dashboard_metrics())