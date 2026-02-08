"""
Customer Segmentation Module
Performs K-Means clustering for customer segmentation
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Optional
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

logger = logging.getLogger(__name__)


class CustomerSegmentation:
    """Performs K-Means customer segmentation"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.customer_data: pd.DataFrame = None
        self.scaled_data: np.ndarray = None
        self.scaler: StandardScaler = None
        self.kmeans_model: KMeans = None
        self.optimal_k: int = None
        self.labels: np.ndarray = None
        
    def prepare_customer_data(self) -> pd.DataFrame:
        """Prepare customer-level data for clustering"""
        if 'customer_id' not in self.df.columns:
            raise ValueError("customer_id column required for segmentation")
        
        # Aggregate customer metrics
        customer_data = self.df.groupby('customer_id').agg({
            'transaction_id': 'nunique',
            'transaction_amount': ['sum', 'mean', 'std'],
            'quantity': ['sum', 'mean'],
            'transaction_date': ['min', 'max']
        }).reset_index()
        
        customer_data.columns = ['customer_id', 'total_transactions', 
                                'total_spend', 'avg_transaction', 'std_transaction',
                                'total_items', 'avg_items',
                                'first_purchase', 'last_purchase']
        
        # Fill NaN standard deviation with 0
        customer_data['std_transaction'] = customer_data['std_transaction'].fillna(0)
        
        # Calculate tenure
        customer_data['tenure_days'] = (
            customer_data['last_purchase'] - customer_data['first_purchase']
        ).dt.days
        
        # Calculate recency (days since last purchase)
        max_date = self.df['transaction_date'].max()
        customer_data['recency_days'] = (max_date - customer_data['last_purchase']).dt.days
        
        self.customer_data = customer_data
        logger.info(f"Prepared data for {len(customer_data)} customers")
        
        return customer_data
    
    def scale_features(self, features: List[str] = None) -> np.ndarray:
        """Scale features for clustering"""
        if self.customer_data is None:
            self.prepare_customer_data()
        
        # Default features for clustering
        if features is None:
            features = ['total_transactions', 'total_spend', 'avg_transaction', 
                       'total_items', 'recency_days', 'tenure_days']
        
        # Ensure all features exist
        available_features = [f for f in features if f in self.customer_data.columns]
        
        self.scaler = StandardScaler()
        self.scaled_data = self.scaler.fit_transform(self.customer_data[available_features])
        self.feature_names = available_features
        
        logger.info(f"Scaled {len(available_features)} features")
        
        return self.scaled_data
    
    def find_optimal_k(self, k_range: tuple = (2, 10)) -> Dict[str, Any]:
        """Find optimal number of clusters using elbow method and silhouette score"""
        if self.scaled_data is None:
            self.scale_features()
        
        k_values = range(k_range[0], k_range[1] + 1)
        inertias = []
        silhouette_scores = []
        
        for k in k_values:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(self.scaled_data)
            inertias.append(kmeans.inertia_)
            silhouette_scores.append(silhouette_score(self.scaled_data, kmeans.labels_))
        
        # Find optimal k based on silhouette score
        self.optimal_k = k_values[np.argmax(silhouette_scores)]
        
        elbow_results = {
            'k_values': list(k_values),
            'inertias': [round(i, 2) for i in inertias],
            'silhouette_scores': [round(s, 4) for s in silhouette_scores],
            'optimal_k': self.optimal_k,
            'best_silhouette': round(max(silhouette_scores), 4)
        }
        
        logger.info(f"Optimal K found: {self.optimal_k} (silhouette: {max(silhouette_scores):.4f})")
        
        return elbow_results
    
    def perform_clustering(self, n_clusters: int = None) -> pd.DataFrame:
        """Perform K-Means clustering"""
        if self.scaled_data is None:
            self.scale_features()
        
        if n_clusters is None:
            if self.optimal_k is None:
                self.find_optimal_k()
            n_clusters = self.optimal_k
        
        self.kmeans_model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.labels = self.kmeans_model.fit_predict(self.scaled_data)
        
        self.customer_data['cluster'] = self.labels
        
        logger.info(f"Clustering complete with {n_clusters} clusters")
        
        return self.customer_data
    
    def get_cluster_profiles(self) -> List[Dict[str, Any]]:
        """Generate profiles for each cluster"""
        if 'cluster' not in self.customer_data.columns:
            self.perform_clustering()
        
        profiles = []
        
        for cluster_id in sorted(self.customer_data['cluster'].unique()):
            cluster_data = self.customer_data[self.customer_data['cluster'] == cluster_id]
            
            profile = {
                'cluster_id': int(cluster_id),
                'customer_count': len(cluster_data),
                'percentage': round(len(cluster_data) / len(self.customer_data) * 100, 2),
                'avg_transactions': round(cluster_data['total_transactions'].mean(), 2),
                'avg_spend': round(cluster_data['total_spend'].mean(), 2),
                'total_revenue': round(cluster_data['total_spend'].sum(), 2),
                'avg_transaction_value': round(cluster_data['avg_transaction'].mean(), 2),
                'avg_items': round(cluster_data['total_items'].mean(), 2),
                'avg_recency': round(cluster_data['recency_days'].mean(), 2),
                'avg_tenure': round(cluster_data['tenure_days'].mean(), 2)
            }
            
            # Assign cluster label based on characteristics
            profile['label'] = self._assign_cluster_label(profile)
            
            profiles.append(profile)
        
        return sorted(profiles, key=lambda x: x['total_revenue'], reverse=True)
    
    def _assign_cluster_label(self, profile: Dict[str, Any]) -> str:
        """Assign descriptive label to cluster based on profile"""
        avg_spend = profile['avg_spend']
        avg_transactions = profile['avg_transactions']
        avg_recency = profile['avg_recency']
        
        # Get overall averages for comparison
        overall_spend = self.customer_data['total_spend'].mean()
        overall_transactions = self.customer_data['total_transactions'].mean()
        overall_recency = self.customer_data['recency_days'].mean()
        
        if avg_spend > overall_spend * 1.5 and avg_transactions > overall_transactions * 1.5:
            return 'VIP Customers'
        elif avg_spend > overall_spend and avg_recency < overall_recency:
            return 'High-Value Active'
        elif avg_transactions > overall_transactions and avg_recency < overall_recency:
            return 'Frequent Buyers'
        elif avg_recency > overall_recency * 1.5:
            return 'Churning'
        elif avg_spend < overall_spend * 0.5:
            return 'Low-Value'
        else:
            return 'Regular'
    
    def get_cluster_distribution(self) -> Dict[str, Any]:
        """Get cluster size distribution"""
        if 'cluster' not in self.customer_data.columns:
            self.perform_clustering()
        
        distribution = self.customer_data['cluster'].value_counts().sort_index()
        
        return {
            'cluster_sizes': distribution.to_dict(),
            'total_customers': len(self.customer_data),
            'n_clusters': len(distribution)
        }
    
    def get_cluster_centroids(self) -> List[Dict[str, Any]]:
        """Get cluster centroids in original scale"""
        if self.kmeans_model is None:
            self.perform_clustering()
        
        # Inverse transform centroids
        centroids = self.scaler.inverse_transform(self.kmeans_model.cluster_centers_)
        
        centroid_list = []
        for i, centroid in enumerate(centroids):
            centroid_dict = {'cluster_id': i}
            for j, feature in enumerate(self.feature_names):
                centroid_dict[feature] = round(centroid[j], 2)
            centroid_list.append(centroid_dict)
        
        return centroid_list
    
    def get_segmented_customers(self) -> pd.DataFrame:
        """Return customer data with cluster assignments"""
        if 'cluster' not in self.customer_data.columns:
            self.perform_clustering()
        return self.customer_data
    
    def get_segmentation_report(self) -> Dict[str, Any]:
        """Generate comprehensive segmentation report"""
        if 'cluster' not in self.customer_data.columns:
            self.perform_clustering()
        
        return {
            'n_clusters': len(self.customer_data['cluster'].unique()),
            'total_customers': len(self.customer_data),
            'cluster_profiles': self.get_cluster_profiles(),
            'cluster_distribution': self.get_cluster_distribution(),
            'cluster_centroids': self.get_cluster_centroids(),
            'silhouette_score': round(silhouette_score(self.scaled_data, self.labels), 4) if self.labels is not None else None,
            'features_used': self.feature_names if hasattr(self, 'feature_names') else []
        }
