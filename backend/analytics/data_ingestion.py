"""
Data Ingestion Module
Handles loading and initial validation of retail transaction data
"""
import pandas as pd
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class DataIngestion:
    """Handles data loading and initial validation"""
    
    REQUIRED_COLUMNS = [
        'transaction_id', 'transaction_item_code', 'transaction_item_description',
        'product_type', 'quantity', 'transaction_date', 'price',
        'customer_id', 'country', 'transaction_amount'
    ]
    
    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        self.df: Optional[pd.DataFrame] = None
        self.validation_report: Dict[str, Any] = {}
        
    def load_data(self) -> pd.DataFrame:
        """Load data from Excel or CSV file"""
        logger.info(f"Loading data from {self.data_path}")
        
        if self.data_path.suffix.lower() in ['.xlsx', '.xls']:
            self.df = pd.read_excel(self.data_path)
        elif self.data_path.suffix.lower() == '.csv':
            self.df = pd.read_csv(self.data_path)
        else:
            raise ValueError(f"Unsupported file format: {self.data_path.suffix}")
        
        logger.info(f"Loaded {len(self.df)} records with {len(self.df.columns)} columns")
        return self.df
    
    def validate_schema(self) -> Dict[str, Any]:
        """Validate data schema and report issues"""
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        validation = {
            'total_records': len(self.df),
            'total_columns': len(self.df.columns),
            'columns_found': self.df.columns.tolist(),
            'missing_required_columns': [],
            'column_types': {},
            'is_valid': True
        }
        
        # Check required columns
        for col in self.REQUIRED_COLUMNS:
            if col not in self.df.columns:
                validation['missing_required_columns'].append(col)
                validation['is_valid'] = False
        
        # Record column types
        validation['column_types'] = self.df.dtypes.astype(str).to_dict()
        
        self.validation_report = validation
        logger.info(f"Schema validation: {'PASSED' if validation['is_valid'] else 'FAILED'}")
        return validation
    
    def get_data_quality_report(self) -> Dict[str, Any]:
        """Generate comprehensive data quality report"""
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        report = {
            'null_counts': self.df.isnull().sum().to_dict(),
            'null_percentages': (self.df.isnull().sum() / len(self.df) * 100).round(2).to_dict(),
            'duplicate_rows': int(self.df.duplicated().sum()),
            'unique_counts': {},
            'numeric_stats': {},
            'date_range': {},
            'memory_usage_mb': round(self.df.memory_usage(deep=True).sum() / (1024 * 1024), 2)
        }
        
        # Unique counts for categorical columns
        for col in self.df.select_dtypes(include=['object', 'category']).columns:
            report['unique_counts'][col] = int(self.df[col].nunique())
        
        # Statistics for numeric columns
        numeric_cols = self.df.select_dtypes(include=['int64', 'float64']).columns
        for col in numeric_cols:
            report['numeric_stats'][col] = {
                'min': float(self.df[col].min()) if pd.notna(self.df[col].min()) else None,
                'max': float(self.df[col].max()) if pd.notna(self.df[col].max()) else None,
                'mean': float(self.df[col].mean()) if pd.notna(self.df[col].mean()) else None,
                'median': float(self.df[col].median()) if pd.notna(self.df[col].median()) else None,
                'std': float(self.df[col].std()) if pd.notna(self.df[col].std()) else None
            }
        
        # Date range
        date_cols = self.df.select_dtypes(include=['datetime64']).columns
        for col in date_cols:
            report['date_range'][col] = {
                'min': self.df[col].min().isoformat() if pd.notna(self.df[col].min()) else None,
                'max': self.df[col].max().isoformat() if pd.notna(self.df[col].max()) else None
            }
        
        return report
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a concise summary of the loaded data"""
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        return {
            'file_name': self.data_path.name,
            'total_records': len(self.df),
            'total_columns': len(self.df.columns),
            'date_loaded': datetime.now().isoformat(),
            'validation_status': self.validation_report.get('is_valid', None)
        }
