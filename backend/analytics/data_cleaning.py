"""
Data Cleaning Module
Handles data preprocessing and cleaning operations
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class DataCleaning:
    """Handles data cleaning and preprocessing"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.cleaning_log: List[Dict[str, Any]] = []
        self.original_shape = df.shape
        
    def _log_operation(self, operation: str, details: Dict[str, Any]):
        """Log cleaning operations"""
        self.cleaning_log.append({
            'operation': operation,
            'details': details,
            'records_after': len(self.df)
        })
        logger.info(f"{operation}: {details}")
    
    def remove_duplicates(self) -> 'DataCleaning':
        """Remove duplicate rows"""
        before = len(self.df)
        self.df = self.df.drop_duplicates()
        removed = before - len(self.df)
        self._log_operation('remove_duplicates', {'removed': removed})
        return self
    
    def handle_missing_values(self, strategy: str = 'drop_customers') -> 'DataCleaning':
        """Handle missing values in the dataset"""
        before = len(self.df)
        
        if strategy == 'drop_customers':
            # Drop rows with missing customer_id (can't do customer analysis without it)
            self.df = self.df.dropna(subset=['customer_id'])
            
        elif strategy == 'fill_median':
            # Fill numeric nulls with median
            numeric_cols = self.df.select_dtypes(include=['float64', 'int64']).columns
            for col in numeric_cols:
                if self.df[col].isnull().any():
                    self.df[col] = self.df[col].fillna(self.df[col].median())
        
        # Fill description nulls with 'Unknown'
        if 'transaction_item_description' in self.df.columns:
            self.df['transaction_item_description'] = self.df['transaction_item_description'].fillna('Unknown')
        
        removed = before - len(self.df)
        self._log_operation('handle_missing_values', {'strategy': strategy, 'removed': removed})
        return self
    
    def remove_cancelled_transactions(self) -> 'DataCleaning':
        """Remove cancelled transactions (negative quantities)"""
        before = len(self.df)
        self.df = self.df[self.df['quantity'] > 0]
        removed = before - len(self.df)
        self._log_operation('remove_cancelled_transactions', {'removed': removed})
        return self
    
    def remove_outliers(self, column: str, method: str = 'iqr', threshold: float = 1.5) -> 'DataCleaning':
        """Remove outliers using IQR or Z-score method"""
        before = len(self.df)
        
        if method == 'iqr':
            Q1 = self.df[column].quantile(0.25)
            Q3 = self.df[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            self.df = self.df[(self.df[column] >= lower_bound) & (self.df[column] <= upper_bound)]
            
        elif method == 'zscore':
            mean = self.df[column].mean()
            std = self.df[column].std()
            self.df = self.df[np.abs((self.df[column] - mean) / std) < threshold]
        
        removed = before - len(self.df)
        self._log_operation('remove_outliers', {
            'column': column, 
            'method': method, 
            'threshold': threshold,
            'removed': removed
        })
        return self
    
    def standardize_data_types(self) -> 'DataCleaning':
        """Standardize data types for consistency"""
        type_changes = {}
        
        # Ensure customer_id is integer
        if 'customer_id' in self.df.columns:
            self.df['customer_id'] = self.df['customer_id'].astype(int)
            type_changes['customer_id'] = 'int'
        
        # Ensure transaction_date is datetime
        if 'transaction_date' in self.df.columns:
            self.df['transaction_date'] = pd.to_datetime(self.df['transaction_date'])
            type_changes['transaction_date'] = 'datetime'
        
        # Ensure quantity is integer
        if 'quantity' in self.df.columns:
            self.df['quantity'] = self.df['quantity'].astype(int)
            type_changes['quantity'] = 'int'
        
        # Ensure numeric columns are float
        for col in ['price', 'transaction_amount']:
            if col in self.df.columns:
                self.df[col] = self.df[col].astype(float)
                type_changes[col] = 'float'
        
        self._log_operation('standardize_data_types', type_changes)
        return self
    
    def filter_by_date_range(self, start_date: str = None, end_date: str = None) -> 'DataCleaning':
        """Filter data by date range"""
        before = len(self.df)
        
        if start_date:
            self.df = self.df[self.df['transaction_date'] >= pd.to_datetime(start_date)]
        if end_date:
            self.df = self.df[self.df['transaction_date'] <= pd.to_datetime(end_date)]
        
        removed = before - len(self.df)
        self._log_operation('filter_by_date_range', {
            'start_date': start_date,
            'end_date': end_date,
            'removed': removed
        })
        return self
    
    def clean_text_columns(self) -> 'DataCleaning':
        """Clean and standardize text columns"""
        text_cols = ['transaction_item_description', 'product_type', 'country']
        
        for col in text_cols:
            if col in self.df.columns:
                # Strip whitespace
                self.df[col] = self.df[col].astype(str).str.strip()
                # Standardize case for country
                if col == 'country':
                    self.df[col] = self.df[col].str.title()
        
        self._log_operation('clean_text_columns', {'columns': text_cols})
        return self
    
    def get_cleaned_data(self) -> pd.DataFrame:
        """Return the cleaned dataframe"""
        return self.df
    
    def get_cleaning_report(self) -> Dict[str, Any]:
        """Get comprehensive cleaning report"""
        return {
            'original_shape': self.original_shape,
            'final_shape': self.df.shape,
            'records_removed': self.original_shape[0] - len(self.df),
            'removal_percentage': round((1 - len(self.df) / self.original_shape[0]) * 100, 2),
            'operations': self.cleaning_log
        }
    
    def run_full_cleaning_pipeline(self) -> pd.DataFrame:
        """Run complete cleaning pipeline"""
        logger.info("Starting full cleaning pipeline...")
        
        self.remove_duplicates() \
            .handle_missing_values() \
            .remove_cancelled_transactions() \
            .standardize_data_types() \
            .clean_text_columns() \
            .remove_outliers('quantity', method='iqr', threshold=3) \
            .remove_outliers('transaction_amount', method='iqr', threshold=3)
        
        logger.info(f"Cleaning complete. Final shape: {self.df.shape}")
        return self.df
