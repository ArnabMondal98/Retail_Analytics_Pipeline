"""
Sales Forecasting Module
Performs time series forecasting for sales predictions
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

logger = logging.getLogger(__name__)


class SalesForecasting:
    """Performs sales forecasting using various methods"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.time_series: pd.DataFrame = None
        self.forecasts: Dict[str, Any] = {}
        
    def prepare_time_series(self, frequency: str = 'M') -> pd.DataFrame:
        """Prepare time series data for forecasting"""
        if 'transaction_date' not in self.df.columns:
            raise ValueError("transaction_date column required for forecasting")
        
        # Aggregate by time period
        if frequency == 'D':
            ts = self.df.groupby(self.df['transaction_date'].dt.date).agg({
                'transaction_amount': 'sum',
                'transaction_id': 'nunique',
                'quantity': 'sum'
            }).reset_index()
        elif frequency == 'W':
            ts = self.df.groupby(self.df['transaction_date'].dt.to_period('W')).agg({
                'transaction_amount': 'sum',
                'transaction_id': 'nunique',
                'quantity': 'sum'
            }).reset_index()
            ts['transaction_date'] = ts['transaction_date'].dt.start_time
        else:  # Monthly
            ts = self.df.groupby(self.df['transaction_date'].dt.to_period('M')).agg({
                'transaction_amount': 'sum',
                'transaction_id': 'nunique',
                'quantity': 'sum'
            }).reset_index()
            ts['transaction_date'] = ts['transaction_date'].dt.start_time
        
        ts.columns = ['date', 'revenue', 'transactions', 'quantity']
        ts = ts.sort_values('date').reset_index(drop=True)
        
        self.time_series = ts
        self.frequency = frequency
        
        logger.info(f"Time series prepared with {len(ts)} periods")
        
        return ts
    
    def moving_average_forecast(self, periods: int = 3, forecast_periods: int = 6) -> Dict[str, Any]:
        """Simple moving average forecast"""
        if self.time_series is None:
            self.prepare_time_series()
        
        ts = self.time_series.copy()
        
        # Calculate moving average
        ts['ma'] = ts['revenue'].rolling(window=periods).mean()
        
        # Forecast using last MA value
        last_ma = ts['ma'].iloc[-1]
        
        # Generate future dates
        last_date = ts['date'].iloc[-1]
        if self.frequency == 'M':
            future_dates = pd.date_range(start=last_date + timedelta(days=32), periods=forecast_periods, freq='MS')
        elif self.frequency == 'W':
            future_dates = pd.date_range(start=last_date + timedelta(days=7), periods=forecast_periods, freq='W-MON')
        else:
            future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=forecast_periods, freq='D')
        
        forecast_values = [last_ma] * forecast_periods
        
        result = {
            'method': 'Moving Average',
            'parameters': {'periods': periods},
            'historical': ts[['date', 'revenue']].to_dict(orient='records'),
            'forecast': [
                {'date': d.strftime('%Y-%m-%d'), 'revenue': round(v, 2)}
                for d, v in zip(future_dates, forecast_values)
            ],
            'total_forecasted_revenue': round(sum(forecast_values), 2)
        }
        
        self.forecasts['moving_average'] = result
        return result
    
    def linear_trend_forecast(self, forecast_periods: int = 6) -> Dict[str, Any]:
        """Linear regression trend forecast"""
        if self.time_series is None:
            self.prepare_time_series()
        
        ts = self.time_series.copy()
        
        # Prepare features
        X = np.arange(len(ts)).reshape(-1, 1)
        y = ts['revenue'].values
        
        # Fit linear regression
        model = LinearRegression()
        model.fit(X, y)
        
        # Generate predictions for historical data
        ts['trend'] = model.predict(X)
        
        # Forecast future periods
        future_X = np.arange(len(ts), len(ts) + forecast_periods).reshape(-1, 1)
        future_predictions = model.predict(future_X)
        
        # Ensure no negative forecasts
        future_predictions = np.maximum(future_predictions, 0)
        
        # Generate future dates
        last_date = ts['date'].iloc[-1]
        if self.frequency == 'M':
            future_dates = pd.date_range(start=last_date + timedelta(days=32), periods=forecast_periods, freq='MS')
        elif self.frequency == 'W':
            future_dates = pd.date_range(start=last_date + timedelta(days=7), periods=forecast_periods, freq='W-MON')
        else:
            future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=forecast_periods, freq='D')
        
        # Calculate R-squared
        r_squared = model.score(X, y)
        
        result = {
            'method': 'Linear Trend',
            'parameters': {
                'slope': round(model.coef_[0], 2),
                'intercept': round(model.intercept_, 2),
                'r_squared': round(r_squared, 4)
            },
            'historical': [
                {'date': row['date'].strftime('%Y-%m-%d') if hasattr(row['date'], 'strftime') else str(row['date']), 
                 'revenue': round(row['revenue'], 2),
                 'trend': round(row['trend'], 2)}
                for _, row in ts.iterrows()
            ],
            'forecast': [
                {'date': d.strftime('%Y-%m-%d'), 'revenue': round(v, 2)}
                for d, v in zip(future_dates, future_predictions)
            ],
            'total_forecasted_revenue': round(sum(future_predictions), 2)
        }
        
        self.forecasts['linear_trend'] = result
        return result
    
    def seasonal_decomposition(self) -> Dict[str, Any]:
        """Analyze seasonal patterns"""
        if self.time_series is None:
            self.prepare_time_series()
        
        ts = self.time_series.copy()
        
        if len(ts) < 12:
            return {'error': 'Insufficient data for seasonal analysis (need at least 12 periods)'}
        
        # Calculate monthly average (for monthly data)
        ts['month'] = pd.to_datetime(ts['date']).dt.month
        seasonal = ts.groupby('month')['revenue'].mean().reset_index()
        seasonal.columns = ['month', 'avg_revenue']
        
        # Calculate seasonal indices
        overall_mean = seasonal['avg_revenue'].mean()
        seasonal['seasonal_index'] = (seasonal['avg_revenue'] / overall_mean).round(3)
        
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        seasonal['month_name'] = seasonal['month'].map(lambda x: month_names[x-1])
        
        return {
            'seasonal_indices': seasonal[['month_name', 'seasonal_index', 'avg_revenue']].to_dict(orient='records'),
            'peak_month': seasonal.loc[seasonal['seasonal_index'].idxmax(), 'month_name'],
            'low_month': seasonal.loc[seasonal['seasonal_index'].idxmin(), 'month_name'],
            'seasonality_strength': round(seasonal['seasonal_index'].std(), 3)
        }
    
    def exponential_smoothing_forecast(self, alpha: float = 0.3, forecast_periods: int = 6) -> Dict[str, Any]:
        """Simple exponential smoothing forecast"""
        if self.time_series is None:
            self.prepare_time_series()
        
        ts = self.time_series.copy()
        
        # Calculate exponential smoothing
        smoothed = [ts['revenue'].iloc[0]]
        for i in range(1, len(ts)):
            smoothed.append(alpha * ts['revenue'].iloc[i] + (1 - alpha) * smoothed[-1])
        
        ts['smoothed'] = smoothed
        
        # Forecast (flat forecast based on last smoothed value)
        last_smoothed = smoothed[-1]
        
        # Generate future dates
        last_date = ts['date'].iloc[-1]
        if self.frequency == 'M':
            future_dates = pd.date_range(start=last_date + timedelta(days=32), periods=forecast_periods, freq='MS')
        else:
            future_dates = pd.date_range(start=last_date + timedelta(days=7), periods=forecast_periods, freq='W-MON')
        
        forecast_values = [last_smoothed] * forecast_periods
        
        result = {
            'method': 'Exponential Smoothing',
            'parameters': {'alpha': alpha},
            'historical': [
                {'date': row['date'].strftime('%Y-%m-%d') if hasattr(row['date'], 'strftime') else str(row['date']),
                 'revenue': round(row['revenue'], 2),
                 'smoothed': round(row['smoothed'], 2)}
                for _, row in ts.iterrows()
            ],
            'forecast': [
                {'date': d.strftime('%Y-%m-%d'), 'revenue': round(v, 2)}
                for d, v in zip(future_dates, forecast_values)
            ],
            'total_forecasted_revenue': round(sum(forecast_values), 2)
        }
        
        self.forecasts['exponential_smoothing'] = result
        return result
    
    def get_forecast_comparison(self) -> Dict[str, Any]:
        """Compare different forecasting methods"""
        if not self.forecasts:
            self.moving_average_forecast()
            self.linear_trend_forecast()
            self.exponential_smoothing_forecast()
        
        comparison = {
            'methods': [],
            'best_method': None,
            'forecast_summary': {}
        }
        
        total_forecasts = {}
        
        for method, result in self.forecasts.items():
            if 'total_forecasted_revenue' in result:
                total_forecasts[method] = result['total_forecasted_revenue']
                comparison['methods'].append({
                    'name': result.get('method', method),
                    'total_forecasted': result['total_forecasted_revenue'],
                    'parameters': result.get('parameters', {})
                })
        
        # Best method based on reasonable forecast
        if total_forecasts:
            avg_forecast = np.mean(list(total_forecasts.values()))
            comparison['forecast_summary'] = {
                'average_forecast': round(avg_forecast, 2),
                'min_forecast': round(min(total_forecasts.values()), 2),
                'max_forecast': round(max(total_forecasts.values()), 2)
            }
        
        return comparison
    
    def get_forecast_report(self, forecast_periods: int = 6) -> Dict[str, Any]:
        """Generate comprehensive forecast report"""
        if self.time_series is None:
            self.prepare_time_series()
        
        # Run all forecasting methods
        self.moving_average_forecast(forecast_periods=forecast_periods)
        self.linear_trend_forecast(forecast_periods=forecast_periods)
        self.exponential_smoothing_forecast(forecast_periods=forecast_periods)
        
        return {
            'generated_at': datetime.now().isoformat(),
            'forecast_horizon': forecast_periods,
            'frequency': self.frequency,
            'historical_periods': len(self.time_series),
            'forecasts': self.forecasts,
            'seasonal_analysis': self.seasonal_decomposition(),
            'comparison': self.get_forecast_comparison()
        }
