import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
import json
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "cleaned_heart.csv")
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "heart_model.pkl")
PERF_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "model_performance.json")
FEATURE_COLS = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach",
    "exang", "oldpeak", "slope", "ca", "thal"
]
TARGET_COL = "target"

_model = None

def _load_or_train_model():
    """加载或训练模型（单例）"""
    global _model
    if _model is not None:
        return _model
    if os.path.exists(MODEL_PATH):
        _model = joblib.load(MODEL_PATH)
        return _model
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError("找不到训练数据，请先上传数据集。")
    df = pd.read_csv(DATA_PATH)
    X = df[FEATURE_COLS]
    y = df[TARGET_COL]
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    _model = model
    return model

def evaluate_and_save_performance(model, X, y, save_path=PERF_PATH):
    """评估模型并将指标保存为 JSON 文件"""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    y_pred = model.predict(X_test)
    accuracy = model.score(X_test, y_test)
    report = classification_report(y_test, y_pred, output_dict=True)
    cm = confusion_matrix(y_test, y_pred).tolist()
    feature_importance = model.feature_importances_.tolist()
    performance = {
        'accuracy': accuracy,
        'classification_report': report,
        'confusion_matrix': cm,
        'feature_importance': feature_importance,
        'feature_names': FEATURE_COLS
    }
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, 'w') as f:
        json.dump(performance, f, indent=2)
    print(f"模型性能指标已保存至 {save_path}")
    return performance

def retrain_model(csv_path=None):
    """使用指定的 CSV 重新训练模型并保存，同时保存性能指标"""
    global _model
    if csv_path is None:
        csv_path = DATA_PATH
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"训练数据不存在: {csv_path}")
    df = pd.read_csv(csv_path)
    missing_cols = [col for col in FEATURE_COLS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"缺少特征列: {missing_cols}")
    if TARGET_COL not in df.columns:
        raise ValueError(f"缺少目标列: {TARGET_COL}")
    X = df[FEATURE_COLS]
    y = df[TARGET_COL]
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    _model = model
    print(f"模型已重新训练并保存至 {MODEL_PATH}")
    # 评估并保存性能
    evaluate_and_save_performance(model, X, y)
    return model

def predict_risk(input_data):
    """预测风险，输入字典或列表，返回DataFrame"""
    model = _load_or_train_model()
    if isinstance(input_data, dict):
        input_df = pd.DataFrame([input_data])
    elif isinstance(input_data, list):
        input_df = pd.DataFrame(input_data)
    elif isinstance(input_data, pd.DataFrame):
        input_df = input_data.copy()
    else:
        raise ValueError("输入格式不支持")
    for col in FEATURE_COLS:
        if col not in input_df.columns:
            input_df[col] = 0
    X_pred = input_df[FEATURE_COLS]
    pred_label = model.predict(X_pred)
    pred_prob = model.predict_proba(X_pred)[:, 1]
    result = input_df.copy()
    result["pred_label"] = pred_label
    result["pred_prob"] = pred_prob
    return result