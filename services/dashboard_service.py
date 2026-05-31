from utils.db_utils import get_connection

def get_dashboard_metrics():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM fact_health_record')
        total_result = cursor.fetchone()
        total = total_result[0] if total_result else 0
        
        if total > 0:
            cursor.execute('SELECT SUM(target) FROM fact_health_record')
            disease_count = cursor.fetchone()[0] or 0
            rate = f'{(disease_count / total * 100):.1f}%'
            
            cursor.execute('SELECT AVG(age) FROM dim_patient')
            avg_age = int(cursor.fetchone()[0] or 0)
            
            cursor.execute('''
                SELECT p.age_group, COUNT(f.record_id) 
                FROM dim_patient p
                JOIN fact_health_record f ON p.patient_key = f.patient_key
                WHERE f.target = 1
                GROUP BY p.age_group
            ''')
            age_rows = cursor.fetchall()
            age_dist = [{'age_group': row[0], 'count': row[1]} for row in age_rows]
            
            cursor.execute('''
                SELECT p.sex_desc, COUNT(f.record_id)
                FROM dim_patient p
                JOIN fact_health_record f ON p.patient_key = f.patient_key
                WHERE f.target = 1
                GROUP BY p.sex_desc
            ''')
            sex_rows = cursor.fetchall()
            sex_dist = [{'value': row[1], 'name': f'{row[0]}性患病'} for row in sex_rows]

            cursor.execute('''
                SELECT p.cp_desc, COUNT(f.record_id)
                FROM dim_patient p
                JOIN fact_health_record f ON p.patient_key = f.patient_key
                WHERE f.target = 1
                GROUP BY p.cp_desc
            ''')
            cp_rows = cursor.fetchall()
            cp_dist = [{'cp_type': row[0], 'count': row[1]} for row in cp_rows]

            cursor.execute('''
                SELECT 
                    CASE WHEN fbs = 1 THEN '血糖>120mg/dl' ELSE '血糖正常' END as fbs_type,
                    SUM(target) * 100.0 / COUNT(record_id) as disease_rate
                FROM fact_health_record
                GROUP BY fbs
            ''')
            fbs_rows = cursor.fetchall()
            fbs_dist = [{'name': row[0], 'value': round(row[1], 1)} for row in fbs_rows]
            
        else:
            rate, avg_age = '0%', 0
            age_dist, sex_dist, cp_dist, fbs_dist = [], [], [], []
            
        conn.close()

        return {
            'success': True,
            'kpis': {'total': total, 'heart_disease_rate': rate, 'avg_age': avg_age},
            'charts': {
                'age_dist': age_dist,
                'sex_dist': sex_dist,
                'cp_dist': cp_dist,
                'fbs_dist': fbs_dist
            }
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}