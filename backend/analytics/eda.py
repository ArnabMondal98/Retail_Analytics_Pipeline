"""
Exploratory Data Analysis Module
Generates insights and statistics from the dataset
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class ExploratoryDataAnalysis:
    """Performs exploratory data analysis on retail data"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.insights: List[Dict[str, Any]] = []
        
    def get_basic_statistics(self) -> Dict[str, Any]:
        """Get basic statistical measures"""
        numeric_stats = {}
        numeric_cols = self.df.select_dtypes(include=['int64', 'float64']).columns
        
        for col in numeric_cols:
            numeric_stats[col] = {
                'count': int(self.df[col].count()),
                'mean': round(float(self.df[col].mean()), 2),
                'std': round(float(self.df[col].std()), 2),
                'min': round(float(self.df[col].min()), 2),
                'q25': round(float(self.df[col].quantile(0.25)), 2),
                'median': round(float(self.df[col].median()), 2),
                'q75': round(float(self.df[col].quantile(0.75)), 2),
                'max': round(float(self.df[col].max()), 2)
            }
        
        return numeric_stats
    
    def get_distribution_analysis(self) -> Dict[str, Any]:
        """Analyze distributions of key metrics"""
        distributions = {}
        
        # Transaction amount distribution
        if 'transaction_amount' in self.df.columns:
            bins = [0, 10, 25, 50, 100, 250, 500, 1000, float('inf')]
            labels = ['0-10', '10-25', '25-50', '50-100', '100-250', '250-500', '500-1000', '1000+']
            dist = pd.cut(self.df['transaction_amount'], bins=bins, labels=labels)
            distributions['transaction_amount'] = dist.value_counts().to_dict()
        
        # Quantity distribution
        if 'quantity' in self.df.columns:
            bins = [0, 1, 5, 10, 25, 50, 100, float('inf')]
            labels = ['1', '2-5', '6-10', '11-25', '26-50', '51-100', '100+']
            dist = pd.cut(self.df['quantity'], bins=bins, labels=labels)
            distributions['quantity'] = dist.value_counts().to_dict()
        
        return distributions
    
    def get_temporal_analysis(self) -> Dict[str, Any]:
        """Analyze temporal patterns"""
        temporal = {}
        
        if 'transaction_date' not in self.df.columns:
            return temporal
        
        # Monthly trends
        monthly = self.df.groupby(self.df['transaction_date'].dt.to_period('M')).agg({
            'transaction_id': 'nunique',
            'transaction_amount': 'sum',
            'customer_id': 'nunique' if 'customer_id' in self.df.columns else lambda x: 0
        }).reset_index()
        monthly['transaction_date'] = monthly['transaction_date'].astype(str)
        monthly.columns = ['period', 'transactions', 'revenue', 'customers']
        temporal['monthly'] = monthly.to_dict(orient='records')
        
        # Day of week analysis
        if 'day_of_week' in self.df.columns:
            dow_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            dow = self.df.groupby('day_of_week').agg({
                'transaction_id': 'count',
                'transaction_amount': 'sum'
            }).reset_index()
            dow['day_name'] = dow['day_of_week'].map(lambda x: dow_names[x])
            temporal['day_of_week'] = dow.to_dict(orient='records')
        
        # Hourly patterns (if time data available)
        if hasattr(self.df['transaction_date'].dt, 'hour'):
            hourly = self.df.groupby(self.df['transaction_date'].dt.hour).agg({
                'transaction_id': 'count',
                'transaction_amount': 'sum'
            }).reset_index()
            hourly.columns = ['hour', 'transactions', 'revenue']
            temporal['hourly'] = hourly.to_dict(orient='records')
        
        return temporal
    
    def get_categorical_analysis(self) -> Dict[str, Any]:
        """Analyze categorical variables"""
        categorical = {}
        
        # Country analysis
        if 'country' in self.df.columns:
            country_stats = self.df.groupby('country').agg({
                'transaction_id': 'nunique',
                'transaction_amount': 'sum',
                'customer_id': 'nunique' if 'customer_id' in self.df.columns else lambda x: 0
            }).reset_index()
            country_stats.columns = ['country', 'transactions', 'revenue', 'customers']
            country_stats = country_stats.sort_values('revenue', ascending=False).head(20)
            categorical['country'] = country_stats.to_dict(orient='records')
        
        # Product type analysis
        if 'product_type' in self.df.columns:
            product_stats = self.df.groupby('product_type').agg({
                'transaction_id': 'nunique',
                'transaction_amount': 'sum',
                'quantity': 'sum'
            }).reset_index()
            product_stats.columns = ['product_type', 'transactions', 'revenue', 'quantity']
            product_stats = product_stats.sort_values('revenue', ascending=False).head(20)
            categorical['product_type'] = product_stats.to_dict(orient='records')
        
        return categorical
    
    def get_correlation_analysis(self) -> Dict[str, Any]:
        """Analyze correlations between numeric variables"""
        numeric_cols = ['quantity', 'price', 'transaction_amount']
        available_cols = [col for col in numeric_cols if col in self.df.columns]
        
        if len(available_cols) < 2:
            return {}
        
        corr_matrix = self.df[available_cols].corr()
        
        return {
            'correlation_matrix': corr_matrix.round(3).to_dict()
        }
    
    def get_top_products(self, n: int = 10) -> List[Dict[str, Any]]:
        """Get top products by revenue"""
        if 'transaction_item_code' not in self.df.columns:
            return []
        
        top = self.df.groupby(['transaction_item_code', 'transaction_item_description']).agg({
            'transaction_amount': 'sum',
            'quantity': 'sum',
            'transaction_id': 'nunique'
        }).reset_index()
        top.columns = ['product_code', 'description', 'revenue', 'quantity_sold', 'transactions']
        top = top.sort_values('revenue', ascending=False).head(n)
        
        return top.to_dict(orient='records')
    
    def get_top_customers(self, n: int = 10) -> List[Dict[str, Any]]:
        """Get top customers by spend"""
        if 'customer_id' not in self.df.columns:
            return []
        
        top = self.df.groupby('customer_id').agg({
            'transaction_amount': 'sum',
            'transaction_id': 'nunique',
            'quantity': 'sum'
        }).reset_index()
        top.columns = ['customer_id', 'total_spend', 'transactions', 'items_purchased']
        top = top.sort_values('total_spend', ascending=False).head(n)
        top['customer_id'] = top['customer_id'].astype(int)
        
        return top.to_dict(orient='records')
    
    def generate_insights(self) -> List[Dict[str, Any]]:
        """Generate automated insights from the data"""
        insights = []
        
        # Revenue insights
        total_revenue = self.df['transaction_amount'].sum()
        avg_transaction = self.df['transaction_amount'].mean()
        insights.append({
            'type': 'revenue',
            'title': 'Total Revenue',
            'value': f"${total_revenue:,.2f}",
            'description': f"Average transaction value: ${avg_transaction:.2f}"
        })
        
        # Customer insights
        if 'customer_id' in self.df.columns:
            unique_customers = self.df['customer_id'].nunique()
            insights.append({
                'type': 'customers',
                'title': 'Unique Customers',
                'value': f"{unique_customers:,}",
                'description': f"Avg revenue per customer: ${total_revenue/unique_customers:,.2f}"
            })
        
        # Top country insight
        if 'country' in self.df.columns:
            top_country = self.df.groupby('country')['transaction_amount'].sum().idxmax()
            top_country_revenue = self.df.groupby('country')['transaction_amount'].sum().max()
            insights.append({
                'type': 'geography',
                'title': 'Top Market',
                'value': top_country,
                'description': f"Revenue: ${top_country_revenue:,.2f}"
            })
        
        self.insights = insights
        return insights
    
    def get_full_eda_report(self) -> Dict[str, Any]:
        """Generate comprehensive EDA report"""
        return {
            'basic_statistics': self.get_basic_statistics(),
            'distribution_analysis': self.get_distribution_analysis(),
            'temporal_analysis': self.get_temporal_analysis(),
            'categorical_analysis': self.get_categorical_analysis(),
            'correlation_analysis': self.get_correlation_analysis(),
            'top_products': self.get_top_products(10),
            'top_customers': self.get_top_customers(10),
            'insights': self.generate_insights(),
            'data_shape': self.df.shape
        }
