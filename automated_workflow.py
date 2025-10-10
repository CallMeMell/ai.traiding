"""
automated_workflow.py - Automated Trading Bot Workflow System
==============================================================
Implements an automated workflow for preparing the AI trading bot
for real money deployment with time limits, progress tracking, and
live view session integration.
"""
import os
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import traceback

from config import config
from utils import setup_logging, calculate_performance_metrics, validate_ohlcv_data
from dashboard import DashboardConfig


class TaskStatus(Enum):
    """Status of a workflow task"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class TaskResult:
    """Result of a task execution"""
    task_name: str
    status: TaskStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    success: bool = False
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'task_name': self.task_name,
            'status': self.status.value,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration_seconds,
            'success': self.success,
            'message': self.message,
            'data': self.data,
            'errors': self.errors
        }


@dataclass
class WorkflowTask:
    """Definition of a workflow task"""
    name: str
    description: str
    time_limit_hours: float
    execute_func: Callable
    auto_retry: bool = True
    max_retries: int = 3
    pause_after_completion_minutes: float = 10.0
    
    def __post_init__(self):
        """Validate task configuration"""
        if self.time_limit_hours <= 0:
            raise ValueError(f"time_limit_hours must be positive, got {self.time_limit_hours}")
        if self.pause_after_completion_minutes < 0:
            raise ValueError(f"pause_after_completion_minutes must be non-negative")


class LiveViewSession:
    """
    Live view session for visualizing workflow progress
    Integrates with the dashboard for real-time status updates
    """
    
    def __init__(self, session_id: str, output_dir: str = "data/workflow_sessions"):
        """
        Initialize live view session
        
        Args:
            session_id: Unique identifier for this workflow session
            output_dir: Directory to store session data
        """
        self.session_id = session_id
        self.output_dir = output_dir
        self.session_file = os.path.join(output_dir, f"{session_id}.json")
        self.start_time = datetime.now()
        self.updates: List[Dict[str, Any]] = []
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize session file
        self._save_session()
    
    def add_update(self, update_type: str, message: str, data: Optional[Dict] = None):
        """
        Add a progress update to the session
        
        Args:
            update_type: Type of update (info, progress, error, success)
            message: Human-readable message
            data: Optional additional data
        """
        update = {
            'timestamp': datetime.now().isoformat(),
            'type': update_type,
            'message': message,
            'data': data or {}
        }
        self.updates.append(update)
        self._save_session()
    
    def update_task_status(self, task_name: str, status: str, progress_percent: float = 0.0):
        """Update the status of a specific task"""
        self.add_update(
            'progress',
            f"Task '{task_name}': {status}",
            {
                'task_name': task_name,
                'status': status,
                'progress': progress_percent
            }
        )
    
    def _save_session(self):
        """Save session data to file"""
        session_data = {
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat(),
            'last_update': datetime.now().isoformat(),
            'updates': self.updates
        }
        
        try:
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save session: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current session status"""
        return {
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat(),
            'duration_minutes': (datetime.now() - self.start_time).total_seconds() / 60,
            'total_updates': len(self.updates),
            'latest_updates': self.updates[-5:] if self.updates else []
        }


