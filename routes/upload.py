from flask import Blueprint, jsonify, request
from services.upload_service import process_upload_preview, confirm_import, cancel_import, rollback_import

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/preview', methods=['POST'], strict_slashes=False)
def preview():
    """预览：上传 -> 清洗 -> 返回预览数据（不写入正式库）"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': '未找到文件'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': '未选择文件'})
    return jsonify(process_upload_preview(file))

@upload_bp.route('/confirm', methods=['POST'], strict_slashes=False)
def confirm():
    """确认导入：将临时数据写入正式库"""
    return jsonify(confirm_import())

@upload_bp.route('/cancel', methods=['POST'], strict_slashes=False)
def cancel():
    """取消导入：删除临时文件"""
    return jsonify(cancel_import())

@upload_bp.route('/rollback', methods=['POST'], strict_slashes=False)
def rollback():
    """撤销上次导入：从备份恢复"""
    return jsonify(rollback_import())