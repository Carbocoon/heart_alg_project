from utils.classification import predict_risk

def make_prediction(data):
    try:
        # 将前端传来的字符串转数值
        processed_data = {}
        for k, v in data.items():
            if v == '':
                continue
            try:
                processed_data[k] = float(v)
            except ValueError:
                processed_data[k] = v
        
        result_df = predict_risk(processed_data)
        prob = float(result_df.iloc[0]["pred_prob"])
        label = int(result_df.iloc[0]["pred_label"])
        
        if label == 1:
            class_name = '高危心脏病预警'
            message = '经随机森林模型全面评估，您的多项指标异常，罹患心血管疾病的概率较高，建议您立即就医复查。'
        else:
            class_name = '低风险，状态良好'
            message = '您的关键指标目前在正常或低风险区间，请继续保持健康的生活方式！'
        
        return {
            'success': True,
            'prediction': label,
            'risk_prob': prob,
            'class_name': class_name,
            'message': message
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}