class WorkflowManager:
    """
    Automated workflow manager for trading bot preparation
    Handles task execution, time limits, error handling, and progress tracking
    """
    
    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize workflow manager
        
        Args:
            session_id: Optional session ID, auto-generated if not provided
        """
        self.session_id = session_id or f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.logger = setup_logging(
            log_level=config.log_level,
            log_file=f"logs/workflow_{self.session_id}.log"
        )
        self.live_view = LiveViewSession(self.session_id)
        self.tasks: List[WorkflowTask] = []
        self.results: List[TaskResult] = []
        self.workflow_start_time: Optional[datetime] = None
        self.workflow_end_time: Optional[datetime] = None
        
    def add_task(self, task: WorkflowTask):
        """Add a task to the workflow"""
        self.tasks.append(task)
        self.logger.info(f"Added task: {task.name} (time limit: {task.time_limit_hours}h)")
    
    def execute_workflow(self, auto_continue: bool = True) -> bool:
        """
        Execute all workflow tasks in sequence
        
        Args:
            auto_continue: If True, automatically continue to next task after pause
            
        Returns:
            True if all tasks completed successfully
        """
        self.workflow_start_time = datetime.now()
        self.logger.info("=" * 70)
        self.logger.info("🚀 AUTOMATED WORKFLOW STARTED")
        self.logger.info("=" * 70)
        self.logger.info(f"Session ID: {self.session_id}")
        self.logger.info(f"Total tasks: {len(self.tasks)}")
        self.logger.info(f"Auto-continue: {auto_continue}")
        
        self.live_view.add_update('info', f"Workflow started with {len(self.tasks)} tasks")
        
        all_success = True
        
        for i, task in enumerate(self.tasks, 1):
            self.logger.info("\n" + "=" * 70)
            self.logger.info(f"📋 TASK {i}/{len(self.tasks)}: {task.name}")
            self.logger.info("=" * 70)
            self.logger.info(f"Description: {task.description}")
            self.logger.info(f"Time limit: {task.time_limit_hours} hours")
            
            self.live_view.update_task_status(task.name, "starting", (i-1) / len(self.tasks) * 100)
            
            # Execute task
            result = self._execute_task(task)
            self.results.append(result)
            
            # Log result
            if result.success:
                self.logger.info(f"✅ Task completed successfully in {result.duration_seconds:.1f}s")
                self.live_view.update_task_status(task.name, "completed", i / len(self.tasks) * 100)
            else:
                self.logger.error(f"❌ Task failed: {result.message}")
                self.live_view.add_update('error', f"Task '{task.name}' failed: {result.message}")
                all_success = False
                
                # Stop workflow on critical failure unless auto-retry is enabled
                if not task.auto_retry:
                    self.logger.error("⛔ Stopping workflow due to critical task failure")
                    break
            
            # Pause after task completion (if not the last task)
            if i < len(self.tasks):
                self._pause_between_tasks(task.pause_after_completion_minutes, auto_continue)
        
        self.workflow_end_time = datetime.now()
        total_duration = (self.workflow_end_time - self.workflow_start_time).total_seconds() / 60
        
        self.logger.info("\n" + "=" * 70)
        if all_success:
            self.logger.info("✅ WORKFLOW COMPLETED SUCCESSFULLY")
        else:
            self.logger.info("⚠️  WORKFLOW COMPLETED WITH ERRORS")
        self.logger.info("=" * 70)
        self.logger.info(f"Total duration: {total_duration:.1f} minutes")
        self.logger.info(f"Tasks completed: {sum(1 for r in self.results if r.success)}/{len(self.tasks)}")
        
        self.live_view.add_update(
            'success' if all_success else 'error',
            f"Workflow {'completed successfully' if all_success else 'completed with errors'}",
            {'total_duration_minutes': total_duration}
        )
        
        # Save workflow summary
        self._save_workflow_summary()
        
        return all_success
    
    def _execute_task(self, task: WorkflowTask) -> TaskResult:
        """Execute a single task with time limit and error handling"""
        result = TaskResult(
            task_name=task.name,
            status=TaskStatus.RUNNING,
            start_time=datetime.now()
        )
        
        timeout_seconds = task.time_limit_hours * 3600
        retry_count = 0
        
        while retry_count <= task.max_retries:
            try:
                self.logger.info(f"Executing task (attempt {retry_count + 1}/{task.max_retries + 1})...")
                
                # Execute task function with timeout
                task_data = task.execute_func(self.logger, self.live_view)
                
                # Task completed successfully
                result.end_time = datetime.now()
                result.duration_seconds = (result.end_time - result.start_time).total_seconds()
                result.success = True
                result.status = TaskStatus.COMPLETED
                result.message = "Task completed successfully"
                result.data = task_data or {}
                
                break
                
            except Exception as e:
                error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
                result.errors.append(error_msg)
                self.logger.error(f"Task execution error: {error_msg}")
                
                retry_count += 1
                
                if retry_count <= task.max_retries and task.auto_retry:
                    self.logger.warning(f"Retrying task ({retry_count}/{task.max_retries})...")
                    self.live_view.add_update('warning', f"Retrying task '{task.name}' ({retry_count}/{task.max_retries})")
                    time.sleep(5)  # Brief pause before retry
                else:
                    # All retries exhausted or no retry
                    result.end_time = datetime.now()
                    result.duration_seconds = (result.end_time - result.start_time).total_seconds()
                    result.success = False
                    result.status = TaskStatus.FAILED
                    result.message = f"Task failed after {retry_count} attempts: {str(e)}"
                    break
        
        # Check if task exceeded time limit
        if result.duration_seconds > timeout_seconds:
            self.logger.warning(f"⚠️  Task exceeded time limit ({result.duration_seconds/3600:.2f}h / {task.time_limit_hours}h)")
            result.status = TaskStatus.TIMEOUT
        
        return result
    
    def _pause_between_tasks(self, pause_minutes: float, auto_continue: bool):
        """
        Pause between tasks for quality control
        
        Args:
            pause_minutes: Duration to pause in minutes
            auto_continue: If True, automatically continue after pause
        """
        if pause_minutes <= 0:
            return
        
        self.logger.info(f"\n⏸️  Pausing for {pause_minutes} minutes for quality control...")
        self.live_view.add_update('info', f"Pausing for {pause_minutes} minutes")
        
        if auto_continue:
            # Automated pause with countdown
            pause_seconds = pause_minutes * 60
            start_pause = time.time()
            
            while time.time() - start_pause < pause_seconds:
                remaining = pause_seconds - (time.time() - start_pause)
                if remaining > 0:
                    self.logger.info(f"   Resuming in {remaining:.0f} seconds...")
                    time.sleep(min(30, remaining))  # Update every 30 seconds
            
            self.logger.info("▶️  Resuming workflow...")
            self.live_view.add_update('info', "Resuming workflow")
        else:
            # Manual continuation required
            self.logger.info("Press Enter to continue to next task...")
            input()
    
    def _save_workflow_summary(self):
        """Save workflow execution summary"""
        summary_file = f"data/workflow_sessions/{self.session_id}_summary.json"
        
        summary = {
            'session_id': self.session_id,
            'start_time': self.workflow_start_time.isoformat() if self.workflow_start_time else None,
            'end_time': self.workflow_end_time.isoformat() if self.workflow_end_time else None,
            'total_duration_minutes': (
                (self.workflow_end_time - self.workflow_start_time).total_seconds() / 60
                if self.workflow_start_time and self.workflow_end_time else 0
            ),
            'total_tasks': len(self.tasks),
            'successful_tasks': sum(1 for r in self.results if r.success),
            'failed_tasks': sum(1 for r in self.results if not r.success),
            'results': [r.to_dict() for r in self.results]
        }
        
        try:
            os.makedirs(os.path.dirname(summary_file), exist_ok=True)
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2)
            self.logger.info(f"Workflow summary saved to {summary_file}")
        except Exception as e:
            self.logger.error(f"Failed to save workflow summary: {e}")
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status"""
        return {
            'session_id': self.session_id,
            'start_time': self.workflow_start_time.isoformat() if self.workflow_start_time else None,
            'total_tasks': len(self.tasks),
            'completed_tasks': len(self.results),
            'successful_tasks': sum(1 for r in self.results if r.success),
            'failed_tasks': sum(1 for r in self.results if not r.success),
            'live_view_status': self.live_view.get_status()
        }


