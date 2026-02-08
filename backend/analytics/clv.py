"""
Customer Lifetime Value Module
Calculates and analyzes customer lifetime value
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CustomerLifetimeValue:
    """Calculates Customer Lifetime Value (CLV)"""
    
    def __init__(self, df: pd.DataFrame, time_horizon_months: int = 12):
        self.df = df.copy()
        self.time_horizon = time_horizon_months
        self.clv_data: pd.DataFrame = None
        
    def calculate_clv_metrics(self) -> pd.DataFrame:
        """Calculate CLV metrics for each customer"""
        if 'customer_id' not in self.df.columns:
            raise ValueError("customer_id column required for CLV calculation")
        
        # Calculate customer-level metrics
        clv = self.df.groupby('customer_id').agg({
            'transaction_id': 'nunique',
            'transaction_amount': ['sum', 'mean'],
            'transaction_date': ['min', 'max', 'count']
        }).reset_index()
        
        clv.columns = ['customer_id', 'total_orders', 'total_revenue', 
                      'avg_order_value', 'first_purchase', 'last_purchase', 'total_transactions']
        
        # Calculate metrics
        # Customer lifespan in days
        clv['lifespan_days'] = (clv['last_purchase'] - clv['first_purchase']).dt.days
        clv['lifespan_days'] = clv['lifespan_days'].replace(0, 1)  # Avoid division by zero
        
        # Purchase frequency (orders per month)
        clv['lifespan_months'] = clv['lifespan_days'] / 30.44  # Average days per month
        clv['purchase_frequency'] = clv['total_orders'] / clv['lifespan_months'].replace(0, 1)
        
        # Calculate CLV components
        # Average profit margin (assuming 30% margin)
        profit_margin = 0.30
        
        # Customer Value = Average Order Value * Purchase Frequency
        clv['customer_value_monthly'] = clv['avg_order_value'] * clv['purchase_frequency']
        
        # Simple CLV = Customer Value * Avg Customer Lifespan (in months)
        avg_lifespan_months = clv['lifespan_months'].mean()
        clv['simple_clv'] = clv['customer_value_monthly'] * avg_lifespan_months
        
        # Predictive CLV (for next time_horizon months)
        clv['predictive_clv'] = clv['customer_value_monthly'] * self.time_horizon
        
        # CLV with profit margin
        clv['clv_profit'] = clv['predictive_clv'] * profit_margin
        
        # Churn probability (based on recency)
        max_date = self.df['transaction_date'].max()
        clv['days_since_last'] = (max_date - clv['last_purchase']).dt.days
        avg_gap = clv['lifespan_days'] / clv['total_orders']
        clv['churn_probability'] = np.minimum(clv['days_since_last'] / (avg_gap * 3), 1)
        
        # Risk-adjusted CLV
        clv['risk_adjusted_clv'] = clv['predictive_clv'] * (1 - clv['churn_probability'])
        
        # Round numeric columns
        numeric_cols = ['total_revenue', 'avg_order_value', 'lifespan_months', 
                       'purchase_frequency', 'customer_value_monthly', 'simple_clv',
                       'predictive_clv', 'clv_profit', 'churn_probability', 'risk_adjusted_clv']
        for col in numeric_cols:
            if col in clv.columns:
                clv[col] = clv[col].round(2)
        
        self.clv_data = clv
        logger.info(f"CLV calculated for {len(clv)} customers")
        
        return clv
    
    def get_clv_segments(self) -> pd.DataFrame:
        """Segment customers by CLV"""
        if self.clv_data is None:
            self.calculate_clv_metrics()
        
        clv = self.clv_data.copy()
        
        # Create CLV tiers
        clv['clv_tier'] = pd.qcut(
            clv['predictive_clv'].rank(method='first'),
            q=5,
            labels=['Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond']
        )
        
        return clv
    
    def get_clv_summary(self) -> Dict[str, Any]:
        """Get CLV summary statistics"""
        if self.clv_data is None:
            self.calculate_clv_metrics()
        
        clv = self.clv_data
        
        return {
            'total_customers': len(clv),
            'total_historical_revenue': round(clv['total_revenue'].sum(), 2),
            'total_predicted_clv': round(clv['predictive_clv'].sum(), 2),
            'avg_clv': round(clv['predictive_clv'].mean(), 2),
            'median_clv': round(clv['predictive_clv'].median(), 2),
            'max_clv': round(clv['predictive_clv'].max(), 2),
            'min_clv': round(clv['predictive_clv'].min(), 2),
            'avg_order_value': round(clv['avg_order_value'].mean(), 2),
            'avg_purchase_frequency': round(clv['purchase_frequency'].mean(), 2),
            'avg_churn_probability': round(clv['churn_probability'].mean(), 2),
            'total_risk_adjusted_clv': round(clv['risk_adjusted_clv'].sum(), 2)
        }
    
    def get_clv_distribution(self) -> List[Dict[str, Any]]:
        """Get CLV distribution for visualization"""
        if self.clv_data is None:
            self.calculate_clv_metrics()
        
        clv = self.clv_data
        
        # Create bins for distribution
        bins = [0, 100, 500, 1000, 5000, 10000, float('inf')]
        labels = ['$0-100', '$100-500', '$500-1K', '$1K-5K', '$5K-10K', '$10K+']
        
        clv['clv_bucket'] = pd.cut(clv['predictive_clv'], bins=bins, labels=labels)
        
        distribution = clv.groupby('clv_bucket').agg({
            'customer_id': 'count',
            'predictive_clv': 'sum'
        }).reset_index()
        distribution.columns = ['bucket', 'customer_count', 'total_clv']
        
        return distribution.to_dict(orient='records')
    
    def get_top_value_customers(self, n: int = 20) -> List[Dict[str, Any]]:
        """Get top customers by CLV"""
        if self.clv_data is None:
            self.calculate_clv_metrics()
        
        top = self.clv_data.nlargest(n, 'predictive_clv')[[
            'customer_id', 'total_orders', 'total_revenue', 'avg_order_value',
            'purchase_frequency', 'predictive_clv', 'risk_adjusted_clv', 'churn_probability'
        ]]
        
        top['customer_id'] = top['customer_id'].astype(int)
        
        return top.to_dict(orient='records')
    
    def get_at_risk_customers(self, n: int = 20) -> List[Dict[str, Any]]:
        """Get high-value customers at risk of churning"""
        if self.clv_data is None:
            self.calculate_clv_metrics()
        
        # High CLV with high churn probability
        at_risk = self.clv_data[
            (self.clv_data['predictive_clv'] > self.clv_data['predictive_clv'].median()) &
            (self.clv_data['churn_probability'] > 0.5)
        ].nlargest(n, 'predictive_clv')[[
            'customer_id', 'total_orders', 'total_revenue', 'days_since_last',
            'predictive_clv', 'churn_probability'
        ]]
        
        if len(at_risk) > 0:
            at_risk['customer_id'] = at_risk['customer_id'].astype(int)
        
        return at_risk.to_dict(orient='records')
    
    def get_clv_data(self) -> pd.DataFrame:
        """Return CLV data"""
        if self.clv_data is None:
            self.calculate_clv_metrics()
        return self.clv_data
    
    def get_clv_report(self) -> Dict[str, Any]:
        """Generate comprehensive CLV report"""
        if self.clv_data is None:
            self.calculate_clv_metrics()
        
        return {
            'time_horizon_months': self.time_horizon,
            'summary': self.get_clv_summary(),
            'distribution': self.get_clv_distribution(),
            'top_customers': self.get_top_value_customers(10),
            'at_risk_customers': self.get_at_risk_customers(10),
            'metrics_explanation': {
                'predictive_clv': f"Expected revenue per customer over next {self.time_horizon} months",
                'risk_adjusted_clv': "CLV adjusted for churn probability",
                'purchase_frequency': "Average orders per month",
                'churn_probability': "Likelihood of customer not returning (0-1)"
            }
        }
