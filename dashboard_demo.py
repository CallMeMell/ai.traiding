"""
dashboard_demo.py - Demo script for Visual Dashboard
====================================================
Demonstrates the enhanced dashboard functionality
"""
import sys
import os
from dashboard import create_dashboard, DashboardModal
from utils import setup_logging

logger = None


def print_menu():
    """Display main menu"""
    print("\n" + "=" * 60)
    print("📊 VISUAL DASHBOARD DEMO")
    print("=" * 60)
    print("1. Display Metrics")
    print("2. Open Modal (Manage Metrics & Charts)")
    print("3. Generate Charts (Matplotlib)")
    print("4. Generate Charts (Plotly - Interactive)")
    print("5. Export Dashboard to HTML")
    print("6. Exit")
    print("=" * 60)


def modal_menu(modal: DashboardModal):
    """Display modal menu"""
    while modal.is_open:
        print("\n" + "=" * 60)
        print("🔧 DASHBOARD MODAL - Manage Metrics & Charts")
        print("=" * 60)
        print("1. View Current Metrics")
        print("2. Add Metric")
        print("3. Remove Metric")
        print("4. View Current Charts")
        print("5. Add Chart")
        print("6. Remove Chart")
        print("7. Close Modal")
        print("=" * 60)
        
        choice = input("Select option: ").strip()
        
        if choice == '1':
            print("\nCurrent Metrics:")
            for i, metric in enumerate(modal.dashboard.config.metrics, 1):
                print(f"  {i}. {metric}")
        
        elif choice == '2':
            print("\nAvailable Metrics:")
            available = modal.get_available_metrics()
            for i, metric in enumerate(available, 1):
                print(f"  {i}. {metric}")
            
            try:
                idx = int(input("Select metric number to add: ")) - 1
                if 0 <= idx < len(available):
                    modal.add_metric(available[idx])
                    print(f"✓ Added metric: {available[idx]}")
                else:
                    print("❌ Invalid selection")
            except (ValueError, IndexError):
                print("❌ Invalid input")
        
        elif choice == '3':
            current = modal.dashboard.config.metrics
            if not current:
                print("No metrics to remove")
                continue
            
            print("\nCurrent Metrics:")
            for i, metric in enumerate(current, 1):
                print(f"  {i}. {metric}")
            
            try:
                idx = int(input("Select metric number to remove: ")) - 1
                if 0 <= idx < len(current):
                    modal.remove_metric(current[idx])
                    print(f"✓ Removed metric: {current[idx]}")
                else:
                    print("❌ Invalid selection")
            except (ValueError, IndexError):
                print("❌ Invalid input")
        
        elif choice == '4':
            print("\nCurrent Charts:")
            for i, chart in enumerate(modal.dashboard.config.charts, 1):
                print(f"  {i}. {chart['title']} ({chart['type']})")
        
        elif choice == '5':
            print("\nAvailable Chart Types:")
            chart_types = modal.get_available_chart_types()
            for i, ct in enumerate(chart_types, 1):
                print(f"  {i}. {ct}")
            
            try:
                type_idx = int(input("Select chart type: ")) - 1
                if 0 <= type_idx < len(chart_types):
                    chart_type = chart_types[type_idx]
                    
                    title = input("Enter chart title: ").strip()
                    
                    print("\nAvailable Data Sources:")
                    sources = modal.get_available_data_sources()
                    for i, src in enumerate(sources, 1):
                        print(f"  {i}. {src}")
                    
                    src_idx = int(input("Select data source: ")) - 1
                    if 0 <= src_idx < len(sources):
                        data_source = sources[src_idx]
                        modal.add_chart(chart_type, title, data_source)
                        print(f"✓ Added chart: {title}")
                    else:
                        print("❌ Invalid data source")
                else:
                    print("❌ Invalid chart type")
            except (ValueError, IndexError):
                print("❌ Invalid input")
        
        elif choice == '6':
            current = modal.dashboard.config.charts
            if not current:
                print("No charts to remove")
                continue
            
            print("\nCurrent Charts:")
            for i, chart in enumerate(current, 1):
                print(f"  {i}. {chart['title']}")
            
            try:
                idx = int(input("Select chart number to remove: ")) - 1
                if 0 <= idx < len(current):
                    modal.remove_chart(current[idx]['title'])
                    print(f"✓ Removed chart: {current[idx]['title']}")
                else:
                    print("❌ Invalid selection")
            except (ValueError, IndexError):
                print("❌ Invalid input")
        
        elif choice == '7':
            modal.close()
            print("✓ Modal closed")
        
        else:
            print("❌ Invalid option")


def main():
    """Main demo function"""
    global logger
    logger = setup_logging(log_level="INFO", log_file="logs/dashboard_demo.log")
    
    print("🚀 Initializing Visual Dashboard...")
    dashboard = create_dashboard()
    modal = DashboardModal(dashboard)
    
    while True:
        print_menu()
        choice = input("Select option: ").strip()
        
        if choice == '1':
            # Display Metrics
            dashboard.display_metrics_console()
        
        elif choice == '2':
            # Open Modal
            modal.open()
            modal_menu(modal)
        
        elif choice == '3':
            # Generate Charts (Matplotlib)
            print("\n📊 Generating charts with Matplotlib...")
            files = dashboard.generate_all_charts(use_plotly=False)
            if files:
                print(f"✓ Generated {len(files)} chart(s):")
                for f in files:
                    print(f"  - {f}")
            else:
                print("❌ No charts generated. Matplotlib may not be installed.")
        
        elif choice == '4':
            # Generate Charts (Plotly)
            print("\n📊 Generating interactive charts with Plotly...")
            files = dashboard.generate_all_charts(use_plotly=True)
            if files:
                print(f"✓ Generated {len(files)} chart(s):")
                for f in files:
                    print(f"  - {f}")
            else:
                print("❌ No charts generated. Plotly may not be installed.")
        
        elif choice == '5':
            # Export Dashboard
            print("\n📄 Exporting dashboard to HTML...")
            dashboard.export_dashboard_html()
            print("✓ Dashboard exported to data/dashboard.html")
        
        elif choice == '6':
            # Exit
            print("\n👋 Goodbye!")
            sys.exit(0)
        
        else:
            print("❌ Invalid option. Please try again.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if logger:
            logger.error(f"Demo error: {e}", exc_info=True)
        sys.exit(1)
