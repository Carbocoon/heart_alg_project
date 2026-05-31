import pandas as pd
import numpy as np
import os

def clean_heart_data(input_path, output_path):
    df = pd.read_csv(input_path)
    original_columns = df.columns.tolist()
    print("检测到原始列名:", original_columns)

    col_map = {}
    normalized_cols = []
    for col in original_columns:
        norm = col.strip().lower().replace('  ', ' ').replace('_', ' ')
        normalized_cols.append(norm)
        col_map[norm] = col

    # 检测格式
    is_uci = ('target' in normalized_cols and
              all(c in normalized_cols for c in ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs',
                                                  'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal']))
    has_heart_rate = any('heartrate' in c for c in normalized_cols)
    has_sysbp = any('sysbp' in c for c in normalized_cols)
    has_totchol = any('totchol' in c for c in normalized_cols)
    has_target = any(('heart' in c and 'stroke' in c) or 'tenyearchd' in c for c in normalized_cols)
    is_framingham = has_heart_rate and has_sysbp and has_totchol and has_target

    if is_uci:
        print("检测到 UCI Heart Disease 格式")
        df_clean = _clean_uci_format(df)
    elif is_framingham:
        print("检测到 Framingham Heart Study 格式")
        df_clean = _convert_framingham_to_uci(df, col_map)
    else:
        if has_target:
            print("尝试按 Framingham 转换")
            df_clean = _convert_framingham_to_uci(df, col_map)
        else:
            raise ValueError(f"未知的数据集格式。实际列名：{original_columns}")

    df_clean.to_csv(output_path, index=False)
    assert not df_clean.isnull().any().any(), "转换后仍有空值！"
    print(f"清洗完成，共 {len(df_clean)} 条记录")
    return df_clean

def _clean_uci_format(df):
    df = df.copy()
    for col in df.columns:
        if df[col].isnull().any():
            if df[col].dtype in ['int64', 'float64']:
                df[col].fillna(df[col].median(), inplace=True)
            else:
                df[col].fillna(df[col].mode()[0], inplace=True)
    if 'trestbps' in df.columns:
        median_bp = df['trestbps'].median()
        df.loc[(df['trestbps'] < 80) | (df['trestbps'] > 200), 'trestbps'] = median_bp
    if 'chol' in df.columns:
        median_chol = df['chol'].median()
        df.loc[(df['chol'] < 100) | (df['chol'] > 600), 'chol'] = median_chol
    cat_cols = ['sex', 'cp', 'restecg', 'slope', 'thal']
    for col in cat_cols:
        if col in df.columns:
            df[col] = df[col].astype('category').cat.codes
    return df

def _convert_framingham_to_uci(df, col_map):
    df = df.copy()
    new = pd.DataFrame(index=df.index)

    # 辅助函数
    def get_col(keys):
        for key in keys:
            for norm, orig in col_map.items():
                if key in norm:
                    return orig
        return None

    # 基本字段
    new['age'] = pd.to_numeric(df['age'], errors='coerce')
    sex_col = get_col(['gender'])
    if sex_col:
        new['sex'] = df[sex_col].map({'Male': 1, 'Female': 0})
    else:
        new['sex'] = 0
    new['sex'] = pd.to_numeric(new['sex'], errors='coerce')
    new['cp'] = 0

    sysbp_col = get_col(['sysbp', 'sys bp'])
    if sysbp_col:
        new['trestbps'] = pd.to_numeric(df[sysbp_col], errors='coerce')
    else:
        raise KeyError("未找到收缩压字段")
    chol_col = get_col(['totchol', 'total cholesterol'])
    if chol_col:
        new['chol'] = pd.to_numeric(df[chol_col], errors='coerce')
    else:
        raise KeyError("未找到胆固醇字段")
    glucose_col = get_col(['glucose'])
    if glucose_col:
        glucose = pd.to_numeric(df[glucose_col], errors='coerce')
        new['fbs'] = (glucose > 120).astype(int)
    else:
        new['fbs'] = 0
    new['fbs'] = pd.to_numeric(new['fbs'], errors='coerce')
    new['restecg'] = 0
    hr_col = get_col(['heartrate', 'heart rate'])
    if hr_col:
        new['thalach'] = pd.to_numeric(df[hr_col], errors='coerce')
    else:
        raise KeyError("未找到心率字段")
    new['exang'] = 0
    new['oldpeak'] = 0.0
    new['slope'] = 0
    new['ca'] = 0
    new['thal'] = 0

    # target列
    target_col = None
    for norm, orig in col_map.items():
        if ('heart' in norm and 'stroke' in norm) or 'tenyearchd' in norm:
            target_col = orig
            break
    if target_col is None:
        raise ValueError("未找到目标列")
    target_vals = df[target_col].astype(str).str.strip().str.lower()
    new['target'] = target_vals.map({'yes': 1, 'no': 0}).fillna(0).astype(int)

    # 强制处理所有列：转换为数值，替换NaN为0，无穷为0
    for col in new.columns:
        new[col] = pd.to_numeric(new[col], errors='coerce')
        new[col] = new[col].fillna(0)
        new[col] = new[col].replace([np.inf, -np.inf], 0)
        if col != 'oldpeak':
            new[col] = new[col].round(0).astype(int)
        else:
            new[col] = new[col].astype(float)

    # 异常值后处理
    median_bp = new['trestbps'].median()
    new.loc[(new['trestbps'] < 80) | (new['trestbps'] > 250), 'trestbps'] = median_bp
    median_chol = new['chol'].median()
    new.loc[(new['chol'] < 100) | (new['chol'] > 600), 'chol'] = median_chol

    return new