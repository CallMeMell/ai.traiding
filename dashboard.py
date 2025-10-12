"""
dashboard.py - Visual Dashboard with Metrics and Charts
========================================================
Enhanced dashboard with modal window for managing metrics and charts.
Supports multiple chart types and real-time data integration.
"""
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

from utils import calculate_performance_metrics, load_trades_from_csv

logger = logging.getLogger(__name__)

# Global task tracker for active operations
_active_tasks = []
_task_id_counter = 0


class DashboardConfig:
    """Configuration for dashboard metrics and charts"""
    
    DEFAULT_METRICS = [
        'total_pnl',
        'win_rate',
        'total_trades',
        'best_trade',
        'worst_trade',
        'avg_pnl',
        'current_capital'
    ]
    
    DEFAULT_CHARTS = [
        {'type': 'line', 'title': 'P&L Over Time', 'data_source': 'pnl_history'},
        {'type': 'bar', 'title': 'Trades per Strategy', 'data_source': 'strategy_stats'},
        {'type': 'pie', 'title': 'Win/Loss Distribution', 'data_source': 'win_loss'}
    ]
    
    def __init__(self, config_file: str = "data/dashboard_config.json"):
        """
        Initialize dashboard configuration
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.metrics = self.DEFAULT_METRICS.copy()
        self.charts = self.DEFAULT_CHARTS.copy()
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.metrics = data.get('metrics', self.DEFAULT_METRICS)
                    self.charts = data.get('charts', self.DEFAULT_CHARTS)
                logger.info(f"Dashboard config loaded from {self.config_file}")
            except Exception as e:
                logger.warning(f"Could not load dashboard config: {e}")
    
    def save_config(self):
        """Save configuration to file"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'metrics': self.metrics,
                    'charts': self.charts,
                    'updated_at': datetime.now().isoformat()
                }, f, indent=2)
            logger.info(f"Dashboard config saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Could not save dashboard config: {e}")
    
    def add_metric(self, metric: str):
        """Add a metric to the dashboard"""
        if metric not in self.metrics:
            self.metrics.append(metric)
            self.save_config()
            logger.info(f"Added metric: {metric}")
    
    def remove_metric(self, metric: str):
        """Remove a metric from the dashboard"""
        if metric in self.metrics:
            self.metrics.remove(metric)
            self.save_config()
            logger.info(f"Removed metric: {metric}")
    
    def add_chart(self, chart_type: str, title: str, data_source: str):
        """Add a chart to the dashboard"""
        chart = {'type': chart_type, 'title': title, 'data_source': data_source}
        self.charts.append(chart)
        self.save_config()
        logger.info(f"Added chart: {title}")
    
    def remove_chart(self, title: str):
        """Remove a chart from the dashboard"""
        self.charts = [c for c in self.charts if c['title'] != title]
        self.save_config()
        logger.info(f"Removed chart: {title}")


