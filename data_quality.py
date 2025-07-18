import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DataQualityMonitor:
    """Advanced data quality monitoring for Salesforce data"""
    
    def __init__(self, sf_connection):
        self.sf = sf_connection
        self.quality_thresholds = {
            'missing_data_threshold': 10,  # % of missing data that triggers alert
            'anomaly_z_score': 3,          # Z-score threshold for anomalies
            'duplicate_threshold': 5,       # % of duplicates that triggers alert
        }
    
    def analyze_accounts(self):
        """Analyze Account data quality"""
        query = """
        SELECT Id, Name, Phone, BillingStreet, BillingCity, 
               AnnualRevenue, Industry, Type, CreatedDate
        FROM Account 
        WHERE CreatedDate = LAST_N_DAYS:30
        LIMIT 2000
        """
        
        data = self.sf.query_all(query)
        if not data['records']:
            return {}
        
        df = pd.DataFrame(data['records'])
        issues = {}
        
        # Check for missing critical fields
        critical_fields = ['Name', 'Phone', 'BillingStreet']
        for field in critical_fields:
            if field in df.columns:
                missing_pct = (df[field].isna().sum() / len(df)) * 100
                if missing_pct > self.quality_thresholds['missing_data_threshold']:
                    issues[f'missing_{field.lower()}'] = {
                        'severity': 'HIGH' if missing_pct > 25 else 'MEDIUM',
                        'count': df[field].isna().sum(),
                        'percentage': missing_pct,
                        'message': f'{missing_pct:.1f}% of accounts missing {field}'
                    }
        
        # Check for revenue anomalies using statistical analysis
        if 'AnnualRevenue' in df.columns:
            revenues = pd.to_numeric(df['AnnualRevenue'], errors='coerce').dropna()
            if len(revenues) > 10:
                z_scores = np.abs(stats.zscore(revenues))
                anomalies = revenues[z_scores > self.quality_thresholds['anomaly_z_score']]
                if len(anomalies) > 0:
                    issues['revenue_anomalies'] = {
                        'severity': 'MEDIUM',
                        'count': len(anomalies),
                        'percentage': (len(anomalies) / len(revenues)) * 100,
                        'message': f'{len(anomalies)} accounts with unusual revenue values',
                        'anomaly_values': anomalies.tolist()[:5]  # Show top 5
                    }
        
        return issues
    
    def calculate_quality_score(self, issues_dict):
        """Calculate overall data quality score"""
        if not issues_dict:
            return 100
        
        total_score = 100
        penalty_weights = {'HIGH': 10, 'MEDIUM': 5, 'LOW': 2}
        
        for object_name, object_issues in issues_dict.items():
            for issue_name, issue_data in object_issues.items():
                if isinstance(issue_data, dict) and 'severity' in issue_data:
                    penalty = penalty_weights.get(issue_data['severity'], 2)
                    percentage = issue_data.get('percentage', 0)
                    total_score -= min(penalty * (percentage / 10), 20)
        
        return max(0, round(total_score, 1))