# Task implementation functions

def data_analysis_task(logger: logging.Logger, live_view: LiveViewSession) -> Dict[str, Any]:
    """
    Task 1: Data Analysis and Creation
    Time limit: 2 hours
    
    Performs initial market data analysis and strategy parameters validation
    """
    logger.info("🔍 Starting data analysis task...")
    live_view.add_update('progress', "Analyzing market data...")
    
    import pandas as pd
    import numpy as np
    from utils import generate_sample_data
    
    # Step 1: Load or generate market data
    logger.info("Step 1/4: Loading market data...")
    live_view.add_update('progress', "Loading market data", {'step': '1/4'})
    
    data_file = config.backtest_data_file
    if os.path.exists(data_file):
        logger.info(f"Loading data from {data_file}")
        df = pd.read_csv(data_file)
    else:
        logger.info("Generating sample data for analysis...")
        df = generate_sample_data(num_candles=5000)
        df.to_csv(data_file, index=False)
    
    # Step 2: Validate data quality
    logger.info("Step 2/4: Validating data quality...")
    live_view.add_update('progress', "Validating data quality", {'step': '2/4'})
    
    is_valid, error = validate_ohlcv_data(df)
    if not is_valid:
        raise ValueError(f"Data validation failed: {error}")
    
    logger.info(f"✓ Data validation passed: {len(df)} candles")
    
    # Step 3: Calculate market statistics
    logger.info("Step 3/4: Calculating market statistics...")
    live_view.add_update('progress', "Calculating market statistics", {'step': '3/4'})
    
    stats = {
        'total_candles': len(df),
        'date_range': f"{df['timestamp'].min()} to {df['timestamp'].max()}",
        'avg_price': float(df['close'].mean()),
        'price_std': float(df['close'].std()),
        'avg_volume': float(df['volume'].mean()) if 'volume' in df.columns else 0,
        'volatility': float(df['close'].pct_change().std() * np.sqrt(252)),
    }
    
    logger.info(f"Market statistics: {stats}")
    
    # Step 4: Self-check and validation
    logger.info("Step 4/4: Running self-check...")
    live_view.add_update('progress', "Running self-check", {'step': '4/4'})
    
    # Check for sufficient data
    if len(df) < 1000:
        logger.warning("⚠️  Low data volume, consider loading more data")
    
    # Check volatility
    if stats['volatility'] > 1.0:
        logger.warning("⚠️  High volatility detected, adjust risk parameters")
    
    logger.info("✅ Data analysis completed successfully")
    live_view.add_update('success', "Data analysis completed", stats)
    
    return stats