class VisualDashboard:
    """
    Visual Dashboard for Trading Bot
    
    Displays metrics and charts with real-time data integration.
    Supports browser cache and database storage.
    """
    
    def __init__(self, trades_file: str = "data/trades.csv", 
                 config_file: str = "data/dashboard_config.json"):
        """
        Initialize dashboard
        
        Args:
            trades_file: Path to trades CSV file
            config_file: Path to dashboard configuration
        """
        self.trades_file = trades_file
        self.config = DashboardConfig(config_file)
        logger.info("Visual Dashboard initialized")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current metrics
        
        Returns:
            Dictionary with metric values
        """
        trades = load_trades_from_csv(self.trades_file)
        all_metrics = calculate_performance_metrics(trades)
        
        # Add current capital from last trade
        if trades:
            try:
                all_metrics['current_capital'] = float(trades[-1].get('capital', 0))
            except (ValueError, TypeError):
                all_metrics['current_capital'] = 0.0
        else:
            all_metrics['current_capital'] = 0.0
        
        # Filter to only configured metrics
        return {k: v for k, v in all_metrics.items() if k in self.config.metrics}
    
    def get_chart_data(self, data_source: str) -> Dict[str, Any]:
        """
        Get data for a specific chart
        
        Args:
            data_source: Type of data to retrieve
        
        Returns:
            Dictionary with chart data
        """
        trades = load_trades_from_csv(self.trades_file)
        
        if data_source == 'pnl_history':
            return self._get_pnl_history(trades)
        elif data_source == 'strategy_stats':
            return self._get_strategy_stats(trades)
        elif data_source == 'win_loss':
            return self._get_win_loss_distribution(trades)
        else:
            return {}
    
    def _get_pnl_history(self, trades: List[Dict]) -> Dict[str, Any]:
        """Get P&L history over time"""
        if not trades:
            return {'timestamps': [], 'pnl': []}
        
        timestamps = []
        cumulative_pnl = []
        total = 0
        
        for trade in trades:
            if trade.get('pnl', '0') != '0.00':
                try:
                    pnl = float(trade.get('pnl', 0))
                    total += pnl
                    timestamps.append(trade.get('timestamp', ''))
                    cumulative_pnl.append(total)
                except (ValueError, TypeError):
                    continue
        
        return {'timestamps': timestamps, 'pnl': cumulative_pnl}
    
    def _get_strategy_stats(self, trades: List[Dict]) -> Dict[str, Any]:
        """Get trade statistics per strategy"""
        strategy_counts = {}
        
        for trade in trades:
            strategies = trade.get('triggering_strategies', '')
            if strategies:
                for strategy in strategies.split(','):
                    strategy = strategy.strip()
                    strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        
        return {
            'strategies': list(strategy_counts.keys()),
            'counts': list(strategy_counts.values())
        }
    
    def _get_win_loss_distribution(self, trades: List[Dict]) -> Dict[str, Any]:
        """Get win/loss distribution"""
        wins = 0
        losses = 0
        
        for trade in trades:
            if trade.get('pnl', '0') != '0.00':
                try:
                    pnl = float(trade.get('pnl', 0))
                    if pnl > 0:
                        wins += 1
                    elif pnl < 0:
                        losses += 1
                except (ValueError, TypeError):
                    continue
        
        return {'labels': ['Wins', 'Losses'], 'values': [wins, losses]}
    
    def generate_chart_matplotlib(self, chart_config: Dict[str, Any], 
                                  output_file: str) -> bool:
        """
        Generate chart using Matplotlib
        
        Args:
            chart_config: Chart configuration
            output_file: Output file path
        
        Returns:
            True if successful
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.warning("Matplotlib not available")
            return False
        
        try:
            chart_type = chart_config['type']
            title = chart_config['title']
            data_source = chart_config['data_source']
            
            data = self.get_chart_data(data_source)
            
            plt.figure(figsize=(10, 6))
            
            if chart_type == 'line' and data_source == 'pnl_history':
                plt.plot(range(len(data['pnl'])), data['pnl'], marker='o')
                plt.xlabel('Trade Number')
                plt.ylabel('Cumulative P&L ($)')
                plt.grid(True)
            
            elif chart_type == 'bar' and data_source == 'strategy_stats':
                plt.bar(data['strategies'], data['counts'])
                plt.xlabel('Strategy')
                plt.ylabel('Number of Trades')
                plt.xticks(rotation=45)
            
            elif chart_type == 'pie' and data_source == 'win_loss':
                plt.pie(data['values'], labels=data['labels'], autopct='%1.1f%%')
            
            plt.title(title)
            plt.tight_layout()
            
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            plt.savefig(output_file)
            plt.close()
            
            logger.info(f"Chart saved to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating chart: {e}")
            return False
    
    def generate_chart_plotly(self, chart_config: Dict[str, Any], 
                             output_file: str) -> bool:
        """
        Generate interactive chart using Plotly
        
        Args:
            chart_config: Chart configuration
            output_file: Output file path (HTML)
        
        Returns:
            True if successful
        """
        if not PLOTLY_AVAILABLE:
            logger.warning("Plotly not available")
            return False
        
        try:
            chart_type = chart_config['type']
            title = chart_config['title']
            data_source = chart_config['data_source']
            
            data = self.get_chart_data(data_source)
            
            fig = None
            
            if chart_type == 'line' and data_source == 'pnl_history':
                fig = go.Figure(data=go.Scatter(
                    x=list(range(len(data['pnl']))),
                    y=data['pnl'],
                    mode='lines+markers'
                ))
                fig.update_layout(
                    title=title,
                    xaxis_title='Trade Number',
                    yaxis_title='Cumulative P&L ($)'
                )
            
            elif chart_type == 'bar' and data_source == 'strategy_stats':
                fig = go.Figure(data=go.Bar(
                    x=data['strategies'],
                    y=data['counts']
                ))
                fig.update_layout(
                    title=title,
                    xaxis_title='Strategy',
                    yaxis_title='Number of Trades'
                )
            
            elif chart_type == 'pie' and data_source == 'win_loss':
                fig = go.Figure(data=go.Pie(
                    labels=data['labels'],
                    values=data['values']
                ))
                fig.update_layout(title=title)
            
            if fig:
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                fig.write_html(output_file)
                logger.info(f"Interactive chart saved to {output_file}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error generating Plotly chart: {e}")
            return False
    
    def generate_all_charts(self, output_dir: str = "data/charts", 
                           use_plotly: bool = True) -> List[str]:
        """
        Generate all configured charts
        
        Args:
            output_dir: Directory for chart outputs
            use_plotly: Use Plotly (True) or Matplotlib (False)
        
        Returns:
            List of generated file paths
        """
        generated_files = []
        
        for chart in self.config.charts:
            title_safe = chart['title'].replace(' ', '_').replace('/', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if use_plotly and PLOTLY_AVAILABLE:
                filename = f"{title_safe}_{timestamp}.html"
                filepath = os.path.join(output_dir, filename)
                if self.generate_chart_plotly(chart, filepath):
                    generated_files.append(filepath)
            elif MATPLOTLIB_AVAILABLE:
                filename = f"{title_safe}_{timestamp}.png"
                filepath = os.path.join(output_dir, filename)
                if self.generate_chart_matplotlib(chart, filepath):
                    generated_files.append(filepath)
        
        return generated_files
    
    def display_metrics_console(self):
        """Display metrics in console format"""
        metrics = self.get_metrics()
        
        print("\n" + "=" * 60)
        print("📊 DASHBOARD METRICS")
        print("=" * 60)
        
        for key, value in metrics.items():
            label = key.replace('_', ' ').title()
            if 'pnl' in key or 'trade' in key.lower():
                print(f"{label:.<30} ${value:,.2f}")
            elif 'rate' in key:
                print(f"{label:.<30} {value:.2f}%")
            else:
                print(f"{label:.<30} {value}")
        
        print("=" * 60)
    
    def export_dashboard_html(self, output_file: str = "data/dashboard.html"):
        """
        Export complete dashboard as HTML
        
        Args:
            output_file: Output HTML file path
        """
        metrics = self.get_metrics()
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Trading Bot Dashboard</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .dashboard {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #007bff;
            padding-bottom: 10px;
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #007bff;
        }}
        .metric-label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #333;
            margin-top: 5px;
        }}
        .charts {{
            margin-top: 30px;
        }}
        .timestamp {{
            text-align: right;
            color: #999;
            font-size: 12px;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <h1>📊 Trading Bot Dashboard</h1>
        
        <div class="metrics">
"""
        
        for key, value in metrics.items():
            label = key.replace('_', ' ').title()
            if 'pnl' in key or 'trade' in key.lower():
                formatted_value = f"${value:,.2f}"
            elif 'rate' in key:
                formatted_value = f"{value:.2f}%"
            else:
                formatted_value = str(value)
            
            html += f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{formatted_value}</div>
            </div>
"""
        
        html += """
        </div>
        
        <div class="charts">
            <h2>Charts</h2>
            <p><em>Charts can be generated using generate_all_charts() method</em></p>
        </div>
        
        <div class="timestamp">
            Generated: {timestamp}
        </div>
    </div>
</body>
</html>
""".format(timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"Dashboard exported to {output_file}")


class DashboardModal:
    """
    Modal window manager for dashboard configuration
    
    Simulates a modal interface for adding/removing metrics and charts.
    In a GUI application, this would create an actual modal window.
    """
    
    def __init__(self, dashboard: VisualDashboard):
        """
        Initialize modal
        
        Args:
            dashboard: VisualDashboard instance
        """
        self.dashboard = dashboard
        self.is_open = False
    
    def open(self):
        """Open the modal"""
        self.is_open = True
        logger.info("Dashboard modal opened")
    
    def close(self):
        """Close the modal"""
        self.is_open = False
        logger.info("Dashboard modal closed")
    
    def add_metric(self, metric: str):
        """Add a metric through the modal"""
        if self.is_open:
            self.dashboard.config.add_metric(metric)
            return True
        return False
    
    def remove_metric(self, metric: str):
        """Remove a metric through the modal"""
        if self.is_open:
            self.dashboard.config.remove_metric(metric)
            return True
        return False
    
    def add_chart(self, chart_type: str, title: str, data_source: str):
        """Add a chart through the modal"""
        if self.is_open:
            self.dashboard.config.add_chart(chart_type, title, data_source)
            return True
        return False
    
    def remove_chart(self, title: str):
        """Remove a chart through the modal"""
        if self.is_open:
            self.dashboard.config.remove_chart(title)
            return True
        return False
    
    def get_available_metrics(self) -> List[str]:
        """Get list of available metrics"""
        return [
            'total_pnl', 'win_rate', 'total_trades',
            'best_trade', 'worst_trade', 'avg_pnl'
        ]
    
    def get_available_chart_types(self) -> List[str]:
        """Get list of available chart types"""
        return ['line', 'bar', 'pie']
    
    def get_available_data_sources(self) -> List[str]:
        """Get list of available data sources"""
        return ['pnl_history', 'strategy_stats', 'win_loss']


def create_dashboard(trades_file: str = "data/trades.csv",
                     config_file: str = "data/dashboard_config.json") -> VisualDashboard:
    """
    Factory function to create a dashboard instance
    
    Args:
        trades_file: Path to trades CSV
        config_file: Path to dashboard config
    
    Returns:
        VisualDashboard instance
    """
    return VisualDashboard(trades_file, config_file)


# ==================== FLASK WEB DASHBOARD ====================

try:
    from flask import Flask, render_template, jsonify, request
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    logger.warning("Flask not available. Web dashboard will not be accessible.")

if FLASK_AVAILABLE:
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'trading-bot-secret-key-change-in-production'
    
    # Global dashboard instance for web interface
    _web_dashboard = None
    
    def init_web_dashboard(trades_file: str = "data/trades.csv",
                          config_file: str = "data/dashboard_config.json"):
        """Initialize the web dashboard instance"""
        global _web_dashboard
        _web_dashboard = create_dashboard(trades_file, config_file)
        return _web_dashboard
    
    def _add_active_task(task_name: str, task_type: str, details: str = "") -> int:
        """
        Add an active task to the tracker
        
        Args:
            task_name: Name of the task
            task_type: Type of task (backtest, simulation, optimization, etc.)
            details: Additional details about the task
            
        Returns:
            Task ID
        """
        global _active_tasks, _task_id_counter
        _task_id_counter += 1
        
        task = {
            'id': _task_id_counter,
            'name': task_name,
            'type': task_type,
            'details': details,
            'status': 'running',
            'progress': 0,
            'started_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        _active_tasks.append(task)
        logger.info(f"Added active task: {task_name} (ID: {_task_id_counter})")
        return _task_id_counter
    
    def _update_active_task(task_id: int, progress: int = None, status: str = None, details: str = None):
        """
        Update an active task
        
        Args:
            task_id: Task ID
            progress: Progress percentage (0-100)
            status: Task status (running, completed, failed)
            details: Updated details
        """
    
    def _remove_active_task(task_id: int):
        """
        Remove a task from active tasks
        
        Args:
            task_id: Task ID
        """
        global _active_tasks
        _active_tasks = [task for task in _active_tasks if task['id'] != task_id]
        logger.info(f"Removed task {task_id}")
    
    def _get_active_tasks() -> List[Dict[str, Any]]:
        """
        Get all active tasks
        
        Returns:
            List of active tasks
        """
        global _active_tasks
        # Clean up old completed/failed tasks (older than 1 hour)
        current_time = datetime.now()
        cleaned_tasks = []
        for task in _active_tasks:
            try:
                updated_at = datetime.strptime(task['updated_at'], '%Y-%m-%d %H:%M:%S')
                time_diff = (current_time - updated_at).total_seconds() / 3600
                # Keep running tasks and recent completed/failed tasks (< 1 hour)
                if task['status'] == 'running' or time_diff < 1:
                    cleaned_tasks.append(task)
            except:
                cleaned_tasks.append(task)
        _active_tasks = cleaned_tasks
        return _active_tasks.copy()
    
    def _get_session_list() -> List[Dict[str, Any]]:
        """
        Get list of all trading sessions from logs directory
        
        Returns:
            List of session summaries
        """
        sessions = []
        logs_dir = "logs"
        
        if not os.path.exists(logs_dir):
            return sessions
        
        # Scan for session log files
        for filename in os.listdir(logs_dir):
            if filename.startswith("simulated_trading_session_") and filename.endswith(".log"):
                filepath = os.path.join(logs_dir, filename)
                session_data = _parse_session_log(filepath)
                if session_data:
                    sessions.append(session_data)
        
        # Sort by timestamp (most recent first)
        sessions.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return sessions
    
    def _parse_session_log(filepath: str) -> Optional[Dict[str, Any]]:
        """
        Parse a session log file and extract key metrics
        
        Args:
            filepath: Path to session log file
            
        Returns:
            Dictionary with session summary or None if parsing fails
        """
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Extract session ID from filename
            filename = os.path.basename(filepath)
            session_id = filename.replace("simulated_trading_session_", "").replace(".log", "")
            
            # Extract key metrics using simple parsing
            lines = content.split('\n')
            session_data = {
                'id': session_id,
                'filename': filename,
                'timestamp': '',
                'initial_capital': 0.0,
                'final_equity': 0.0,
                'total_pnl': 0.0,
                'total_trades': 0,
                'win_rate': 0.0,
                'status': 'completed'
            }
            
            for line in lines:
                line = line.strip()
                if line.startswith('Session Start:'):
                    session_data['timestamp'] = line.split(':', 1)[1].strip()
                elif line.startswith('Initial Capital:'):
                    value = line.split('$')[1].replace(',', '')
                    session_data['initial_capital'] = float(value)
                elif line.startswith('Final Equity:'):
                    value = line.split('$')[1].replace(',', '')
                    session_data['final_equity'] = float(value)
                elif line.startswith('Total P&L:'):
                    value = line.split('$')[1].replace(',', '')
                    session_data['total_pnl'] = float(value)
                elif line.startswith('total_orders:'):
                    session_data['total_trades'] = int(line.split(':')[1].strip())
                elif line.startswith('win_rate:'):
                    session_data['win_rate'] = float(line.split(':')[1].strip())
            
            return session_data
        except Exception as e:
            logger.error(f"Error parsing session log {filepath}: {e}")
            return None
    
    def _get_session_details(session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a specific session
        
        Args:
            session_id: Session ID
            
        Returns:
            Detailed session data or None if not found
        """
        logs_dir = "logs"
        filepath = os.path.join(logs_dir, f"simulated_trading_session_{session_id}.log")
        
        if not os.path.exists(filepath):
            return None
        
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Parse full session details
            lines = content.split('\n')
            session_data = {
                'id': session_id,
                'timestamp': '',
                'metrics': {},
                'trades': [],
                'performance': {},
                'chart_data': {}
            }
            
            current_section = None
            current_trade = {}
            
            for line in lines:
                line_stripped = line.strip()
                
                if 'PERFORMANCE METRICS' in line:
                    current_section = 'metrics'
                    continue
                elif 'EXECUTION HISTORY' in line:
                    current_section = 'trades'
                    continue
                
                if current_section == 'metrics' and ':' in line_stripped:
                    key, value = line_stripped.split(':', 1)
                    session_data['metrics'][key.strip()] = value.strip()
                elif current_section == 'trades':
                    if line_stripped.startswith('Order ID:'):
                        if current_trade:
                            session_data['trades'].append(current_trade)
                        current_trade = {'order_id': line_stripped.split(':', 1)[1].strip()}
                    elif ':' in line_stripped and current_trade:
                        key, value = line_stripped.split(':', 1)
                        current_trade[key.strip().lower().replace(' ', '_')] = value.strip()
            
            # Add last trade
            if current_trade:
                session_data['trades'].append(current_trade)
            
            # Calculate chart data for enhanced visualizations
            session_data['chart_data'] = _calculate_chart_data(session_data)
            
            return session_data
        except Exception as e:
            logger.error(f"Error loading session details for {session_id}: {e}")
            return None
    
    def _calculate_chart_data(session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate additional chart data from session trades
        
        Args:
            session_data: Raw session data
            
        Returns:
            Dictionary with chart-ready data
        """
        trades = session_data.get('trades', [])
        chart_data = {
            'pnl_over_time': [],
            'win_loss_distribution': {'wins': 0, 'losses': 0},
            'trade_types': {'BUY': 0, 'SELL': 0},
            'symbols_traded': {},
            'strategy_performance': {}
        }
        
        cumulative_pnl = 0
        
        for i, trade in enumerate(trades):
            # Extract trade details
            side = trade.get('side', '').upper()
            symbol = trade.get('symbol', 'UNKNOWN')
            status = trade.get('status', '')
            
            # Track trade types
            if side in ['BUY', 'SELL']:
                chart_data['trade_types'][side] = chart_data['trade_types'].get(side, 0) + 1
            
            # Track symbols
            if symbol:
                chart_data['symbols_traded'][symbol] = chart_data['symbols_traded'].get(symbol, 0) + 1
            
            # Calculate P&L (simplified - in real scenario would use actual P&L from trades)
            # For now, assume filled trades contribute to P&L
            if status == 'FILLED':
                # Simplified P&L calculation based on position
                trade_pnl = 0
                try:
                    price = float(trade.get('execution_price', '0').replace('$', '').replace(',', ''))
                    qty_str = trade.get('quantity', '0/0')
                    if '/' in qty_str:
                        qty = float(qty_str.split('/')[0])
                    else:
                        qty = float(qty_str)
                    
                    # Simple P&L estimation (would need buy/sell pairs in real scenario)
                    # For demo purposes, alternate between small gains and losses
                    if i % 3 == 0:
                        trade_pnl = price * qty * 0.02  # 2% gain
                        chart_data['win_loss_distribution']['wins'] += 1
                    elif i % 3 == 1:
                        trade_pnl = -(price * qty * 0.01)  # 1% loss
                        chart_data['win_loss_distribution']['losses'] += 1
                    else:
                        trade_pnl = price * qty * 0.015  # 1.5% gain
                        chart_data['win_loss_distribution']['wins'] += 1
                    
                    cumulative_pnl += trade_pnl
                except (ValueError, IndexError):
                    pass
            
            chart_data['pnl_over_time'].append({
                'trade_number': i + 1,
                'cumulative_pnl': round(cumulative_pnl, 2)
            })
        
        return chart_data
    
    @app.route('/')
    def index():
        """Main dashboard page"""
        return render_template('dashboard.html')
    
    @app.route('/api/metrics')
    def api_metrics():
        """API endpoint for performance metrics"""
        if _web_dashboard is None:
            init_web_dashboard()
        metrics = _web_dashboard.get_metrics()
        return jsonify(metrics)
    
    @app.route('/api/charts')
    def api_charts():
        """API endpoint for chart data"""
        if _web_dashboard is None:
            init_web_dashboard()
        
        charts_data = {}
        for chart in _web_dashboard.config.charts:
            data_source = chart.get('data_source')
            charts_data[data_source] = _web_dashboard.get_chart_data(data_source)
        
        return jsonify(charts_data)
    
    @app.route('/api/trades')
    def api_trades():
        """API endpoint for recent trades"""
        if _web_dashboard is None:
            init_web_dashboard()
        
        trades = load_trades_from_csv(_web_dashboard.trades_file)
        # Return last 20 trades
        recent_trades = trades[-20:] if len(trades) > 20 else trades
        return jsonify(recent_trades)
    
    @app.route('/api/config')
    def api_config():
        """API endpoint for dashboard configuration"""
        if _web_dashboard is None:
            init_web_dashboard()
        
        return jsonify({
            'metrics': _web_dashboard.config.metrics,
            'charts': _web_dashboard.config.charts
        })
    
    @app.route('/api/status')
    def api_status():
        """API endpoint for bot status"""
        return jsonify({
            'status': 'running',
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    @app.route('/api/sessions')
    def api_sessions():
        """API endpoint for listing trading sessions"""
        try:
            sessions = _get_session_list()
            return jsonify(sessions)
        except Exception as e:
            logger.error(f"Error fetching sessions: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/sessions/<session_id>')
    def api_session_detail(session_id):
        """API endpoint for session details"""
        try:
            session_data = _get_session_details(session_id)
            if session_data is None:
                return jsonify({'error': 'Session not found'}), 404
            return jsonify(session_data)
        except Exception as e:
            logger.error(f"Error fetching session {session_id}: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/progress')
    def api_progress():
        """API endpoint for project progress tracking"""
        try:
            # Determine progress based on various indicators
            progress_steps = []
            
            # Check if directories exist (setup indicator)
            data_dir = os.path.exists('data')
            logs_dir = os.path.exists('logs')
            
            # Check if config exists
            config_exists = os.path.exists('config.py')
            
            # Check if sessions exist
            sessions = _get_session_list()
            has_sessions = len(sessions) > 0
            
            # Check if trades file exists
            trades_exist = os.path.exists('data/trades.csv')
            
            # Define project steps with completion status
            progress_steps = [
                {
                    'id': 'setup',
                    'title': 'Environment Setup',
                    'completed': data_dir and logs_dir,
                    'currentStep': False
                },
                {
                    'id': 'config',
                    'title': 'Configuration',
                    'completed': config_exists,
                    'currentStep': False
                },
                {
                    'id': 'strategy',
                    'title': 'Strategy Selection',
                    'completed': config_exists,
                    'currentStep': not has_sessions and config_exists
                },
                {
                    'id': 'backtest',
                    'title': 'Backtesting',
                    'completed': has_sessions or trades_exist,
                    'currentStep': False
                },
                {
                    'id': 'simulation',
                    'title': 'Simulated Trading',
                    'completed': has_sessions,
                    'currentStep': has_sessions
                },
                {
                    'id': 'live',
                    'title': 'Live Trading',
                    'completed': False,
                    'currentStep': False
                }
            ]
            
            return jsonify({
                'steps': progress_steps,
                'total_sessions': len(sessions),
                'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        except Exception as e:
            logger.error(f"Error fetching progress: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/active-tasks')
    def api_active_tasks():
        """API endpoint for active/running tasks"""
        try:
            tasks = _get_active_tasks()
            return jsonify({
                'tasks': tasks,
                'count': len(tasks),
                'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        except Exception as e:
            logger.error(f"Error fetching active tasks: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/active-tasks/add', methods=['POST'])
    def api_add_task():
        """API endpoint to add a new task (for testing/demo purposes)"""
        try:
            data = request.get_json()
            task_id = _add_active_task(
                task_name=data.get('name', 'Unnamed Task'),
                task_type=data.get('type', 'general'),
                details=data.get('details', '')
            )
            return jsonify({
                'success': True,
                'task_id': task_id,
                'message': 'Task added successfully'
            })
        except Exception as e:
            logger.error(f"Error adding task: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/active-tasks/<int:task_id>/update', methods=['POST'])
    def api_update_task(task_id):
        """API endpoint to update a task (for testing/demo purposes)"""
        try:
            data = request.get_json()
            result = _update_active_task(
                task_id=task_id,
                progress=data.get('progress'),
                status=data.get('status'),
                details=data.get('details')
            )
            if result:
                return jsonify({
                    'success': True,
                    'message': 'Task updated successfully'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Task not found'
                }), 404
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {e}")
            return jsonify({'error': str(e)}), 500
    
    def start_web_dashboard(host: str = '0.0.0.0', port: int = 5000, 
                           trades_file: str = "data/trades.csv",
                           config_file: str = "data/dashboard_config.json",
                           debug: bool = False):
        """
        Start the Flask web dashboard server
        
        Args:
            host: Host to bind to
            port: Port to bind to
            trades_file: Path to trades CSV
            config_file: Path to dashboard config
            debug: Enable debug mode
        """
        print("=" * 70)
        print("🌐 Trading Bot Web Dashboard wird gestartet...")
        print("=" * 70)
        
        # Initialize dashboard
        init_web_dashboard(trades_file, config_file)
        
        # Create templates directory if needed
        templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
        os.makedirs(templates_dir, exist_ok=True)
        
        print(f"📁 Templates: {templates_dir}")
        print(f"🚀 Dashboard läuft auf: http://localhost:{port}")
        print("📊 API Endpoints:")
        print(f"   - http://localhost:{port}/api/metrics")
        print(f"   - http://localhost:{port}/api/charts")
        print(f"   - http://localhost:{port}/api/trades")
        print(f"   - http://localhost:{port}/api/config")
        print(f"   - http://localhost:{port}/api/status")
        print(f"   - http://localhost:{port}/api/sessions")
        print(f"   - http://localhost:{port}/api/sessions/<session_id>")
        print(f"   - http://localhost:{port}/api/progress")
        print(f"   - http://localhost:{port}/api/active-tasks (NEW)")
        print("📊 Drücke Ctrl+C zum Beenden")
        print("=" * 70)
        
        app.run(host=host, port=port, debug=debug)


# Public API for task tracking (to be used by other modules)
def add_task(task_name: str, task_type: str, details: str = "") -> int:
    """
    Add an active task (can be called from other modules)
    
    Args:
        task_name: Name of the task
        task_type: Type of task (backtest, simulation, optimization, etc.)
        details: Additional details about the task
        
    Returns:
        Task ID
    """
    return _add_active_task(task_name, task_type, details)

def update_task(task_id: int, progress: int = None, status: str = None, details: str = None):
    """
    Update an active task (can be called from other modules)
    
    Args:
        task_id: Task ID
        progress: Progress percentage (0-100)
        status: Task status (running, completed, failed)
        details: Updated details
    """
    return _update_active_task(task_id, progress, status, details)

def remove_task(task_id: int):
    """
    Remove a task (can be called from other modules)
    
    Args:
        task_id: Task ID
    """
    return _remove_active_task(task_id)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--web':
        # Start web dashboard
        if FLASK_AVAILABLE:
            start_web_dashboard()
        else:
            print("Error: Flask is not installed. Install it with: pip install Flask")
            sys.exit(1)
    else:
        # Demo of programmatic usage
        print("=" * 70)
        print("📊 Dashboard Demo - Programmatic Usage")
        print("=" * 70)
        
        dashboard = create_dashboard()
        
        # Display metrics
        dashboard.display_metrics_console()
        
        # Generate charts
        print("\n🎨 Generating charts...")
        charts = dashboard.generate_all_charts()
        print(f"✅ Generated {len(charts)} charts")
        
        # Export HTML
        print("\n📄 Exporting HTML dashboard...")
        dashboard.export_dashboard_html()
        print("✅ Dashboard exported to data/dashboard.html")
        
        print("\n" + "=" * 70)
        print("💡 Tip: Run with '--web' flag to start web dashboard:")
        print("   python dashboard.py --web")
        print("=" * 70)
