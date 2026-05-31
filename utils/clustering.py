import os
import pandas as pd
from flask import Blueprint, jsonify

clustering_bp = Blueprint('clustering', __name__)

@clustering_bp.route('/', methods=['GET'], strict_slashes=False)
def get_clustering():
    try:
        # 优先使用清洗后的数据，如果不存在则使用原始数据
        base_dir = os.path.dirname(os.path.dirname(__file__))
        cleaned_path = os.path.join(base_dir, "data", "cleaned_heart.csv")
        raw_path = os.path.join(base_dir, "data", "heart.csv")
        
        if os.path.exists(cleaned_path):
            df = pd.read_csv(cleaned_path)
        elif os.path.exists(raw_path):
            df = pd.read_csv(raw_path)
        else:
            return jsonify({'success': False, 'error': '未找到数据文件，请先上传数据集'})
        
        # 确保存在 age 和 chol 列
        if 'age' not in df.columns or 'chol' not in df.columns:
            return jsonify({'success': False, 'error': '数据中缺少 age 或 chol 字段'})
        
        # 提取特征并删除缺失值
        X = df[['age', 'chol']].dropna()
        if len(X) < 3:
            return jsonify({'success': False, 'error': '有效数据点不足3个，无法聚类'})
        
        # 执行 K-Means 聚类
        from sklearn.cluster import KMeans
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X)
        
        # 准备散点图数据：每个点 [age, chol, cluster_label]
        scatter_data = X.values.tolist()
        for i, point in enumerate(scatter_data):
            point.append(int(labels[i]))
        
        # 准备聚类中心坐标
        centers = kmeans.cluster_centers_.tolist()
        
        return jsonify({
            'success': True,
            'data': {
                'cluster_centers': centers,
                'scatter_data': scatter_data
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})