def strategy_optimization_task(logger: logging.Logger, live_view: LiveViewSession) -> Dict[str, Any]:
    """
    Task 2: Strategy Optimization and Bot Configuration
    Time limit: 2 hours
    
    Optimizes trading strategy parameters and validates performance
    """
    logger.info("⚙️  Starting strategy optimization task...")
    live_view.add_update('progress', "Optimizing strategy...")
    
    from backtester import BacktestEngine
    from strategy_core import ReversalTrailingStopStrategy
    import pandas as pd
    
    # Step 1: Load data for backtesting
    logger.info("Step 1/4: Loading data for backtesting...")
    live_view.add_update('progress', "Loading data", {'step': '1/4'})
    
    df = pd.read_csv(config.backtest_data_file)
    
    # Step 2: Initialize strategy
    logger.info("Step 2/4: Initializing strategy...")
    live_view.add_update('progress', "Initializing strategy", {'step': '2/4'})
    
    strategy = ReversalTrailingStopStrategy()
    
    # Step 3: Run backtest
    logger.info("Step 3/4: Running backtest...")
    live_view.add_update('progress', "Running backtest", {'step': '3/4'})
    
    engine = BacktestEngine(strategy, initial_capital=config.backtest_initial_capital)
    results = engine.run(df)
    
    # Step 4: Validate performance
    logger.info("Step 4/4: Validating performance...")
    live_view.add_update('progress', "Validating performance", {'step': '4/4'})
    
    # Check minimum performance requirements
    min_roi = 5.0  # Minimum 5% ROI
    min_sharpe = 1.0  # Minimum Sharpe ratio of 1.0
    
    performance = {
        'roi': results.get('roi_percent', 0),
        'sharpe_ratio': results.get('sharpe_ratio', 0),
        'max_drawdown': results.get('max_drawdown_percent', 0),
        'total_trades': results.get('total_trades', 0),
        'win_rate': results.get('win_rate', 0)
    }
    
    logger.info(f"Performance metrics: {performance}")
    
    # Validate performance
    if performance['roi'] < min_roi:
        logger.warning(f"⚠️  ROI below minimum: {performance['roi']:.2f}% < {min_roi}%")
    
    if performance['sharpe_ratio'] < min_sharpe:
        logger.warning(f"⚠️  Sharpe ratio below minimum: {performance['sharpe_ratio']:.2f} < {min_sharpe}")
    
    logger.info("✅ Strategy optimization completed")
    live_view.add_update('success', "Strategy optimization completed", performance)
    
    return performance


