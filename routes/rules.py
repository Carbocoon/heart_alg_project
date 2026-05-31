import os
import pandas as pd
import sqlite3
from flask import Blueprint, request, jsonify
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules

rules_bp = Blueprint('rules', __name__)

def load_and_discretize(db_path='heart_disease.db'):
    """从 SQLite 加载数据，并对连续特征离散化"""
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM fact_health_record", conn)
    conn.close()
    
    # 离散化连续特征
    df['age_group'] = pd.cut(df['age'], bins=[0, 40, 60, 100], labels=['young', 'middle', 'old'])
    df['bp_group'] = pd.cut(df['trestbps'], bins=[0, 120, 140, 300], labels=['normal', 'high', 'very_high'])
    df['chol_group'] = pd.cut(df['chol'], bins=[0, 200, 240, 600], labels=['low', 'border', 'high'])
    df['thalach_group'] = pd.cut(df['thalach'], bins=[0, 100, 150, 250], labels=['low', 'medium', 'high'])
    df['oldpeak_group'] = pd.cut(df['oldpeak'], bins=[-0.1, 1, 2, 10], labels=['none', 'mild', 'severe'])
    
    # 选择用于挖掘的列（可自定义）
    feature_cols = ['age_group', 'sex', 'cp', 'fbs', 'restecg', 'exang', 'slope', 'ca', 'thal', 'target']
    # 将 target 转换为字符串表示
    df['target'] = df['target'].map({0: 'no_disease', 1: 'disease'})
    return df[feature_cols].astype(str)

def generate_rules(df, min_support=0.1, min_confidence=0.6):
    """生成关联规则"""
    # 将每行转换为事务列表
    transactions = df.values.tolist()
    te = TransactionEncoder()
    te_array = te.fit(transactions).transform(transactions)
    df_te = pd.DataFrame(te_array, columns=te.columns_)
    
    # 挖掘频繁项集
    frequent = apriori(df_te, min_support=min_support, use_colnames=True)
    if len(frequent) == 0:
        return pd.DataFrame()
    
    # 生成规则
    rules = association_rules(frequent, metric='confidence', min_threshold=min_confidence)
    rules = rules[rules['lift'] > 1]
    
    # 整理输出格式
    rules['antecedents'] = rules['antecedents'].apply(lambda x: ', '.join(list(x)))
    rules['consequents'] = rules['consequents'].apply(lambda x: ', '.join(list(x)))
    return rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']]

@rules_bp.route('/rules', methods=['POST'])
def get_rules():
    """POST 请求，接收 min_support 和 min_confidence，返回规则列表"""
    data = request.get_json()
    min_support = data.get('min_support', 0.1)
    min_confidence = data.get('min_confidence', 0.6)
    try:
        df = load_and_discretize()
        rules_df = generate_rules(df, min_support, min_confidence)
        if rules_df.empty:
            return jsonify({'success': True, 'rules': [], 'message': '未找到符合条件的规则，请降低支持度或置信度。'})
        return jsonify({'success': True, 'rules': rules_df.to_dict(orient='records')})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})