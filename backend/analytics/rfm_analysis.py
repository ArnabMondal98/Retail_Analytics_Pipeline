"""
RFM Analysis Module
Performs Recency, Frequency, Monetary analysis for customer segmentation
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RFMAnalysis:
    """Performs RFM (Recency, Frequency, Monetary) analysis"""
    
    def __init__(self, df: pd.DataFrame, reference_date: datetime = None):
        self.df = df.copy()
        self.reference_date = reference_date or datetime.now()
        self.rfm_table: pd.DataFrame = None
        self.rfm_segments: pd.DataFrame = None
        
    def calculate_rfm_metrics(self) -> pd.DataFrame:
        """Calculate RFM metrics for each customer"""
        if 'customer_id' not in self.df.columns:
            raise ValueError("customer_id column required for RFM analysis")
        
        if 'transaction_date' not in self.df.columns:
            raise ValueError("transaction_date column required for RFM analysis")
        
        # Ensure transaction_date is datetime
        self.df['transaction_date'] = pd.to_datetime(self.df['transaction_date'])
        
        # Use max date in dataset as reference if not provided
        if self.reference_date is None or self.reference_date < self.df['transaction_date'].max():
            self.reference_date = self.df['transaction_date'].max() + timedelta(days=1)
        
        # Calculate RFM metrics
        rfm = self.df.groupby('customer_id').agg({
            'transaction_date': lambda x: (self.reference_date - x.max()).days,  # Recency
            'transaction_id': 'nunique',  # Frequency
            'transaction_amount': 'sum'   # Monetary
        }).reset_index()
        
        rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']
        
        # Ensure all values are numeric
        rfm['recency'] = rfm['recency'].astype(int)
        rfm['frequency'] = rfm['frequency'].astype(int)
        rfm['monetary'] = rfm['monetary'].astype(float).round(2)
        
        self.rfm_table = rfm
        logger.info(f"RFM metrics calculated for {len(rfm)} customers")
        
        return rfm
    
    def assign_rfm_scores(self, n_quantiles: int = 5) -> pd.DataFrame:
        """Assign RFM scores based on quantiles"""
        if self.rfm_table is None:
            self.calculate_rfm_metrics()
        
        rfm = self.rfm_table.copy()
        
        # Recency score (lower is better, so we reverse)
        rfm['r_score'] = pd.qcut(rfm['recency'], q=n_quantiles, labels=range(n_quantiles, 0, -1), duplicates='drop')
        
        # Frequency score (higher is better)
        rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), q=n_quantiles, labels=range(1, n_quantiles + 1), duplicates='drop')
        
        # Monetary score (higher is better)
        rfm['m_score'] = pd.qcut(rfm['monetary'].rank(method='first'), q=n_quantiles, labels=range(1, n_quantiles + 1), duplicates='drop')
        
        # Convert to int
        for col in ['r_score', 'f_score', 'm_score']:
            rfm[col] = rfm[col].astype(int)
        
        # Combined RFM score
        rfm['rfm_score'] = rfm['r_score'].astype(str) + rfm['f_score'].astype(str) + rfm['m_score'].astype(str)
        rfm['rfm_total'] = rfm['r_score'] + rfm['f_score'] + rfm['m_score']
        
        self.rfm_segments = rfm
        logger.info("RFM scores assigned")
        
        return rfm
    
    def assign_customer_segments(self) -> pd.DataFrame:
        """Assign customer segments based on RFM scores"""
        if self.rfm_segments is None:
            self.assign_rfm_scores()
        
        rfm = self.rfm_segments.copy()
        
        # Define segment rules
        def segment_customer(row):
            r, f, m = row['r_score'], row['f_score'], row['m_score']
            
            # Champions - Best customers
            if r >= 4 and f >= 4 and m >= 4:
                return 'Champions'
            
            # Loyal Customers - Buy often
            if f >= 4 and m >= 3:
                return 'Loyal Customers'
            
            # Potential Loyalists - Recent with average frequency
            if r >= 4 and f >= 2 and f < 4:
                return 'Potential Loyalists'
            
            # Recent Customers - Recent but low frequency
            if r >= 4 and f < 2:
                return 'Recent Customers'
            
            # Promising - Recent with low monetary
            if r >= 3 and m < 3:
                return 'Promising'
            
            # Need Attention - Above average but not recent
            if r >= 2 and r < 4 and f >= 2 and m >= 2:
                return 'Need Attention'
            
            # About to Sleep - Below average in all
            if r >= 2 and r < 3 and f < 3:
                return 'About to Sleep'
            
            # At Risk - Used to be good, haven't visited recently
            if r < 3 and f >= 3 and m >= 3:
                return 'At Risk'
            
            # Can't Lose Them - Big spenders who haven't come back
            if r < 2 and f >= 4 and m >= 4:
                return "Can't Lose Them"
            
            # Hibernating - Low scores across the board
            if r < 2 and f < 2:
                return 'Hibernating'
            
            # Lost - Very low engagement
            return 'Lost'
        
        rfm['segment'] = rfm.apply(segment_customer, axis=1)
        
        self.rfm_segments = rfm
        logger.info("Customer segments assigned")
        
        return rfm
    
    def get_segment_summary(self) -> List[Dict[str, Any]]:
        """Get summary statistics for each segment"""
        if self.rfm_segments is None:
            self.assign_customer_segments()
        
        summary = self.rfm_segments.groupby('segment').agg({
            'customer_id': 'count',
            'recency': 'mean',
            'frequency': 'mean',
            'monetary': ['mean', 'sum']
        }).reset_index()
        
        summary.columns = ['segment', 'customer_count', 'avg_recency', 
                          'avg_frequency', 'avg_monetary', 'total_monetary']
        
        # Calculate percentages
        total_customers = summary['customer_count'].sum()
        total_revenue = summary['total_monetary'].sum()
        
        summary['customer_pct'] = (summary['customer_count'] / total_customers * 100).round(2)
        summary['revenue_pct'] = (summary['total_monetary'] / total_revenue * 100).round(2)
        
        # Round numeric columns
        for col in ['avg_recency', 'avg_frequency', 'avg_monetary', 'total_monetary']:
            summary[col] = summary[col].round(2)
        
        return summary.sort_values('total_monetary', ascending=False).to_dict(orient='records')
    
    def get_rfm_distribution(self) -> Dict[str, Any]:
        """Get distribution of RFM scores"""
        if self.rfm_segments is None:
            self.assign_customer_segments()
        
        return {
            'r_score_distribution': self.rfm_segments['r_score'].value_counts().sort_index().to_dict(),
            'f_score_distribution': self.rfm_segments['f_score'].value_counts().sort_index().to_dict(),
            'm_score_distribution': self.rfm_segments['m_score'].value_counts().sort_index().to_dict(),
            'segment_distribution': self.rfm_segments['segment'].value_counts().to_dict()
        }
    
    def get_rfm_matrix(self) -> List[Dict[str, Any]]:
        """Get RFM matrix for heatmap visualization"""
        if self.rfm_segments is None:
            self.assign_customer_segments()
        
        # Create RF matrix (Recency vs Frequency)
        matrix = self.rfm_segments.groupby(['r_score', 'f_score']).agg({
            'customer_id': 'count',
            'monetary': 'sum'
        }).reset_index()
        matrix.columns = ['recency', 'frequency', 'count', 'revenue']
        
        return matrix.to_dict(orient='records')
    
    def get_rfm_data(self) -> pd.DataFrame:
        """Return complete RFM data"""
        if self.rfm_segments is None:
            self.assign_customer_segments()
        return self.rfm_segments
    
    def get_rfm_report(self) -> Dict[str, Any]:
        """Generate comprehensive RFM report"""
        if self.rfm_segments is None:
            self.assign_customer_segments()
        
        return {
            'total_customers': len(self.rfm_segments),
            'reference_date': self.reference_date.isoformat() if isinstance(self.reference_date, datetime) else str(self.reference_date),
            'segment_summary': self.get_segment_summary(),
            'rfm_distribution': self.get_rfm_distribution(),
            'rfm_matrix': self.get_rfm_matrix(),
            'metrics_summary': {
                'avg_recency': round(self.rfm_segments['recency'].mean(), 2),
                'avg_frequency': round(self.rfm_segments['frequency'].mean(), 2),
                'avg_monetary': round(self.rfm_segments['monetary'].mean(), 2),
                'total_revenue': round(self.rfm_segments['monetary'].sum(), 2)
            }
        }
