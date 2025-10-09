"""
dashboard_examples.py - Dashboard Usage Examples
===============================================
Demonstrates various ways to use the Visual Dashboard
"""
from dashboard import create_dashboard, DashboardModal, DashboardConfig
from utils import save_trades_to_csv
import os


def example_1_basic_usage():
    """Example 1: Basic dashboard usage"""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Basic Dashboard Usage")
    print("=" * 70)
    
    # Create dashboard
    dashboard = create_dashboard()
    
    # Display metrics in console
    print("\n📊 Current Metrics:")
    dashboard.display_metrics_console()
    
    print("\n✓ Example 1 complete")


def example_2_export_dashboard():
    """Example 2: Export dashboard to HTML"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Export Dashboard to HTML")
    print("=" * 70)
    
    dashboard = create_dashboard()
    
    # Export to custom location
    output_file = "data/my_dashboard.html"
    dashboard.export_dashboard_html(output_file)
    
    if os.path.exists(output_file):
        size = os.path.getsize(output_file) / 1024
        print(f"\n✓ Dashboard exported to {output_file} ({size:.1f} KB)")
    
    print("✓ Example 2 complete")


def example_3_generate_charts():
    """Example 3: Generate various chart types"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Generate Charts")
    print("=" * 70)
    
    dashboard = create_dashboard()
    
    # Generate interactive Plotly charts
    print("\n📊 Generating Plotly charts...")
    plotly_charts = dashboard.generate_all_charts(
        output_dir="data/charts",
        use_plotly=True
    )
    print(f"✓ Generated {len(plotly_charts)} Plotly chart(s)")
    
    # Generate static Matplotlib charts
    print("\n📊 Generating Matplotlib charts...")
    matplotlib_charts = dashboard.generate_all_charts(
        output_dir="data/charts",
        use_plotly=False
    )
    print(f"✓ Generated {len(matplotlib_charts)} Matplotlib chart(s)")
    
    print("\n✓ Example 3 complete")


