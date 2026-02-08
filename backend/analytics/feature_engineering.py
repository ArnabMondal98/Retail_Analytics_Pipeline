"""
Feature Engineering Module
Creates derived features for analysis
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class FeatureEngineering:
    """Creates derived features for retail analytics"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.features_created: List[str] = []
        
    def _log_feature(self, feature_name: str):
        """Log created feature"""
        self.features_created.append(feature_name)
        logger.info(f"Created feature: {feature_name}")
    
    def create_time_features(self) -> 'FeatureEngineering':
        """Extract time-based features from transaction date"""
        if 'transaction_date' not in self.df.columns:
            logger.warning("transaction_date column not found")
            return self
        
        self.df['year'] = self.df['transaction_date'].dt.year
        self.df['month'] = self.df['transaction_date'].dt.month
        self.df['quarter'] = self.df['transaction_date'].dt.quarter
        self.df['day_of_week'] = self.df['transaction_date'].dt.dayofweek
        self.df['day_of_month'] = self.df['transaction_date'].dt.day
        self.df['week_of_year'] = self.df['transaction_date'].dt.isocalendar().week.astype(int)
        self.df['is_weekend'] = self.df['day_of_week'].isin([5, 6]).astype(int)
        self.df['year_month'] = self.df['transaction_date'].dt.to_period('M').astype(str)
        
        for feature in ['year', 'month', 'quarter', 'day_of_week', 'day_of_month', 
                       'week_of_year', 'is_weekend', 'year_month']:
            self._log_feature(feature)
        
        return self
    
    def create_transaction_features(self) -> 'FeatureEngineering':
        """Create transaction-level features"""
        # Unit price validation
        if 'price' in self.df.columns and 'quantity' in self.df.columns:
            self.df['calculated_amount'] = self.df['price'] * self.df['quantity']
            self._log_feature('calculated_amount')
        
        # Transaction size category
        if 'transaction_amount' in self.df.columns:
            self.df['transaction_size'] = pd.cut(
                self.df['transaction_amount'],
                bins=[-np.inf, 10, 50, 100, 500, np.inf],
                labels=['Micro', 'Small', 'Medium', 'Large', 'Enterprise']
            )
            self._log_feature('transaction_size')
        
        # Quantity tier
        if 'quantity' in self.df.columns:
            self.df['quantity_tier'] = pd.cut(
                self.df['quantity'],
                bins=[-np.inf, 1, 5, 10, 50, np.inf],
                labels=['Single', 'Few', 'Moderate', 'Bulk', 'Wholesale']
            )
            self._log_feature('quantity_tier')
        
        return self
    
    def create_customer_features(self) -> 'FeatureEngineering':
        """Create customer-level aggregated features"""
        if 'customer_id' not in self.df.columns:
            logger.warning("customer_id column not found")
            return self
        
        # Customer aggregations
        customer_stats = self.df.groupby('customer_id').agg({
            'transaction_id': 'nunique',
            'transaction_amount': ['sum', 'mean', 'std', 'min', 'max'],
            'quantity': ['sum', 'mean'],
            'transaction_date': ['min', 'max', 'count']
        }).reset_index()
        
        # Flatten column names
        customer_stats.columns = ['customer_id', 'total_transactions', 
                                  'total_spend', 'avg_transaction_value', 
                                  'std_transaction_value', 'min_transaction',
                                  'max_transaction', 'total_items', 'avg_items',
                                  'first_purchase', 'last_purchase', 'purchase_count']
        
        # Calculate customer tenure (days)
        customer_stats['customer_tenure_days'] = (
            customer_stats['last_purchase'] - customer_stats['first_purchase']
        ).dt.days
        
        # Purchase frequency (avg days between purchases)
        customer_stats['avg_days_between_purchases'] = (
            customer_stats['customer_tenure_days'] / 
            (customer_stats['total_transactions'] - 1).replace(0, np.nan)
        ).fillna(0)
        
        # Store customer features for later use
        self.customer_features = customer_stats
        self._log_feature('customer_aggregations')
        
        return self
    
    def create_product_features(self) -> 'FeatureEngineering':
        """Create product-level aggregated features"""
        if 'transaction_item_code' not in self.df.columns:
            logger.warning("transaction_item_code column not found")
            return self
        
        # Product aggregations
        product_stats = self.df.groupby('transaction_item_code').agg({
            'transaction_id': 'nunique',
            'transaction_amount': ['sum', 'mean'],
            'quantity': ['sum', 'mean'],
            'customer_id': 'nunique'
        }).reset_index()
        
        product_stats.columns = ['product_code', 'times_purchased', 
                                'total_revenue', 'avg_revenue',
                                'total_quantity_sold', 'avg_quantity',
                                'unique_customers']
        
        self.product_features = product_stats
        self._log_feature('product_aggregations')
        
        return self
    
    def create_country_features(self) -> 'FeatureEngineering':
        """Create country-level aggregated features"""
        if 'country' not in self.df.columns:
            logger.warning("country column not found")
            return self
        
        country_stats = self.df.groupby('country').agg({
            'transaction_id': 'nunique',
            'transaction_amount': ['sum', 'mean'],
            'customer_id': 'nunique',
            'quantity': 'sum'
        }).reset_index()
        
        country_stats.columns = ['country', 'total_transactions',
                                'total_revenue', 'avg_transaction_value',
                                'unique_customers', 'total_quantity']
        
        self.country_features = country_stats
        self._log_feature('country_aggregations')
        
        return self
    
    def get_featured_data(self) -> pd.DataFrame:
        """Return dataframe with all features"""
        return self.df
    
    def get_customer_features(self) -> pd.DataFrame:
        """Return customer-level features"""
        if hasattr(self, 'customer_features'):
            return self.customer_features
        return pd.DataFrame()
    
    def get_product_features(self) -> pd.DataFrame:
        """Return product-level features"""
        if hasattr(self, 'product_features'):
            return self.product_features
        return pd.DataFrame()
    
    def get_country_features(self) -> pd.DataFrame:
        """Return country-level features"""
        if hasattr(self, 'country_features'):
            return self.country_features
        return pd.DataFrame()
    
    def get_feature_report(self) -> Dict[str, Any]:
        """Get feature engineering report"""
        return {
            'features_created': self.features_created,
            'total_features': len(self.features_created),
            'final_columns': self.df.columns.tolist(),
            'final_shape': self.df.shape
        }
    
    def run_full_feature_pipeline(self) -> pd.DataFrame:
        """Run complete feature engineering pipeline"""
        logger.info("Starting feature engineering pipeline...")
        
        self.create_time_features() \
            .create_transaction_features() \
            .create_customer_features() \
            .create_product_features() \
            .create_country_features()
        
        logger.info(f"Feature engineering complete. Created {len(self.features_created)} feature groups")
        return self.df
