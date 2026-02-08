"""
Performance Analysis Module
Analyzes monthly and category performance
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class PerformanceAnalysis:
    """Analyzes business performance metrics"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        
    def get_monthly_performance(self) -> List[Dict[str, Any]]:
        """Get monthly performance metrics"""
        if 'transaction_date' not in self.df.columns:
            return []
        
        monthly = self.df.groupby(self.df['transaction_date'].dt.to_period('M')).agg({
            'transaction_id': 'nunique',
            'transaction_amount': ['sum', 'mean', 'count'],
            'quantity': 'sum',
            'customer_id': 'nunique' if 'customer_id' in self.df.columns else lambda x: 0
        }).reset_index()
        
        monthly.columns = ['period', 'unique_transactions', 'revenue', 
                          'avg_transaction', 'transaction_count', 'items_sold', 'unique_customers']
        
        monthly['period'] = monthly['period'].astype(str)
        
        # Calculate growth rates
        monthly['revenue_growth'] = monthly['revenue'].pct_change() * 100
        monthly['customer_growth'] = monthly['unique_customers'].pct_change() * 100
        monthly['transaction_growth'] = monthly['unique_transactions'].pct_change() * 100
        
        # Round values
        for col in ['revenue', 'avg_transaction', 'revenue_growth', 'customer_growth', 'transaction_growth']:
            monthly[col] = monthly[col].round(2)
        
        # Fill NaN growth values
        monthly = monthly.fillna(0)
        
        return monthly.to_dict(orient='records')
    
    def get_quarterly_performance(self) -> List[Dict[str, Any]]:
        """Get quarterly performance metrics"""
        if 'transaction_date' not in self.df.columns:
            return []
        
        quarterly = self.df.groupby(self.df['transaction_date'].dt.to_period('Q')).agg({
            'transaction_id': 'nunique',
            'transaction_amount': 'sum',
            'customer_id': 'nunique' if 'customer_id' in self.df.columns else lambda x: 0
        }).reset_index()
        
        quarterly.columns = ['period', 'transactions', 'revenue', 'customers']
        quarterly['period'] = quarterly['period'].astype(str)
        
        # Calculate QoQ growth
        quarterly['revenue_growth'] = (quarterly['revenue'].pct_change() * 100).round(2).fillna(0)
        quarterly['revenue'] = quarterly['revenue'].round(2)
        
        return quarterly.to_dict(orient='records')
    
    def get_yearly_performance(self) -> List[Dict[str, Any]]:
        """Get yearly performance metrics"""
        if 'transaction_date' not in self.df.columns:
            return []
        
        yearly = self.df.groupby(self.df['transaction_date'].dt.year).agg({
            'transaction_id': 'nunique',
            'transaction_amount': 'sum',
            'customer_id': 'nunique' if 'customer_id' in self.df.columns else lambda x: 0
        }).reset_index()
        
        yearly.columns = ['year', 'transactions', 'revenue', 'customers']
        
        # Calculate YoY growth
        yearly['revenue_growth'] = (yearly['revenue'].pct_change() * 100).round(2).fillna(0)
        yearly['revenue'] = yearly['revenue'].round(2)
        
        return yearly.to_dict(orient='records')
    
    def get_category_performance(self) -> List[Dict[str, Any]]:
        """Get performance by product category"""
        if 'product_type' not in self.df.columns:
            return []
        
        category = self.df.groupby('product_type').agg({
            'transaction_id': 'nunique',
            'transaction_amount': ['sum', 'mean'],
            'quantity': 'sum',
            'customer_id': 'nunique' if 'customer_id' in self.df.columns else lambda x: 0
        }).reset_index()
        
        category.columns = ['category', 'transactions', 'revenue', 
                          'avg_transaction', 'items_sold', 'unique_customers']
        
        # Calculate market share
        total_revenue = category['revenue'].sum()
        category['market_share'] = (category['revenue'] / total_revenue * 100).round(2)
        
        # Round values
        category['revenue'] = category['revenue'].round(2)
        category['avg_transaction'] = category['avg_transaction'].round(2)
        
        return category.sort_values('revenue', ascending=False).to_dict(orient='records')
    
    def get_country_performance(self) -> List[Dict[str, Any]]:
        """Get performance by country"""
        if 'country' not in self.df.columns:
            return []
        
        country = self.df.groupby('country').agg({
            'transaction_id': 'nunique',
            'transaction_amount': ['sum', 'mean'],
            'quantity': 'sum',
            'customer_id': 'nunique' if 'customer_id' in self.df.columns else lambda x: 0
        }).reset_index()
        
        country.columns = ['country', 'transactions', 'revenue', 
                          'avg_transaction', 'items_sold', 'unique_customers']
        
        # Calculate market share
        total_revenue = country['revenue'].sum()
        country['market_share'] = (country['revenue'] / total_revenue * 100).round(2)
        
        # Round values
        country['revenue'] = country['revenue'].round(2)
        country['avg_transaction'] = country['avg_transaction'].round(2)
        
        return country.sort_values('revenue', ascending=False).to_dict(orient='records')
    
    def get_day_of_week_performance(self) -> List[Dict[str, Any]]:
        """Get performance by day of week"""
        if 'transaction_date' not in self.df.columns:
            return []
        
        self.df['dow'] = self.df['transaction_date'].dt.dayofweek
        
        dow_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        dow = self.df.groupby('dow').agg({
            'transaction_id': 'nunique',
            'transaction_amount': 'sum'
        }).reset_index()
        
        dow['day_name'] = dow['dow'].map(lambda x: dow_names[x])
        dow.columns = ['dow', 'transactions', 'revenue', 'day']
        dow['revenue'] = dow['revenue'].round(2)
        
        return dow[['day', 'transactions', 'revenue']].to_dict(orient='records')
    
    def get_product_performance(self, top_n: int = 20) -> List[Dict[str, Any]]:
        """Get top performing products"""
        if 'transaction_item_code' not in self.df.columns:
            return []
        
        product = self.df.groupby(['transaction_item_code', 'transaction_item_description']).agg({
            'transaction_id': 'nunique',
            'transaction_amount': 'sum',
            'quantity': 'sum',
            'customer_id': 'nunique' if 'customer_id' in self.df.columns else lambda x: 0
        }).reset_index()
        
        product.columns = ['product_code', 'description', 'transactions', 
                          'revenue', 'quantity_sold', 'unique_customers']
        
        product['revenue'] = product['revenue'].round(2)
        product['avg_price'] = (product['revenue'] / product['quantity_sold']).round(2)
        
        return product.nlargest(top_n, 'revenue').to_dict(orient='records')
    
    def get_cohort_analysis(self) -> Dict[str, Any]:
        """Perform simple cohort analysis"""
        if 'customer_id' not in self.df.columns or 'transaction_date' not in self.df.columns:
            return {}
        
        # Get first purchase month for each customer
        customer_first = self.df.groupby('customer_id')['transaction_date'].min().reset_index()
        customer_first.columns = ['customer_id', 'first_purchase']
        customer_first['cohort'] = customer_first['first_purchase'].dt.to_period('M').astype(str)
        
        # Merge with transactions
        df_cohort = self.df.merge(customer_first[['customer_id', 'cohort']], on='customer_id')
        df_cohort['transaction_month'] = df_cohort['transaction_date'].dt.to_period('M').astype(str)
        
        # Calculate cohort metrics
        cohort_data = df_cohort.groupby(['cohort', 'transaction_month']).agg({
            'customer_id': 'nunique',
            'transaction_amount': 'sum'
        }).reset_index()
        
        cohort_data.columns = ['cohort', 'transaction_month', 'customers', 'revenue']
        cohort_data['revenue'] = cohort_data['revenue'].round(2)
        
        return {
            'cohort_data': cohort_data.to_dict(orient='records'),
            'cohorts': sorted(cohort_data['cohort'].unique().tolist())
        }
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        return {
            'generated_at': datetime.now().isoformat(),
            'monthly': self.get_monthly_performance(),
            'quarterly': self.get_quarterly_performance(),
            'yearly': self.get_yearly_performance(),
            'by_category': self.get_category_performance(),
            'by_country': self.get_country_performance(),
            'by_day_of_week': self.get_day_of_week_performance(),
            'top_products': self.get_product_performance(20)
        }