def example_4_modal_management():
    """Example 4: Using modal to manage configuration"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Modal Management")
    print("=" * 70)
    
    dashboard = create_dashboard()
    modal = DashboardModal(dashboard)
    
    print("\nInitial configuration:")
    print(f"  Metrics: {dashboard.config.metrics}")
    print(f"  Charts: {len(dashboard.config.charts)}")
    
    # Open modal
    modal.open()
    print("\n✓ Modal opened")
    
    # Add custom metric
    modal.add_metric('sharpe_ratio')
    print("✓ Added 'sharpe_ratio' metric")
    
    # Add custom chart
    modal.add_chart('line', 'Sharpe Ratio Over Time', 'pnl_history')
    print("✓ Added 'Sharpe Ratio' chart")
    
    # Close modal
    modal.close()
    print("✓ Modal closed")
    
    print("\nUpdated configuration:")
    print(f"  Metrics: {dashboard.config.metrics}")
    print(f"  Charts: {len(dashboard.config.charts)}")
    
    print("\n✓ Example 4 complete")


def example_5_custom_configuration():
    """Example 5: Custom dashboard configuration"""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Custom Configuration")
    print("=" * 70)
    
    # Create custom config
    config_file = "data/custom_dashboard_config.json"
    config = DashboardConfig(config_file)
    
    # Customize metrics
    config.metrics = ['total_pnl', 'win_rate', 'total_trades']
    
    # Customize charts
    config.charts = [
        {'type': 'line', 'title': 'P&L Trend', 'data_source': 'pnl_history'},
        {'type': 'pie', 'title': 'Win/Loss', 'data_source': 'win_loss'}
    ]
    
    # Save configuration
    config.save_config()
    print(f"✓ Custom configuration saved to {config_file}")
    
    # Create dashboard with custom config
    dashboard = create_dashboard(config_file=config_file)
    print("✓ Dashboard created with custom configuration")
    
    print("\n✓ Example 5 complete")


def example_6_get_chart_data():
    """Example 6: Access raw chart data"""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Access Raw Chart Data")
    print("=" * 70)
    
    dashboard = create_dashboard()
    
    # Get P&L history data
    print("\n📈 P&L History Data:")
    pnl_data = dashboard.get_chart_data('pnl_history')
    print(f"  Timestamps: {len(pnl_data['timestamps'])} entries")
    print(f"  P&L values: {len(pnl_data['pnl'])} entries")
    if pnl_data['pnl']:
        print(f"  Last P&L: ${pnl_data['pnl'][-1]:.2f}")
    
    # Get strategy statistics
    print("\n📊 Strategy Statistics:")
    strategy_data = dashboard.get_chart_data('strategy_stats')
    print(f"  Strategies: {strategy_data['strategies']}")
    print(f"  Trade counts: {strategy_data['counts']}")
    
    # Get win/loss distribution
    print("\n🎯 Win/Loss Distribution:")
    win_loss_data = dashboard.get_chart_data('win_loss')
    print(f"  Labels: {win_loss_data['labels']}")
    print(f"  Values: {win_loss_data['values']}")
    
    print("\n✓ Example 6 complete")


def example_7_programmatic_metrics():
    """Example 7: Get metrics programmatically"""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Programmatic Metrics Access")
    print("=" * 70)
    
    dashboard = create_dashboard()
    
    # Get metrics as dictionary
    metrics = dashboard.get_metrics()
    
    print("\n📊 Metrics Dictionary:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")
    
    # Use metrics for decision making
    if metrics.get('win_rate', 0) > 50:
        print("\n✅ Good performance! Win rate above 50%")
    else:
        print("\n⚠️ Performance needs improvement")
    
    if metrics.get('total_pnl', 0) > 0:
        print("✅ Profitable overall")
    else:
        print("⚠️ Currently unprofitable")
    
    print("\n✓ Example 7 complete")


def example_8_modal_query_options():
    """Example 8: Query available options from modal"""
    print("\n" + "=" * 70)
    print("EXAMPLE 8: Query Available Options")
    print("=" * 70)
    
    dashboard = create_dashboard()
    modal = DashboardModal(dashboard)
    
    # Get available metrics
    print("\n📊 Available Metrics:")
    for metric in modal.get_available_metrics():
        print(f"  - {metric}")
    
    # Get available chart types
    print("\n📈 Available Chart Types:")
    for chart_type in modal.get_available_chart_types():
        print(f"  - {chart_type}")
    
    # Get available data sources
    print("\n📁 Available Data Sources:")
    for source in modal.get_available_data_sources():
        print(f"  - {source}")
    
    print("\n✓ Example 8 complete")


def example_9_create_custom_trades():
    """Example 9: Create custom trade data and visualize"""
    print("\n" + "=" * 70)
    print("EXAMPLE 9: Custom Trade Data")
    print("=" * 70)
    
    # Create custom trades
    custom_trades = [
        {
            'timestamp': '2024-01-01T09:00:00',
            'symbol': 'ETH/USDT',
            'order_type': 'BUY',
            'price': '2000.00',
            'quantity': 50,
            'triggering_strategies': 'macd, rsi',
            'capital': '5000.00',
            'pnl': '0.00'
        },
        {
            'timestamp': '2024-01-01T10:00:00',
            'symbol': 'ETH/USDT',
            'order_type': 'SELL',
            'price': '2100.00',
            'quantity': 50,
            'triggering_strategies': 'macd, rsi',
            'capital': '5500.00',
            'pnl': '500.00'
        }
    ]
    
    # Save to custom file
    custom_trades_file = "data/custom_trades.csv"
    save_trades_to_csv(custom_trades, custom_trades_file)
    print(f"✓ Created custom trades in {custom_trades_file}")
    
    # Create dashboard with custom trades
    dashboard = create_dashboard(
        trades_file=custom_trades_file,
        config_file="data/custom_config.json"
    )
    
    # Display metrics
    print("\n📊 Custom Trades Metrics:")
    dashboard.display_metrics_console()
    
    print("\n✓ Example 9 complete")


def example_10_integration_pattern():
    """Example 10: Dashboard integration pattern"""
    print("\n" + "=" * 70)
    print("EXAMPLE 10: Integration Pattern")
    print("=" * 70)
    
    print("""
Integration pattern for trading bot:

class TradingBot:
    def __init__(self):
        # ... bot initialization ...
        
        # Add dashboard
        self.dashboard = create_dashboard()
        self.dashboard_modal = DashboardModal(self.dashboard)
    
    def on_trade_complete(self):
        # Update dashboard after each trade
        self.dashboard.display_metrics_console()
    
    def on_shutdown(self):
        # Export dashboard on shutdown
        self.dashboard.export_dashboard_html()
        self.dashboard.generate_all_charts()
    
    def configure_dashboard(self):
        # Allow user to configure dashboard
        self.dashboard_modal.open()
        # ... user interaction ...
        self.dashboard_modal.close()
    """)
    
    print("\n✓ Example 10 complete")


def run_all_examples():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("🚀 DASHBOARD USAGE EXAMPLES")
    print("=" * 70)
    
    examples = [
        example_1_basic_usage,
        example_2_export_dashboard,
        example_3_generate_charts,
        example_4_modal_management,
        example_5_custom_configuration,
        example_6_get_chart_data,
        example_7_programmatic_metrics,
        example_8_modal_query_options,
        example_9_create_custom_trades,
        example_10_integration_pattern
    ]
    
    for i, example in enumerate(examples, 1):
        try:
            example()
        except Exception as e:
            print(f"\n❌ Error in example {i}: {e}")
    
    print("\n" + "=" * 70)
    print("✅ ALL EXAMPLES COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    run_all_examples()
