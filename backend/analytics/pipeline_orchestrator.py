"""
Pipeline Orchestrator Module
Orchestrates the complete analytics pipeline
"""
import pandas as pd
import logging
import json
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import traceback

from .data_ingestion import DataIngestion
from .data_cleaning import DataCleaning
from .feature_engineering import FeatureEngineering
from .eda import ExploratoryDataAnalysis
from .rfm_analysis import RFMAnalysis
from .segmentation import CustomerSegmentation
from .clv import CustomerLifetimeValue
from .kpi_generator import KPIGenerator
from .performance_analysis import PerformanceAnalysis
from .forecasting import SalesForecasting
from .report_generator import ReportGenerator

logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """Orchestrates the complete retail analytics pipeline"""
    
    STAGES = [
        'ingestion',
        'cleaning',
        'feature_engineering',
        'eda',
        'rfm_analysis',
        'segmentation',
        'clv',
        'kpi_generation',
        'performance_analysis',
        'forecasting',
        'report_generation',
        'export'
    ]
    
    def __init__(self, data_path: str, output_dir: str = 'outputs'):
        self.data_path = data_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.raw_data: pd.DataFrame = None
        self.cleaned_data: pd.DataFrame = None
        self.featured_data: pd.DataFrame = None
        
        self.results: Dict[str, Any] = {}
        self.status: Dict[str, Any] = {
            'current_stage': None,
            'stages_completed': [],
            'stages_failed': [],
            'start_time': None,
            'end_time': None,
            'errors': []
        }
        
        self.progress_callback: Optional[Callable] = None
        
    def set_progress_callback(self, callback: Callable):
        """Set callback function for progress updates"""
        self.progress_callback = callback
        
    def _update_progress(self, stage: str, status: str, message: str = "", progress: float = 0):
        """Update pipeline progress"""
        self.status['current_stage'] = stage
        
        if self.progress_callback:
            self.progress_callback({
                'stage': stage,
                'status': status,
                'message': message,
                'progress': progress,
                'stages_completed': self.status['stages_completed']
            })
        
        logger.info(f"[{stage}] {status}: {message}")
    
    def run_stage(self, stage: str) -> bool:
        """Run a specific pipeline stage"""
        try:
            self._update_progress(stage, 'running', f'Starting {stage}...')
            
            if stage == 'ingestion':
                self._run_ingestion()
            elif stage == 'cleaning':
                self._run_cleaning()
            elif stage == 'feature_engineering':
                self._run_feature_engineering()
            elif stage == 'eda':
                self._run_eda()
            elif stage == 'rfm_analysis':
                self._run_rfm_analysis()
            elif stage == 'segmentation':
                self._run_segmentation()
            elif stage == 'clv':
                self._run_clv()
            elif stage == 'kpi_generation':
                self._run_kpi_generation()
            elif stage == 'performance_analysis':
                self._run_performance_analysis()
            elif stage == 'forecasting':
                self._run_forecasting()
            elif stage == 'report_generation':
                self._run_report_generation()
            elif stage == 'export':
                self._run_export()
            
            self.status['stages_completed'].append(stage)
            self._update_progress(stage, 'completed', f'{stage} completed successfully')
            return True
            
        except Exception as e:
            error_msg = f"{stage} failed: {str(e)}"
            self.status['stages_failed'].append(stage)
            self.status['errors'].append({
                'stage': stage,
                'error': str(e),
                'traceback': traceback.format_exc()
            })
            self._update_progress(stage, 'failed', error_msg)
            logger.error(error_msg)
            return False
    
    def _run_ingestion(self):
        """Run data ingestion stage"""
        ingestion = DataIngestion(self.data_path)
        self.raw_data = ingestion.load_data()
        validation = ingestion.validate_schema()
        quality = ingestion.get_data_quality_report()
        
        self.results['ingestion'] = {
            'summary': ingestion.get_summary(),
            'validation': validation,
            'quality': quality
        }
    
    def _run_cleaning(self):
        """Run data cleaning stage"""
        if self.raw_data is None:
            raise ValueError("Data not loaded. Run ingestion first.")
        
        cleaner = DataCleaning(self.raw_data)
        self.cleaned_data = cleaner.run_full_cleaning_pipeline()
        
        self.results['cleaning'] = cleaner.get_cleaning_report()
    
    def _run_feature_engineering(self):
        """Run feature engineering stage"""
        if self.cleaned_data is None:
            raise ValueError("Data not cleaned. Run cleaning first.")
        
        engineer = FeatureEngineering(self.cleaned_data)
        self.featured_data = engineer.run_full_feature_pipeline()
        
        self.results['feature_engineering'] = {
            'report': engineer.get_feature_report(),
            'customer_features': len(engineer.get_customer_features()),
            'product_features': len(engineer.get_product_features()),
            'country_features': len(engineer.get_country_features())
        }
        
        # Store aggregated features
        self.customer_features = engineer.get_customer_features()
        self.product_features = engineer.get_product_features()
        self.country_features = engineer.get_country_features()
    
    def _run_eda(self):
        """Run exploratory data analysis"""
        df = self.featured_data if self.featured_data is not None else self.cleaned_data
        if df is None:
            raise ValueError("No data available for EDA")
        
        eda = ExploratoryDataAnalysis(df)
        self.results['eda'] = eda.get_full_eda_report()
    
    def _run_rfm_analysis(self):
        """Run RFM analysis"""
        df = self.featured_data if self.featured_data is not None else self.cleaned_data
        if df is None:
            raise ValueError("No data available for RFM analysis")
        
        rfm = RFMAnalysis(df)
        rfm.calculate_rfm_metrics()
        rfm.assign_rfm_scores()
        rfm.assign_customer_segments()
        
        self.results['rfm'] = rfm.get_rfm_report()
        self.rfm_data = rfm.get_rfm_data()
    
    def _run_segmentation(self):
        """Run customer segmentation"""
        df = self.featured_data if self.featured_data is not None else self.cleaned_data
        if df is None:
            raise ValueError("No data available for segmentation")
        
        seg = CustomerSegmentation(df)
        seg.prepare_customer_data()
        seg.scale_features()
        elbow = seg.find_optimal_k()
        seg.perform_clustering()
        
        self.results['segmentation'] = seg.get_segmentation_report()
        self.results['segmentation']['elbow_analysis'] = elbow
        self.segmented_customers = seg.get_segmented_customers()
    
    def _run_clv(self):
        """Run CLV calculation"""
        df = self.featured_data if self.featured_data is not None else self.cleaned_data
        if df is None:
            raise ValueError("No data available for CLV calculation")
        
        clv = CustomerLifetimeValue(df)
        clv.calculate_clv_metrics()
        
        self.results['clv'] = clv.get_clv_report()
        self.clv_data = clv.get_clv_data()
    
    def _run_kpi_generation(self):
        """Run KPI generation"""
        df = self.featured_data if self.featured_data is not None else self.cleaned_data
        if df is None:
            raise ValueError("No data available for KPI generation")
        
        kpi = KPIGenerator(df)
        self.results['kpis'] = kpi.get_kpi_report()
    
    def _run_performance_analysis(self):
        """Run performance analysis"""
        df = self.featured_data if self.featured_data is not None else self.cleaned_data
        if df is None:
            raise ValueError("No data available for performance analysis")
        
        perf = PerformanceAnalysis(df)
        self.results['performance'] = perf.get_performance_report()
    
    def _run_forecasting(self):
        """Run sales forecasting"""
        df = self.featured_data if self.featured_data is not None else self.cleaned_data
        if df is None:
            raise ValueError("No data available for forecasting")
        
        forecast = SalesForecasting(df)
        self.results['forecast'] = forecast.get_forecast_report(forecast_periods=6)
    
    def _run_report_generation(self):
        """Generate reports"""
        reporter = ReportGenerator(str(self.output_dir))
        
        # Compile report data
        report_data = {
            'kpis': self.results.get('kpis', {}).get('kpis', {}),
            'summary': self.results.get('kpis', {}).get('summary', []),
            'rfm': self.results.get('rfm', {}),
            'segmentation': self.results.get('segmentation', {}),
            'performance': self.results.get('performance', {}),
            'forecast': self.results.get('forecast', {})
        }
        
        # Generate HTML report
        html_path = reporter.generate_html_report(report_data, "Retail Analytics Report")
        
        # Export JSON summary
        json_path = reporter.export_to_json(self.results, "analytics_results.json")
        
        self.results['reports'] = {
            'html_report': html_path,
            'json_export': json_path,
            'generated_files': reporter.list_generated_reports()
        }
    
    def _run_export(self):
        """Export processed datasets"""
        exports = {}
        
        # Export cleaned data
        if self.cleaned_data is not None:
            csv_path = self.output_dir / 'cleaned_data.csv'
            excel_path = self.output_dir / 'cleaned_data.xlsx'
            self.cleaned_data.to_csv(csv_path, index=False)
            self.cleaned_data.to_excel(excel_path, index=False)
            exports['cleaned_data'] = {'csv': str(csv_path), 'excel': str(excel_path)}
        
        # Export RFM data
        if hasattr(self, 'rfm_data') and self.rfm_data is not None:
            csv_path = self.output_dir / 'rfm_analysis.csv'
            excel_path = self.output_dir / 'rfm_analysis.xlsx'
            self.rfm_data.to_csv(csv_path, index=False)
            self.rfm_data.to_excel(excel_path, index=False)
            exports['rfm_analysis'] = {'csv': str(csv_path), 'excel': str(excel_path)}
        
        # Export segmented customers
        if hasattr(self, 'segmented_customers') and self.segmented_customers is not None:
            csv_path = self.output_dir / 'customer_segments.csv'
            excel_path = self.output_dir / 'customer_segments.xlsx'
            self.segmented_customers.to_csv(csv_path, index=False)
            self.segmented_customers.to_excel(excel_path, index=False)
            exports['customer_segments'] = {'csv': str(csv_path), 'excel': str(excel_path)}
        
        # Export CLV data
        if hasattr(self, 'clv_data') and self.clv_data is not None:
            csv_path = self.output_dir / 'customer_ltv.csv'
            excel_path = self.output_dir / 'customer_ltv.xlsx'
            self.clv_data.to_csv(csv_path, index=False)
            self.clv_data.to_excel(excel_path, index=False)
            exports['customer_ltv'] = {'csv': str(csv_path), 'excel': str(excel_path)}
        
        self.results['exports'] = exports
    
    def run_full_pipeline(self) -> Dict[str, Any]:
        """Run the complete analytics pipeline"""
        self.status['start_time'] = datetime.now().isoformat()
        
        logger.info("Starting full analytics pipeline...")
        
        for i, stage in enumerate(self.STAGES):
            progress = (i / len(self.STAGES)) * 100
            self._update_progress(stage, 'starting', f'Stage {i+1}/{len(self.STAGES)}', progress)
            
            success = self.run_stage(stage)
            
            # Continue even if a stage fails (log the error)
            if not success:
                logger.warning(f"Stage {stage} failed, continuing with next stage...")
        
        self.status['end_time'] = datetime.now().isoformat()
        
        # Calculate total execution time
        start = datetime.fromisoformat(self.status['start_time'])
        end = datetime.fromisoformat(self.status['end_time'])
        self.status['execution_time_seconds'] = (end - start).total_seconds()
        
        self._update_progress('complete', 'finished', 'Pipeline completed', 100)
        
        return self.get_pipeline_results()
    
    def get_pipeline_results(self) -> Dict[str, Any]:
        """Get all pipeline results"""
        return {
            'status': self.status,
            'results': self.results
        }
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status"""
        return self.status
