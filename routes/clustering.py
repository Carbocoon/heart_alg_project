import os
import pandas as pd
from flask import Blueprint, jsonify

clustering_bp = Blueprint('clustering', __name__)

@clustering_bp.route('/', methods=['GET'], strict_slashes=False)
def get_clustering():
    try:
        # 尝试读取清洗后的数据，如果没有则读原始数据
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "cleaned_heart.csv")
        if not os.path.exists(data_path):
            data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "heart.csv")
            
        if not os.path.exists(data_path):
            return jsonify({'success': False, 'error': '未找到数据文件'})

        df = pd.read_csv(data_path)
        
        if 'age' not in df.columns or 'chol' not in df.columns:
            return jsonify({'success': False, 'error': '数据中缺失 age 或 chol 字段'})
            
        X = df[['age', 'chol']].dropna()

        # 如果没有安装 sklearn，可以使用模拟的分类，但为了严谨，我们直接用 pandas 和 KMeans
        try:
            from sklearn.cluster import KMeans
            kmeans = KMeans(n_clusters=3, random_state=42)
            labels = kmeans.fit_predict(X)
            centers = kmeans.cluster_centers_.tolist()
        except ImportError:
            return jsonify({'success': False, 'error': '请安装 scikit-learn: pip install scikit-learn'})
        
        scatter_data = []
        for i, row in enumerate(X.values):
            scatter_data.append([float(row[0]), float(row[1]), int(labels[i])])
            
        return jsonify({
            'success': True,
            'data': {
                'cluster_centers': centers,
                'scatter_data': scatter_data
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
