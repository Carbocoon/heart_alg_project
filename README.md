# 心脏病风险智能分析与预测系统 (Heart Disease Risk Analysis & Prediction)

基于 Flask + 原生 JavaScript + ECharts 构建的心脏病数据智能分析与风险预测平台。本项目支持心血管疾病数据的导入、清洗、态势感知、患者聚类分析以及基于机器学习（随机森林）的实时风险预测。

## 核心功能

- **数据态势感知大屏**: 实时展示患者记录总数、患病率、平均年龄等 KPI；可视化各项健康指标（年龄段、血压、性别分布等）的图表特征。
- **数据导入与清洗**: 支持通过 CSV 文件批量上传心脏病数据，提供上传预览与结构化数据入库（SQLite），支持一键“撤销导入”回滚操作。
- **实时风险预测**: 内置基于 Scikit-Learn 的随机森林（Random Forest）分类器，可输入患者 13 项体征指标进行即时发病风险（概率）预测。
- **模型性能自动评估**: 动态生成与展示分类报告、混淆矩阵热力图及特征重要性条形图（具备自愈与自动重训机制）。
- **患者聚类分析 (K-Means)**: 通过无监督学习对患者特征进行自动聚类（如年龄 vs 胆固醇），挖掘高维潜藏联系。
- **清洗数据概览**: 直连数据库的动态数据表格视图，支持实时刷新与全量的体征特征概览。

## 技术栈

- **后端架构**: Python 3.x, Flask 3.0+ (Blueprint 模块化路由)
- **前端架构**: HTML5, Bootstrap 5, 原生 JS (Fetch API 纯动态渲染), SPA 单页应用设计
- **数据可视化**: Apache ECharts 5.4
- **机器学习**: Scikit-Learn (RandomForest, KMeans), Pandas, Numpy
- **持久化存储**: SQLite3 (`dim_patient` 与 `fact_health_record` 表)

## 核心目录结构

```text
heart_alg_project/
├── app.py                  # Flask 主应用入口
├── data/                   # 存放上传与清洗后的数据集文件 (CSV)
├── models/                 # 存放序列化的机器学习模型 (.pkl) 与性能评价 (.json)
├── routes/                 # Flask 路由总线
│   ├── dashboard.py        # 大屏统计指标逻辑
│   ├── predict.py          # 实时分类预测逻辑
│   ├── clustering.py       # KMeans 聚类逻辑
│   ├── data.py             # 原始数据检索逻辑
│   ├── performance.py      # 模型性能解析及自动重训触发
│   └── upload.py           # 数据上传预览、保存及回退逻辑
├── services/               # 核心业务层 (数据库操作等)
├── utils/                  # 工具类及算法支持模块 (分类/聚类等)
├── templates/              # HTML 视图文件
├── static/                 # 静态资源 (css/, js/main.js, img/)
└── requirements.txt        # 项目依赖清单
```

## 快速启动

1. **环境准备**
   推荐在当前目录下创建并激活虚拟环境：
   ```bash
   python -m venv venv
   # Windows 激活
   .\venv\Scripts\activate
   # 终端出现 (venv) 标记即代表进入
   ```

2. **安装依赖项目**
   ```bash
   pip install -r requirements.txt
   ```

3. **启动后台 Flask 核心服务**
   ```bash
   python app.py
   ```
   > 正常启动后将看到 `Running on http://127.0.0.1:5000`

4. **系统访问**
   打开浏览器，访问: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## 数据特征字典参考

| 缩写 | 全称/含义 | 值域与说明 |
| :--- | :--- | :--- |
| `age` | 年龄 | |
| `sex` | 性别 | 1 = 男, 0 = 女 |
| `cp` | 胸痛类型 (Chest Pain) | 分为四个等级或类型 |
| `trestbps` | 静息血压 | mmHg |
| `chol` | 胆固醇 (Cholesterol) | mg/dl |
| `fbs` | 空腹血糖 (Fasting Blood Sugar) | 1 = 大于120mg/dl, 0 = 否则 |
| `restecg` | 静息心电图结果 | |
| `thalach` | 最大心跳率 | |
| `exang` | 运动引起的心绞痛 | 1 = 是, 0 = 否 |
| `oldpeak` | 相关ST段压低 | |
| `slope` | 运动高峰ST段的坡度 | |
| `ca` | 萤光透视的主要血管数量 | 0 - 3 |
| `thal` | 地中海贫血 | |
| `target`| **患病结果标签** | 1 = 患病 / 具有并发风险, 0 = 正常 |
