"""
KPI Generator Module
Generates key performance indicators for retail analytics
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class KPIGenerator:
    """Generates retail KPIs"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.kpis: Dict[str, Any] = {}
        
    def calculate_revenue_kpis(self) -> Dict[str, Any]:
        """Calculate revenue-related KPIs"""
        kpis = {}
        
        # Total Revenue
        kpis['total_revenue'] = round(self.df['transaction_amount'].sum(), 2)
        
        # Average Order Value
        kpis['avg_order_value'] = round(self.df['transaction_amount'].mean(), 2)
        
        # Median Order Value
        kpis['median_order_value'] = round(self.df['transaction_amount'].median(), 2)
        
        # Revenue per Transaction
        total_transactions = self.df['transaction_id'].nunique()
        kpis['revenue_per_transaction'] = round(kpis['total_revenue'] / total_transactions, 2)
        
        # Total Transactions
        kpis['total_transactions'] = total_transactions
        
        # Total Items Sold
        kpis['total_items_sold'] = int(self.df['quantity'].sum())
        
        # Average Items per Transaction
        kpis['avg_items_per_transaction'] = round(self.df['quantity'].mean(), 2)
        
        self.kpis['revenue'] = kpis
        return kpis
    
    def calculate_customer_kpis(self) -> Dict[str, Any]:
        """Calculate customer-related KPIs"""
        kpis = {}
        
        if 'customer_id' not in self.df.columns:
            return kpis
        
        # Unique Customers
        kpis['unique_customers'] = self.df['customer_id'].nunique()
        
        # Revenue per Customer
        kpis['revenue_per_customer'] = round(
            self.df['transaction_amount'].sum() / kpis['unique_customers'], 2
        )
        
        # Average Orders per Customer
        orders_per_customer = self.df.groupby('customer_id')['transaction_id'].nunique()
        kpis['avg_orders_per_customer'] = round(orders_per_customer.mean(), 2)
        
        # Customer with most orders
        kpis['max_orders_single_customer'] = int(orders_per_customer.max())
        
        # Single vs Repeat customers
        repeat_customers = (orders_per_customer > 1).sum()
        kpis['repeat_customer_count'] = int(repeat_customers)
        kpis['single_purchase_customers'] = int(kpis['unique_customers'] - repeat_customers)
        kpis['repeat_customer_rate'] = round(repeat_customers / kpis['unique_customers'] * 100, 2)
        
        self.kpis['customer'] = kpis
        return kpis
    
    def calculate_product_kpis(self) -> Dict[str, Any]:
        """Calculate product-related KPIs"""
        kpis = {}
        
        if 'transaction_item_code' in self.df.columns:
            kpis['unique_products'] = self.df['transaction_item_code'].nunique()
            
            # Average revenue per product
            product_revenue = self.df.groupby('transaction_item_code')['transaction_amount'].sum()
            kpis['avg_revenue_per_product'] = round(product_revenue.mean(), 2)
            kpis['max_product_revenue'] = round(product_revenue.max(), 2)
            
            # Top product
            top_product = self.df.groupby('transaction_item_code')['transaction_amount'].sum().idxmax()
            kpis['top_product'] = str(top_product)
        
        if 'product_type' in self.df.columns:
            kpis['unique_product_types'] = self.df['product_type'].nunique()
            
            # Top category
            top_category = self.df.groupby('product_type')['transaction_amount'].sum().idxmax()
            kpis['top_category'] = str(top_category)
        
        self.kpis['product'] = kpis
        return kpis
    
    def calculate_geographic_kpis(self) -> Dict[str, Any]:
        """Calculate geographic KPIs"""
        kpis = {}
        
        if 'country' not in self.df.columns:
            return kpis
        
        kpis['unique_countries'] = self.df['country'].nunique()
        
        # Top country by revenue
        country_revenue = self.df.groupby('country')['transaction_amount'].sum()
        kpis['top_country'] = str(country_revenue.idxmax())
        kpis['top_country_revenue'] = round(country_revenue.max(), 2)
        kpis['top_country_share'] = round(
            country_revenue.max() / country_revenue.sum() * 100, 2
        )
        
        # Country diversity (how spread out is revenue)
        kpis['country_hhi'] = round(
            ((country_revenue / country_revenue.sum()) ** 2).sum() * 10000, 2
        )  # Herfindahl-Hirschman Index
        
        self.kpis['geographic'] = kpis
        return kpis
    
    def calculate_time_kpis(self) -> Dict[str, Any]:
        """Calculate time-based KPIs"""
        kpis = {}
        
        if 'transaction_date' not in self.df.columns:
            return kpis
        
        # Date range
        kpis['start_date'] = self.df['transaction_date'].min().strftime('%Y-%m-%d')
        kpis['end_date'] = self.df['transaction_date'].max().strftime('%Y-%m-%d')
        kpis['data_span_days'] = (
            self.df['transaction_date'].max() - self.df['transaction_date'].min()
        ).days
        
        # Monthly average
        monthly = self.df.groupby(self.df['transaction_date'].dt.to_period('M'))['transaction_amount'].sum()
        kpis['avg_monthly_revenue'] = round(monthly.mean(), 2)
        kpis['best_month'] = str(monthly.idxmax())
        kpis['best_month_revenue'] = round(monthly.max(), 2)
        
        # Daily average
        daily = self.df.groupby(self.df['transaction_date'].dt.date)['transaction_amount'].sum()
        kpis['avg_daily_revenue'] = round(daily.mean(), 2)
        kpis['best_day_revenue'] = round(daily.max(), 2)
        
        # Transactions per day
        daily_transactions = self.df.groupby(self.df['transaction_date'].dt.date)['transaction_id'].nunique()
        kpis['avg_daily_transactions'] = round(daily_transactions.mean(), 2)
        
        self.kpis['time'] = kpis
        return kpis
    
    def calculate_growth_kpis(self) -> Dict[str, Any]:
        """Calculate growth metrics"""
        kpis = {}
        
        if 'transaction_date' not in self.df.columns:
            return kpis
        
        # Monthly revenue for growth calculation
        monthly = self.df.groupby(self.df['transaction_date'].dt.to_period('M'))['transaction_amount'].sum()
        
        if len(monthly) >= 2:
            # Month over month growth (last 2 months)
            last_month = monthly.iloc[-1]
            prev_month = monthly.iloc[-2]
            kpis['mom_growth'] = round((last_month - prev_month) / prev_month * 100, 2) if prev_month > 0 else 0
            
            # Average monthly growth rate
            if len(monthly) > 2:
                growth_rates = monthly.pct_change().dropna()
                kpis['avg_monthly_growth'] = round(growth_rates.mean() * 100, 2)
            
        if len(monthly) >= 12:
            # Year over year (compare last 12 months to previous 12)
            last_12 = monthly.iloc[-12:].sum()
            prev_12 = monthly.iloc[-24:-12].sum() if len(monthly) >= 24 else monthly.iloc[:-12].sum()
            kpis['yoy_growth'] = round((last_12 - prev_12) / prev_12 * 100, 2) if prev_12 > 0 else 0
        
        self.kpis['growth'] = kpis
        return kpis
    
    def get_all_kpis(self) -> Dict[str, Any]:
        """Calculate and return all KPIs"""
        self.calculate_revenue_kpis()
        self.calculate_customer_kpis()
        self.calculate_product_kpis()
        self.calculate_geographic_kpis()
        self.calculate_time_kpis()
        self.calculate_growth_kpis()
        
        return self.kpis
    
    def get_kpi_summary(self) -> List[Dict[str, Any]]:
        """Get formatted KPI summary for dashboard"""
        if not self.kpis:
            self.get_all_kpis()
        
        summary = []
        
        # Revenue KPIs
        if 'revenue' in self.kpis:
            summary.append({
                'category': 'Revenue',
                'name': 'Total Revenue',
                'value': f"${self.kpis['revenue']['total_revenue']:,.2f}",
                'raw_value': self.kpis['revenue']['total_revenue']
            })
            summary.append({
                'category': 'Revenue',
                'name': 'Average Order Value',
                'value': f"${self.kpis['revenue']['avg_order_value']:,.2f}",
                'raw_value': self.kpis['revenue']['avg_order_value']
            })
            summary.append({
                'category': 'Revenue',
                'name': 'Total Transactions',
                'value': f"{self.kpis['revenue']['total_transactions']:,}",
                'raw_value': self.kpis['revenue']['total_transactions']
            })
        
        # Customer KPIs
        if 'customer' in self.kpis:
            summary.append({
                'category': 'Customer',
                'name': 'Unique Customers',
                'value': f"{self.kpis['customer']['unique_customers']:,}",
                'raw_value': self.kpis['customer']['unique_customers']
            })
            summary.append({
                'category': 'Customer',
                'name': 'Repeat Customer Rate',
                'value': f"{self.kpis['customer']['repeat_customer_rate']}%",
                'raw_value': self.kpis['customer']['repeat_customer_rate']
            })
        
        # Growth KPIs
        if 'growth' in self.kpis and 'mom_growth' in self.kpis['growth']:
            summary.append({
                'category': 'Growth',
                'name': 'Month over Month',
                'value': f"{self.kpis['growth']['mom_growth']:+.1f}%",
                'raw_value': self.kpis['growth']['mom_growth']
            })
        
        return summary
    
    def get_kpi_report(self) -> Dict[str, Any]:
        """Generate comprehensive KPI report"""
        if not self.kpis:
            self.get_all_kpis()
        
        return {
            'generated_at': datetime.now().isoformat(),
            'kpis': self.kpis,
            'summary': self.get_kpi_summary()
        }
