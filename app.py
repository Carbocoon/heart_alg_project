import os
from flask import Flask, render_template

# 导入路由蓝图 (Blueprints)
from routes.dashboard import dashboard_bp
from routes.upload import upload_bp
from routes.predict import predict_bp
from routes.clustering import clustering_bp
from routes.data import data_bp
from routes.performance import performance_bp

app = Flask(__name__)

# 注册所有模块化路由
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
app.register_blueprint(upload_bp, url_prefix='/api/upload')
app.register_blueprint(predict_bp, url_prefix='/api/predict')
app.register_blueprint(clustering_bp, url_prefix='/api/clustering')
app.register_blueprint(data_bp, url_prefix='/api/data')
app.register_blueprint(performance_bp, url_prefix='/api')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    print('启动 Flask 医疗核心分析平台 (模块化重构版)...')
    app.run(debug=True, port=5000)

