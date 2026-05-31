import os
import json
from flask import Blueprint, jsonify
from utils.classification import retrain_model

performance_bp = Blueprint('performance', __name__)

@performance_bp.route('/model_performance', methods=['GET'])
def get_model_performance():
    perf_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'model_performance.json')
    if not os.path.exists(perf_path):
        try:
            # 如果没有性能文件，尝试重新训练并生成性能文件
            retrain_model()
        except Exception as e:
            return jsonify({'success': False, 'error': f'模型尚未训练且评估失败: {str(e)}'})
            
    with open(perf_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify({'success': True, 'performance': data})
