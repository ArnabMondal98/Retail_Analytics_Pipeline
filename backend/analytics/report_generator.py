"""
Report Generator Module
Generates static reports in various formats
"""
import pandas as pd
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates static reports in HTML and other formats"""
    
    def __init__(self, output_dir: str = 'outputs'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_html_report(self, report_data: Dict[str, Any], title: str = "Retail Analytics Report") -> str:
        """Generate an HTML report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"report_{timestamp}.html"
        filepath = self.output_dir / filename
        
        html_content = self._build_html_report(report_data, title)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML report generated: {filepath}")
        return str(filepath)
    
    def _build_html_report(self, data: Dict[str, Any], title: str) -> str:
        """Build HTML content for the report"""
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f8fafc;
            color: #0f172a;
            line-height: 1.6;
            padding: 2rem;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ 
            background: linear-gradient(135deg, #0f172a, #1e293b);
            color: white;
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
        }}
        .header h1 {{ font-size: 2rem; margin-bottom: 0.5rem; }}
        .header .timestamp {{ opacity: 0.8; font-size: 0.9rem; }}
        .section {{ 
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .section h2 {{ 
            color: #0f172a;
            font-size: 1.25rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #e2e8f0;
        }}
        .kpi-grid {{ 
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
        }}
        .kpi-card {{ 
            background: #f1f5f9;
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
        }}
        .kpi-card .value {{ 
            font-size: 1.5rem;
            font-weight: bold;
            color: #2563eb;
        }}
        .kpi-card .label {{ 
            font-size: 0.85rem;
            color: #64748b;
            margin-top: 0.25rem;
        }}
        table {{ 
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }}
        th, td {{ 
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }}
        th {{ 
            background: #f8fafc;
            font-weight: 600;
            color: #64748b;
            font-size: 0.85rem;
            text-transform: uppercase;
        }}
        tr:hover {{ background: #f8fafc; }}
        .chart-placeholder {{ 
            background: #f1f5f9;
            border-radius: 8px;
            padding: 2rem;
            text-align: center;
            color: #64748b;
        }}
        .footer {{ 
            text-align: center;
            padding: 1rem;
            color: #64748b;
            font-size: 0.85rem;
        }}
        @media print {{
            body {{ padding: 0; }}
            .section {{ break-inside: avoid; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <div class="timestamp">Generated: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}</div>
        </div>
"""
        
        # KPI Section
        if 'kpis' in data:
            html += self._build_kpi_section(data['kpis'])
        
        # Summary Section
        if 'summary' in data:
            html += self._build_summary_section(data['summary'])
        
        # RFM Section
        if 'rfm' in data:
            html += self._build_rfm_section(data['rfm'])
        
        # Segmentation Section
        if 'segmentation' in data:
            html += self._build_segmentation_section(data['segmentation'])
        
        # Performance Section
        if 'performance' in data:
            html += self._build_performance_section(data['performance'])
        
        # Forecast Section
        if 'forecast' in data:
            html += self._build_forecast_section(data['forecast'])
        
        html += """
        <div class="footer">
            <p>RetailPulse Analytics - Automated Report Generation</p>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def _build_kpi_section(self, kpis: Dict[str, Any]) -> str:
        """Build KPI cards HTML"""
        html = '<div class="section"><h2>Key Performance Indicators</h2><div class="kpi-grid">'
        
        kpi_mapping = [
            ('revenue', 'total_revenue', 'Total Revenue', '$'),
            ('revenue', 'avg_order_value', 'Avg Order Value', '$'),
            ('revenue', 'total_transactions', 'Total Transactions', ''),
            ('customer', 'unique_customers', 'Unique Customers', ''),
            ('customer', 'repeat_customer_rate', 'Repeat Rate', '', '%'),
            ('geographic', 'unique_countries', 'Countries', ''),
        ]
        
        for mapping in kpi_mapping:
            category = mapping[0]
            key = mapping[1]
            label = mapping[2]
            prefix = mapping[3] if len(mapping) > 3 else ''
            suffix = mapping[4] if len(mapping) > 4 else ''
            
            if category in kpis and key in kpis[category]:
                value = kpis[category][key]
                if isinstance(value, float):
                    formatted = f"{prefix}{value:,.2f}{suffix}"
                else:
                    formatted = f"{prefix}{value:,}{suffix}"
                html += f'''
                <div class="kpi-card">
                    <div class="value">{formatted}</div>
                    <div class="label">{label}</div>
                </div>'''
        
        html += '</div></div>'
        return html
    
    def _build_summary_section(self, summary: Dict[str, Any]) -> str:
        """Build summary section HTML"""
        html = '<div class="section"><h2>Executive Summary</h2>'
        html += '<div class="kpi-grid">'
        
        for item in summary[:6]:  # Top 6 items
            html += f'''
            <div class="kpi-card">
                <div class="value">{item.get('value', 'N/A')}</div>
                <div class="label">{item.get('name', 'Metric')}</div>
            </div>'''
        
        html += '</div></div>'
        return html
    
    def _build_rfm_section(self, rfm: Dict[str, Any]) -> str:
        """Build RFM analysis section HTML"""
        html = '<div class="section"><h2>RFM Customer Analysis</h2>'
        
        if 'segment_summary' in rfm:
            html += '<table><thead><tr>'
            html += '<th>Segment</th><th>Customers</th><th>% Customers</th>'
            html += '<th>Avg Recency</th><th>Avg Frequency</th><th>Total Revenue</th></tr></thead><tbody>'
            
            for seg in rfm['segment_summary'][:10]:
                html += f'''<tr>
                    <td>{seg.get('segment', 'N/A')}</td>
                    <td>{seg.get('customer_count', 0):,}</td>
                    <td>{seg.get('customer_pct', 0)}%</td>
                    <td>{seg.get('avg_recency', 0):.0f} days</td>
                    <td>{seg.get('avg_frequency', 0):.1f}</td>
                    <td>${seg.get('total_monetary', 0):,.2f}</td>
                </tr>'''
            
            html += '</tbody></table>'
        
        html += '</div>'
        return html
    
    def _build_segmentation_section(self, segmentation: Dict[str, Any]) -> str:
        """Build customer segmentation section HTML"""
        html = '<div class="section"><h2>Customer Segmentation (K-Means)</h2>'
        
        if 'cluster_profiles' in segmentation:
            html += '<table><thead><tr>'
            html += '<th>Cluster</th><th>Label</th><th>Customers</th><th>%</th>'
            html += '<th>Avg Spend</th><th>Total Revenue</th></tr></thead><tbody>'
            
            for profile in segmentation['cluster_profiles']:
                html += f'''<tr>
                    <td>{profile.get('cluster_id', 'N/A')}</td>
                    <td>{profile.get('label', 'N/A')}</td>
                    <td>{profile.get('customer_count', 0):,}</td>
                    <td>{profile.get('percentage', 0)}%</td>
                    <td>${profile.get('avg_spend', 0):,.2f}</td>
                    <td>${profile.get('total_revenue', 0):,.2f}</td>
                </tr>'''
            
            html += '</tbody></table>'
        
        html += '</div>'
        return html
    
    def _build_performance_section(self, performance: Dict[str, Any]) -> str:
        """Build performance section HTML"""
        html = '<div class="section"><h2>Monthly Performance</h2>'
        
        if 'monthly' in performance:
            html += '<table><thead><tr>'
            html += '<th>Period</th><th>Revenue</th><th>Transactions</th>'
            html += '<th>Customers</th><th>Growth</th></tr></thead><tbody>'
            
            for month in performance['monthly'][-12:]:  # Last 12 months
                growth = month.get('revenue_growth', 0)
                growth_class = 'color: #10b981' if growth >= 0 else 'color: #ef4444'
                html += f'''<tr>
                    <td>{month.get('period', 'N/A')}</td>
                    <td>${month.get('revenue', 0):,.2f}</td>
                    <td>{month.get('unique_transactions', 0):,}</td>
                    <td>{month.get('unique_customers', 0):,}</td>
                    <td style="{growth_class}">{growth:+.1f}%</td>
                </tr>'''
            
            html += '</tbody></table>'
        
        html += '</div>'
        return html
    
    def _build_forecast_section(self, forecast: Dict[str, Any]) -> str:
        """Build forecast section HTML"""
        html = '<div class="section"><h2>Sales Forecast</h2>'
        
        if 'comparison' in forecast and 'forecast_summary' in forecast['comparison']:
            summary = forecast['comparison']['forecast_summary']
            html += '<div class="kpi-grid">'
            html += f'''
            <div class="kpi-card">
                <div class="value">${summary.get('average_forecast', 0):,.2f}</div>
                <div class="label">Avg Forecast</div>
            </div>
            <div class="kpi-card">
                <div class="value">${summary.get('min_forecast', 0):,.2f}</div>
                <div class="label">Min Forecast</div>
            </div>
            <div class="kpi-card">
                <div class="value">${summary.get('max_forecast', 0):,.2f}</div>
                <div class="label">Max Forecast</div>
            </div>'''
            html += '</div>'
        
        html += '</div>'
        return html
    
    def export_to_json(self, data: Dict[str, Any], filename: str = None) -> str:
        """Export data to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"data_export_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        # Convert non-serializable objects
        def convert(obj):
            if isinstance(obj, (pd.Timestamp, datetime)):
                return obj.isoformat()
            if isinstance(obj, pd.Period):
                return str(obj)
            if hasattr(obj, 'tolist'):
                return obj.tolist()
            return str(obj)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, default=convert, indent=2)
        
        logger.info(f"JSON export created: {filepath}")
        return str(filepath)
    
    def list_generated_reports(self) -> List[Dict[str, Any]]:
        """List all generated reports"""
        reports = []
        
        for file_path in self.output_dir.glob('*'):
            if file_path.is_file():
                reports.append({
                    'filename': file_path.name,
                    'path': str(file_path),
                    'size_kb': round(file_path.stat().st_size / 1024, 2),
                    'created': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                    'type': file_path.suffix[1:].upper()
                })
        
        return sorted(reports, key=lambda x: x['created'], reverse=True)
