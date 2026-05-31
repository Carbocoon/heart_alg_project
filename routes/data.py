# routes/data.py
from flask import Blueprint, jsonify, request   # 必须导入 request
from services.data_service import get_overview_stats, get_data_preview

data_bp = Blueprint('data', __name__)

@data_bp.route('/overview', methods=['GET'], strict_slashes=False)
def overview():
    stats = get_overview_stats()
    return jsonify(stats)

# 匹配前端请求 /api/data
@data_bp.route('/', methods=['GET'], strict_slashes=False)
def data_list():
    limit = request.args.get('limit', 10, type=int)
    rows = get_data_preview(limit)
    # 包装成前端期望的格式
    return jsonify({'success': True, 'data': rows})