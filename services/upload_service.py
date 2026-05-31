import os
import shutil
import pandas as pd
from werkzeug.utils import secure_filename
from utils import db_utils
from utils.preprocessing import clean_heart_data
from utils.classification import retrain_model   # 新增导入

# ========== 路径配置 ==========
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
TEMP_DATA_PATH = os.path.join(BASE_DIR, 'data', 'temp_cleaned.csv')
MAIN_DATA_PATH = os.path.join(BASE_DIR, 'data', 'cleaned_heart.csv')
DB_PATH = os.path.join(BASE_DIR, 'heart_disease.db')
BACKUP_DATA_PATH = os.path.join(BASE_DIR, 'data', 'backup_cleaned.csv')
BACKUP_DB_PATH = os.path.join(BASE_DIR, 'backup_heart_disease.db')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(TEMP_DATA_PATH), exist_ok=True)

def process_upload_preview(file):
    """预览阶段：保存上传文件 -> 调用清洗函数生成临时清洗文件 -> 返回统计预览"""
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        clean_heart_data(filepath, TEMP_DATA_PATH)

        df_clean = pd.read_csv(TEMP_DATA_PATH)

        total = len(df_clean)
        disease_rate = float(df_clean['target'].mean()) if 'target' in df_clean.columns else 0.0
        male_ratio = float((df_clean['sex'] == 1).mean()) if 'sex' in df_clean.columns else 0.0
        avg_age = float(df_clean['age'].mean()) if 'age' in df_clean.columns else 0.0
        avg_trestbps = float(df_clean['trestbps'].mean()) if 'trestbps' in df_clean.columns else 0.0
        avg_chol = float(df_clean['chol'].mean()) if 'chol' in df_clean.columns else 0.0

        preview_rows = df_clean.head(10).to_dict(orient='records')

        return {
            'success': True,
            'preview': {
                'total': total,
                'disease_rate': round(disease_rate, 4),
                'male_ratio': round(male_ratio, 4),
                'avg_age': round(avg_age, 1),
                'avg_trestbps': round(avg_trestbps, 1),
                'avg_chol': round(avg_chol, 1),
                'data_preview': preview_rows
            }
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def confirm_import():
    try:
        if not os.path.exists(TEMP_DATA_PATH):
            return {'success': False, 'error': '没有待确认的临时数据，请先上传文件'}

        # 备份当前累积数据（如果存在）
        if os.path.exists(MAIN_DATA_PATH):
            shutil.copy2(MAIN_DATA_PATH, BACKUP_DATA_PATH)
        if os.path.exists(DB_PATH):
            shutil.copy2(DB_PATH, BACKUP_DB_PATH)

        # 读取本次新清洗的数据
        new_df = pd.read_csv(TEMP_DATA_PATH)

        # 追加到累积文件
        if os.path.exists(MAIN_DATA_PATH):
            existing_df = pd.read_csv(MAIN_DATA_PATH)
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            # 可选：去重（根据某列，例如根据患者ID，但这里简化，不去重）
            combined_df.to_csv(MAIN_DATA_PATH, index=False)
        else:
            new_df.to_csv(MAIN_DATA_PATH, index=False)

        # 重新执行 ETL（追加模式）
        # 需要读取合并后的完整数据，然后调用 etl_to_sqlite(append=True)
        full_df = pd.read_csv(MAIN_DATA_PATH)
        db_utils.etl_to_sqlite(full_df, append=False)  # 注意：这里应该增量追加
        # 实际上我们应该只插入新数据，而不是全量重建。但为了简化，可以采用全量重建方式（效率低但数据量不大）
        # 更优方案：只插入 new_df 到数据库，但需要处理 patient_key 自增。
        # 为简单，我们采用全量重建：用完整数据清空表后重新插入。
        db_utils.etl_to_sqlite(full_df, append=False)  # append=False 表示先清空再全量插入

        # 重新训练模型（基于完整数据）
        retrain_model(MAIN_DATA_PATH)

        # 删除临时文件
        os.remove(TEMP_DATA_PATH)

        return {'success': True, 'message': '数据追加成功，已更新数据仓库并重新训练模型。'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def cancel_import():
    """取消导入：仅删除临时文件，不影响正式数据"""
    try:
        if os.path.exists(TEMP_DATA_PATH):
            os.remove(TEMP_DATA_PATH)
        return {'success': True, 'message': '已取消导入'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def rollback_import():
    """撤销上次导入：从备份恢复正式数据和数据库"""
    try:
        if not os.path.exists(BACKUP_DATA_PATH) or not os.path.exists(BACKUP_DB_PATH):
            return {'success': False, 'error': '没有可用的备份，无法撤销'}

        shutil.copy2(BACKUP_DATA_PATH, MAIN_DATA_PATH)
        shutil.copy2(BACKUP_DB_PATH, DB_PATH)

        # 删除备份文件
        os.remove(BACKUP_DATA_PATH)
        os.remove(BACKUP_DB_PATH)

        # 注意：撤销后也应该重新训练模型，使用恢复后的数据
        retrain_model(MAIN_DATA_PATH)

        return {'success': True, 'message': '已撤销上一次导入，数据已回滚，模型已重训练。'}
    except Exception as e:
        return {'success': False, 'error': str(e)}