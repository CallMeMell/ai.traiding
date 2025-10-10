"""
view_session_app.py - View Session Dashboard with Streamlit
==========================================================
Lightweight dashboard to visualize sessions and trades.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.session_store import SessionStore


# Page config
st.set_page_config(
    page_title="View Session Dashboard",
    page_icon="📊",
    layout="wide"
)


class ViewSessionApp:
    """Streamlit app for viewing session data."""
    
    def __init__(self):
        """Initialize the app."""
        self.store = SessionStore()
        
        # Initialize session state for filters
        if 'time_range' not in st.session_state:
            st.session_state.time_range = 'all'
        if 'strategy_tag' not in st.session_state:
            st.session_state.strategy_tag = 'all'
        if 'custom_start' not in st.session_state:
            st.session_state.custom_start = None
        if 'custom_end' not in st.session_state:
            st.session_state.custom_end = None
    
    def render_header(self):
        """Render page header."""
        st.title("📊 View Session Dashboard")
        st.markdown("Visualize session events and performance metrics in real-time")
    
    def render_filters(self):
        """Render filter controls."""
        st.sidebar.header("🔍 Filters")
        
        # Time range filter
        time_range = st.sidebar.selectbox(
            "Time Range",
            ['all', 'last_1h', 'last_24h', 'last_7d', 'custom'],
            index=0 if st.session_state.time_range == 'all' else 
                  ['all', 'last_1h', 'last_24h', 'last_7d', 'custom'].index(st.session_state.time_range)
        )
        st.session_state.time_range = time_range
        
        # Custom date range
        if time_range == 'custom':
            st.sidebar.subheader("Custom Date Range")
            start_date = st.sidebar.date_input("Start Date", value=st.session_state.custom_start)
            end_date = st.sidebar.date_input("End Date", value=st.session_state.custom_end)
            st.session_state.custom_start = start_date
            st.session_state.custom_end = end_date
        
        # Strategy tag filter
        strategy_tag = st.sidebar.selectbox(
            "Strategy Tag",
            ['all', 'data_phase', 'strategy_phase', 'api_phase'],
            index=0 if st.session_state.strategy_tag == 'all' else
                  ['all', 'data_phase', 'strategy_phase', 'api_phase'].index(st.session_state.strategy_tag)
        )
        st.session_state.strategy_tag = strategy_tag
        
        # Auto-refresh
        auto_refresh = st.sidebar.checkbox("Auto-refresh (every 5s)", value=True)
        if auto_refresh:
            st.sidebar.info("Page will refresh automatically")
    
    def filter_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter events based on selected filters.
        
        Args:
            events: List of events
            
        Returns:
            Filtered events
        """
        if not events:
            return []
        
        filtered = events
        
        # Time range filter
        now = datetime.now()
        if st.session_state.time_range == 'last_1h':
            cutoff = now - timedelta(hours=1)
            filtered = [e for e in filtered if datetime.fromisoformat(e['timestamp']) >= cutoff]
        elif st.session_state.time_range == 'last_24h':
            cutoff = now - timedelta(hours=24)
            filtered = [e for e in filtered if datetime.fromisoformat(e['timestamp']) >= cutoff]
        elif st.session_state.time_range == 'last_7d':
            cutoff = now - timedelta(days=7)
            filtered = [e for e in filtered if datetime.fromisoformat(e['timestamp']) >= cutoff]
        elif st.session_state.time_range == 'custom':
            if st.session_state.custom_start and st.session_state.custom_end:
                start = datetime.combine(st.session_state.custom_start, datetime.min.time())
                end = datetime.combine(st.session_state.custom_end, datetime.max.time())
                filtered = [e for e in filtered 
                           if start <= datetime.fromisoformat(e['timestamp']) <= end]
        
        # Strategy tag filter
        if st.session_state.strategy_tag != 'all':
            filtered = [e for e in filtered 
                       if e.get('phase') == st.session_state.strategy_tag]
        
        return filtered
    
    def render_summary_metrics(self, summary: Optional[Dict[str, Any]]):
        """
        Render summary metrics.
        
        Args:
            summary: Summary dictionary
        """
        if not summary:
            st.warning("No summary data available")
            return
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Initial Capital",
                f"${summary.get('initial_capital', 0):,.2f}"
            )
        
        with col2:
            current_equity = summary.get('current_equity', 0)
            initial_capital = summary.get('initial_capital', 0)
            pnl = current_equity - initial_capital
            st.metric(
                "Current Equity",
                f"${current_equity:,.2f}",
                delta=f"${pnl:,.2f}"
            )
        
        with col3:
            roi = summary.get('roi', 0)
            st.metric(
                "ROI",
                f"{roi:.2f}%",
                delta=f"{roi:.2f}%"
            )
        
        with col4:
            phases_completed = summary.get('phases_completed', 0)
            phases_total = summary.get('phases_total', 0)
            st.metric(
                "Progress",
                f"{phases_completed}/{phases_total}",
                delta=f"{(phases_completed/phases_total*100):.0f}%" if phases_total > 0 else "0%"
            )
    
    def render_pnl_chart(self, summary: Optional[Dict[str, Any]]):
        """
        Render PnL/equity curve chart.
        
        Args:
            summary: Summary dictionary
        """
        st.subheader("📈 Equity Curve")
        
        if not summary:
            st.info("No data available for equity curve")
            return
        
        # Create simple equity curve
        initial = summary.get('initial_capital', 10000)
        current = summary.get('current_equity', 10000)
        
        # Simulate progression (in real scenario, track over time)
        data = [
            {'timestamp': summary.get('session_start', ''), 'equity': initial},
            {'timestamp': summary.get('last_updated', ''), 'equity': current}
        ]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[d['timestamp'] for d in data],
            y=[d['equity'] for d in data],
            mode='lines+markers',
            name='Equity',
            line=dict(color='#00cc96', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            xaxis_title="Time",
            yaxis_title="Equity ($)",
            hovermode='x unified',
            template='plotly_white',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_wins_losses_chart(self, events: List[Dict[str, Any]]):
        """
        Render wins/losses bar chart.
        
        Args:
            events: List of events
        """
        st.subheader("📊 Wins vs Losses by Phase")
        
        if not events:
            st.info("No events available")
            return
        
        # Count wins and losses by phase
        phase_stats = {}
        for event in events:
            phase = event.get('phase', 'unknown')
            status = event.get('status', 'unknown')
            
            if phase not in phase_stats:
                phase_stats[phase] = {'wins': 0, 'losses': 0}
            
            if status == 'success':
                phase_stats[phase]['wins'] += 1
            elif status in ['error', 'failed']:
                phase_stats[phase]['losses'] += 1
        
        if not phase_stats:
            st.info("No phase statistics available")
            return
        
        # Create bar chart
        phases = list(phase_stats.keys())
        wins = [phase_stats[p]['wins'] for p in phases]
        losses = [phase_stats[p]['losses'] for p in phases]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Wins', x=phases, y=wins, marker_color='#00cc96'))
        fig.add_trace(go.Bar(name='Losses', x=phases, y=losses, marker_color='#ef553b'))
        
        fig.update_layout(
            barmode='group',
            xaxis_title="Phase",
            yaxis_title="Count",
            template='plotly_white',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_events_table(self, events: List[Dict[str, Any]]):
        """
        Render events table.
        
        Args:
            events: List of events
        """
        st.subheader("📋 Recent Events")
        
        if not events:
            st.info("No events available")
            return
        
        # Show last 20 events
        recent_events = events[-20:]
        
        # Create table data
        table_data = []
        for event in reversed(recent_events):
            table_data.append({
                'Timestamp': event.get('timestamp', 'N/A'),
                'Type': event.get('type', 'N/A'),
                'Phase': event.get('phase', 'N/A'),
                'Status': event.get('status', 'N/A')
            })
        
        st.dataframe(table_data, use_container_width=True)
    
    def render_empty_state(self):
        """Render empty state when no data."""
        st.info("🔄 No session data available yet. Run the automation runner to generate data.")
        st.code("python automation/runner.py", language="bash")
    
    def run(self):
        """Run the Streamlit app."""
        self.render_header()
        self.render_filters()
        
        # Load data
        summary = self.store.read_summary()
        events = self.store.read_events()
        
        # Filter events
        filtered_events = self.filter_events(events)
        
        # Check if data exists
        if not summary and not events:
            self.render_empty_state()
            return
        
        # Render content
        with st.spinner("Loading data..."):
            self.render_summary_metrics(summary)
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                self.render_pnl_chart(summary)
            
            with col2:
                self.render_wins_losses_chart(filtered_events)
            
            st.markdown("---")
            
            self.render_events_table(filtered_events)
        
        # Auto-refresh
        if st.sidebar.checkbox("Auto-refresh (every 5s)", value=False):
            import time
            time.sleep(5)
            st.rerun()
        
        # Last updated
        st.sidebar.markdown("---")
        st.sidebar.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    """Main entry point."""
    app = ViewSessionApp()
    app.run()


if __name__ == '__main__':
    main()
