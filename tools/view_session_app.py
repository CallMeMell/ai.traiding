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
        if 'event_type_filter' not in st.session_state:
            st.session_state.event_type_filter = 'all'
        if 'phase_filter' not in st.session_state:
            st.session_state.phase_filter = 'all'
        if 'events_cache' not in st.session_state:
            st.session_state.events_cache = []
        if 'last_event_count' not in st.session_state:
            st.session_state.last_event_count = 0
    
    def render_header(self):
        """Render page header."""
        st.title("📊 View Session Dashboard")
        st.markdown("Visualize session events and performance metrics in real-time")
    
    def render_filters(self):
        """Render filter controls."""
        st.sidebar.header("🔍 Filters")
        
        # Time range filter with more presets
        time_range = st.sidebar.selectbox(
            "Time Range",
            ['all', '15min', '1h', '4h', 'today', 'custom'],
            index=0 if st.session_state.time_range == 'all' else 
                  ['all', '15min', '1h', '4h', 'today', 'custom'].index(st.session_state.time_range)
        )
        st.session_state.time_range = time_range
        
        # Custom date range
        if time_range == 'custom':
            st.sidebar.subheader("Custom Date Range")
            start_date = st.sidebar.date_input("Start Date", value=st.session_state.custom_start)
            end_date = st.sidebar.date_input("End Date", value=st.session_state.custom_end)
            st.session_state.custom_start = start_date
            st.session_state.custom_end = end_date
        
        # Phase filter
        phase_filter = st.sidebar.selectbox(
            "Phase Filter",
            ['all', 'data_phase', 'strategy_phase', 'api_phase'],
            index=0 if st.session_state.phase_filter == 'all' else
                  ['all', 'data_phase', 'strategy_phase', 'api_phase'].index(st.session_state.phase_filter)
        )
        st.session_state.phase_filter = phase_filter
        
        # Event type filter
        event_type_filter = st.sidebar.selectbox(
            "Event Type Filter",
            ['all', 'runner_start', 'runner_end', 'phase_start', 'phase_end', 
             'checkpoint', 'heartbeat', 'error', 'summary_updated'],
            index=0
        )
        st.session_state.event_type_filter = event_type_filter
        
        # Manual refresh button
        if st.sidebar.button("🔄 Refresh Now"):
            st.rerun()
        
        # Auto-refresh
        auto_refresh = st.sidebar.checkbox("Auto-refresh (every 10s)", value=True)
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
        if st.session_state.time_range == '15min':
            cutoff = now - timedelta(minutes=15)
            filtered = [e for e in filtered if datetime.fromisoformat(e['timestamp']) >= cutoff]
        elif st.session_state.time_range == '1h':
            cutoff = now - timedelta(hours=1)
            filtered = [e for e in filtered if datetime.fromisoformat(e['timestamp']) >= cutoff]
        elif st.session_state.time_range == '4h':
            cutoff = now - timedelta(hours=4)
            filtered = [e for e in filtered if datetime.fromisoformat(e['timestamp']) >= cutoff]
        elif st.session_state.time_range == 'today':
            cutoff = datetime.combine(now.date(), datetime.min.time())
            filtered = [e for e in filtered if datetime.fromisoformat(e['timestamp']) >= cutoff]
        elif st.session_state.time_range == 'custom':
            if st.session_state.custom_start and st.session_state.custom_end:
                start = datetime.combine(st.session_state.custom_start, datetime.min.time())
                end = datetime.combine(st.session_state.custom_end, datetime.max.time())
                filtered = [e for e in filtered 
                           if start <= datetime.fromisoformat(e['timestamp']) <= end]
        
        # Phase filter
        if st.session_state.phase_filter != 'all':
            filtered = [e for e in filtered 
                       if e.get('phase') == st.session_state.phase_filter]
        
        # Event type filter
        if st.session_state.event_type_filter != 'all':
            filtered = [e for e in filtered 
                       if e.get('type') == st.session_state.event_type_filter]
        
        return filtered
    
    def render_current_status(self, summary: Optional[Dict[str, Any]], events: List[Dict[str, Any]]):
        """
        Render current status panel with live information.
        
        Args:
            summary: Summary dictionary
            events: List of events
        """
        st.subheader("📡 Current Status")
        
        if not summary and not events:
            st.info("No status data available")
            return
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Find current phase from latest events
        current_phase = "N/A"
        for event in reversed(events):
            if event.get('phase'):
                current_phase = event.get('phase')
                break
        
        # Find last heartbeat
        last_heartbeat_time = None
        for event in reversed(events):
            if event.get('type') == 'heartbeat':
                last_heartbeat_time = datetime.fromisoformat(event['timestamp'])
                break
        
        # Calculate uptime
        uptime_str = "N/A"
        if summary and summary.get('session_start'):
            start_time = datetime.fromisoformat(summary['session_start'])
            if summary.get('session_end'):
                end_time = datetime.fromisoformat(summary['session_end'])
                uptime_seconds = (end_time - start_time).total_seconds()
            else:
                uptime_seconds = (datetime.now() - start_time).total_seconds()
            uptime_minutes = int(uptime_seconds / 60)
            uptime_str = f"{uptime_minutes}m {int(uptime_seconds % 60)}s"
        
        # Last heartbeat age
        heartbeat_age_str = "N/A"
        if last_heartbeat_time:
            heartbeat_age = (datetime.now() - last_heartbeat_time).total_seconds()
            heartbeat_age_str = f"{int(heartbeat_age)}s ago"
        
        with col1:
            st.metric("Current Phase", current_phase.replace('_', ' ').title())
        
        with col2:
            st.metric("Session Uptime", uptime_str)
        
        with col3:
            st.metric("Last Heartbeat", heartbeat_age_str)
        
        with col4:
            status = summary.get('status', 'unknown') if summary else 'unknown'
            st.metric("Session Status", status.upper())
    
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
            totals = summary.get('totals', {})
            if totals:
                trades = totals.get('trades', 0)
                wins = totals.get('wins', 0)
                win_rate = (wins / trades * 100) if trades > 0 else 0
                st.metric(
                    "Win Rate",
                    f"{win_rate:.1f}%",
                    delta=f"{wins}/{trades} wins"
                )
            else:
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
    
    def render_activity_feed(self, events: List[Dict[str, Any]]):
        """
        Render activity feed with latest events.
        
        Args:
            events: List of events
        """
        st.subheader("📰 Activity Feed (Latest 100 Events)")
        
        if not events:
            st.info("No events available")
            return
        
        # Show last 100 events
        recent_events = events[-100:]
        
        # Create formatted feed
        feed_data = []
        for event in reversed(recent_events):
            # Format timestamp
            try:
                ts = datetime.fromisoformat(event['timestamp'])
                time_str = ts.strftime('%H:%M:%S')
            except:
                time_str = event.get('timestamp', 'N/A')
            
            # Get event details
            event_type = event.get('type', 'N/A')
            phase = event.get('phase', 'N/A')
            level = event.get('level', 'info')
            message = event.get('message', '')
            status = event.get('status', '')
            
            # Create emoji based on level/type
            emoji = '🔵'
            if level == 'error' or event_type == 'error':
                emoji = '🔴'
            elif level == 'warning':
                emoji = '🟡'
            elif event_type == 'checkpoint':
                emoji = '✅' if status == 'pass' else '❌'
            elif event_type == 'heartbeat':
                emoji = '💓'
            elif event_type == 'phase_start':
                emoji = '🚀'
            elif event_type == 'phase_end':
                emoji = '🏁'
            
            feed_data.append({
                '': emoji,
                'Time': time_str,
                'Type': event_type,
                'Phase': phase,
                'Level': level.upper(),
                'Message': message or f"{event_type} event",
                'Status': status
            })
        
        # Display as dataframe with color coding
        st.dataframe(feed_data, use_container_width=True, height=400)
    
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
    
    def load_data_with_cache(self):
        """
        Load data with incremental caching for performance.
        
        Returns:
            Tuple of (summary, events)
        """
        summary = self.store.read_summary()
        
        # Read all events (can be optimized with tail reading)
        all_events = self.store.read_events()
        
        # Update cache if needed
        if len(all_events) != st.session_state.last_event_count:
            st.session_state.events_cache = all_events
            st.session_state.last_event_count = len(all_events)
        
        return summary, st.session_state.events_cache
    
    def run(self):
        """Run the Streamlit app."""
        self.render_header()
        self.render_filters()
        
        # Load data with caching
        try:
            summary, events = self.load_data_with_cache()
        except Exception as e:
            st.error(f"Error loading data: {e}")
            st.info("💡 Hint: Make sure the automation runner has been executed.")
            return
        
        # Filter events
        filtered_events = self.filter_events(events)
        
        # Check if data exists
        if not summary and not events:
            self.render_empty_state()
            return
        
        # Render content
        with st.spinner("Loading data..."):
            # Current Status Panel
            self.render_current_status(summary, events)
            
            st.markdown("---")
            
            # Summary Metrics
            self.render_summary_metrics(summary)
            
            st.markdown("---")
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                self.render_pnl_chart(summary)
            
            with col2:
                self.render_wins_losses_chart(filtered_events)
            
            st.markdown("---")
            
            # Activity Feed
            self.render_activity_feed(filtered_events)
            
            st.markdown("---")
            
            # Detailed Events Table
            with st.expander("📊 Detailed Event History", expanded=False):
                self.render_events_table(filtered_events)
        
        # Auto-refresh with configurable interval
        if st.sidebar.checkbox("Auto-refresh (every 10s)", value=False):
            import time
            time.sleep(10)
            st.rerun()
        
        # Last updated
        st.sidebar.markdown("---")
        st.sidebar.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.sidebar.caption(f"Total events: {len(events)}")
        if summary:
            st.sidebar.caption(f"Session: {summary.get('session_id', 'N/A')[:8]}...")


def main():
    """Main entry point."""
    app = ViewSessionApp()
    app.run()


if __name__ == '__main__':
    main()