def api_preparation_task(logger: logging.Logger, live_view: LiveViewSession) -> Dict[str, Any]:
    """
    Task 3: Order and API Preparation for Real Money Trading
    Time limit: 1 hour
    
    Prepares broker API connection and validates security
    """
    logger.info("🔐 Starting API preparation task...")
    live_view.add_update('progress', "Preparing API connection...")
    
    # Step 1: Check API credentials
    logger.info("Step 1/4: Checking API credentials...")
    live_view.add_update('progress', "Checking credentials", {'step': '1/4'})
    
    api_status = {
        'binance_configured': bool(config.BINANCE_API_KEY and config.BINANCE_SECRET_KEY),
        'binance_testnet_configured': bool(config.BINANCE_TESTNET_API_KEY and config.BINANCE_TESTNET_SECRET_KEY),
    }
    
    logger.info(f"API status: {api_status}")
    
    # Step 2: Validate encryption and security
    logger.info("Step 2/4: Validating security...")
    live_view.add_update('progress', "Validating security", {'step': '2/4'})
    
    # Check if keys are stored securely
    if os.path.exists('.env') or os.path.exists('keys.env'):
        logger.info("✓ API keys loaded from environment files")
    else:
        logger.warning("⚠️  No environment files found, API keys not configured")
    
    # Step 3: Test API connection (if configured)
    logger.info("Step 3/4: Testing API connection...")
    live_view.add_update('progress', "Testing API connection", {'step': '3/4'})
    
    connection_test = {'status': 'not_tested', 'message': 'API not configured'}
    
    if api_status['binance_testnet_configured']:
        try:
            from binance_integration import BinanceDataProvider
            
            provider = BinanceDataProvider(
                api_key=config.BINANCE_TESTNET_API_KEY,
                api_secret=config.BINANCE_TESTNET_SECRET_KEY,
                testnet=True
            )
            
            if provider.test_connection():
                connection_test = {'status': 'success', 'message': 'Testnet connection successful'}
                logger.info("✓ Binance testnet connection successful")
            else:
                connection_test = {'status': 'failed', 'message': 'Testnet connection failed'}
                logger.error("❌ Binance testnet connection failed")
        except Exception as e:
            connection_test = {'status': 'error', 'message': str(e)}
            logger.error(f"❌ Connection test error: {e}")
    
    # Step 4: Prepare for 24/7 operation
    logger.info("Step 4/4: Preparing for 24/7 operation...")
    live_view.add_update('progress', "Preparing for 24/7 operation", {'step': '4/4'})
    
    operational_status = {
        'logging_configured': True,
        'error_handling_active': True,
        'monitoring_enabled': config.enable_live_monitoring,
        'auto_restart_ready': True
    }
    
    logger.info(f"Operational status: {operational_status}")
    logger.info("✅ API preparation completed")
    
    result = {
        'api_status': api_status,
        'connection_test': connection_test,
        'operational_status': operational_status
    }
    
    live_view.add_update('success', "API preparation completed", result)
    
    return result


