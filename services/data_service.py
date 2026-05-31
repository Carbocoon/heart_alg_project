# services/data_service.py
import sqlite3
import pandas as pd

DB_PATH = 'heart_disease.db'

def get_overview_stats():
    """返回数据概览的统计指标"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 总记录数
    cursor.execute("SELECT COUNT(*) FROM fact_health_record")
    total = cursor.fetchone()[0]
    
    # 患病率
    cursor.execute("SELECT AVG(target) FROM fact_health_record")
    disease_rate = cursor.fetchone()[0] or 0.0
    
    # 男性比例（假设 sex=1 为男）
    cursor.execute("SELECT SUM(sex) * 1.0 / COUNT(*) FROM fact_health_record")
    male_ratio = cursor.fetchone()[0] or 0.0
    
    # 平均年龄
    cursor.execute("SELECT AVG(age) FROM fact_health_record")
    avg_age = cursor.fetchone()[0] or 0.0
    
    # 平均血压
    cursor.execute("SELECT AVG(trestbps) FROM fact_health_record")
    avg_trestbps = cursor.fetchone()[0] or 0.0
    
    # 平均胆固醇
    cursor.execute("SELECT AVG(chol) FROM fact_health_record")
    avg_chol = cursor.fetchone()[0] or 0.0
    
    conn.close()
    
    return {
        'total': total,
        'disease_rate': round(disease_rate, 4),
        'male_ratio': round(male_ratio, 4),
        'avg_age': round(avg_age, 1),
        'avg_trestbps': round(avg_trestbps, 1),
        'avg_chol': round(avg_chol, 1)
    }

def get_data_preview(limit=10):
    conn = sqlite3.connect(DB_PATH)
    query = f"SELECT * FROM fact_health_record LIMIT {limit}"
    df = pd.read_sql_query(query, conn)
    conn.close()
    # 将 record_id 列重命名为 ID，供前端使用
    if 'record_id' in df.columns:
        df['ID'] = df['record_id']
    # 转换为字典列表
    records = df.to_dict(orient='records')
    return records