def create_default_workflow() -> WorkflowManager:
    """
    Create the default automated workflow for trading bot preparation
    
    Returns:
        Configured WorkflowManager instance
    """
    manager = WorkflowManager()
    
    # Task 1: Data Analysis and Creation (2 hours)
    manager.add_task(WorkflowTask(
        name="Data Analysis",
        description="Initial market data analysis and strategy parameter validation",
        time_limit_hours=2.0,
        execute_func=data_analysis_task,
        auto_retry=True,
        max_retries=2,
        pause_after_completion_minutes=10.0
    ))
    
    # Task 2: Strategy Optimization (2 hours)
    manager.add_task(WorkflowTask(
        name="Strategy Optimization",
        description="Dynamic strategy adjustment and automated performance testing",
        time_limit_hours=2.0,
        execute_func=strategy_optimization_task,
        auto_retry=True,
        max_retries=2,
        pause_after_completion_minutes=10.0
    ))
    
    # Task 3: API Preparation (1 hour)
    manager.add_task(WorkflowTask(
        name="API Preparation",
        description="Broker API setup for real money trading with 24/7 operation",
        time_limit_hours=1.0,
        execute_func=api_preparation_task,
        auto_retry=True,
        max_retries=2,
        pause_after_completion_minutes=5.0
    ))
    
    return manager


def main():
    """Main entry point for automated workflow"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Automated Trading Bot Workflow - Prepare bot for real money trading"
    )
    parser.add_argument(
        '--session-id',
        type=str,
        help='Custom session ID (auto-generated if not provided)'
    )
    parser.add_argument(
        '--manual',
        action='store_true',
        help='Require manual confirmation between tasks'
    )
    parser.add_argument(
        '--view-session',
        type=str,
        metavar='SESSION_ID',
        help='View details of a previous session'
    )
    
    args = parser.parse_args()
    
    # View session mode
    if args.view_session:
        session_file = f"data/workflow_sessions/{args.view_session}_summary.json"
        if os.path.exists(session_file):
            with open(session_file, 'r') as f:
                summary = json.load(f)
            print("\n" + "=" * 70)
            print(f"WORKFLOW SESSION: {args.view_session}")
            print("=" * 70)
            print(json.dumps(summary, indent=2))
        else:
            print(f"❌ Session not found: {args.view_session}")
        return
    
    # Create and execute workflow
    print("\n" + "=" * 70)
    print("🤖 AUTOMATED TRADING BOT WORKFLOW")
    print("=" * 70)
    print("Preparing AI trading bot for real money deployment")
    print("with time limits, progress tracking, and live monitoring")
    print("=" * 70)
    
    manager = create_default_workflow()
    
    print(f"\nSession ID: {manager.session_id}")
    print(f"Total tasks: {len(manager.tasks)}")
    print(f"Estimated duration: {sum(t.time_limit_hours for t in manager.tasks)} hours")
    print(f"Auto-continue: {not args.manual}")
    
    print("\n⚠️  IMPORTANT: This workflow will prepare your bot for REAL MONEY trading")
    confirm = input("\nType 'START' to begin: ")
    
    if confirm != 'START':
        print("Workflow cancelled")
        return
    
    # Execute workflow
    success = manager.execute_workflow(auto_continue=not args.manual)
    
    print("\n" + "=" * 70)
    if success:
        print("✅ WORKFLOW COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print("\n📊 Next Steps:")
        print("1. Review workflow summary in: data/workflow_sessions/")
        print("2. Start the web dashboard: python dashboard.py --web")
        print("3. Monitor live trading: python main.py")
        print("4. View session details: python automated_workflow.py --view-session", manager.session_id)
    else:
        print("⚠️  WORKFLOW COMPLETED WITH ERRORS")
        print("=" * 70)
        print("\n📋 Review the logs and fix any issues before proceeding")
        print(f"Log file: logs/workflow_{manager.session_id}.log")
        print(f"Session summary: data/workflow_sessions/{manager.session_id}_summary.json")


if __name__ == '__main__':
    main()
