"""
UEBA Monitoring Page

User and Entity Behavior Analytics for security monitoring
and access control auditing.
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import random
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.loaders import load_json


# Page config
st.set_page_config(
    page_title="UEBA Monitoring",
    page_icon="🔒",
    layout="wide"
)


def generate_anomaly_timeline():
    """Generate sample anomaly timeline data"""
    dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30, 0, -1)]
    anomaly_counts = [random.randint(0, 5) for _ in dates]
    
    return dates, anomaly_counts


def main():
    """UEBA Monitoring Dashboard Page"""
    
    st.title("🔒 UEBA Monitoring")
    st.markdown("User and Entity Behavior Analytics - Security & Access Control")
    st.markdown("---")
    
    # Load data
    try:
        ueba_data = load_json('data/ueba_logs.json')
    except FileNotFoundError:
        st.error("❌ Data files not found. Please regenerate data from the home page.")
        return
    
    # Summary metrics
    allowed_actions = ueba_data.get('allowed_actions', [])
    blocked_actions = ueba_data.get('blocked_actions', [])
    total_events = ueba_data.get('total_events', 0)
    blocked_count = ueba_data.get('blocked_count', 0)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Events", total_events)
    
    with col2:
        st.metric("Allowed", len(allowed_actions), delta=f"{(len(allowed_actions)/total_events*100):.0f}%")
    
    with col3:
        st.metric("Blocked", blocked_count, delta=f"-{(blocked_count/total_events*100):.0f}%", delta_color="inverse")
    
    with col4:
        compliance_rate = (len(allowed_actions) / total_events * 100) if total_events > 0 else 0
        st.metric("Compliance Rate", f"{compliance_rate:.1f}%")
    
    st.markdown("---")
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["📋 Access Logs", "📊 Anomaly Timeline", "🔥 Agent-Resource Heatmap"])
    
    with tab1:
        st.subheader("Access Control Logs")
        
        # Combine all logs
        all_logs = []
        
        for action in allowed_actions:
            all_logs.append({
                'Agent': action['agent'],
                'Action': action['action'],
                'Resource': action['resource'],
                'Status': '✅ ' + action['status'],
                'Anomaly Score': 0.0,
                'Reason': action.get('reason', 'N/A')
            })
        
        for action in blocked_actions:
            # Generate random anomaly score for blocked actions
            anomaly_score = random.uniform(0.7, 0.95)
            all_logs.append({
                'Agent': action['agent'],
                'Action': action['action'],
                'Resource': action['resource'],
                'Status': '🔴 ' + action['status'],
                'Anomaly Score': anomaly_score,
                'Reason': action.get('reason', 'N/A')
            })
        
        # Create DataFrame
        logs_df = pd.DataFrame(all_logs)
        
        # Color coding function
        def highlight_status(row):
            if '🔴' in str(row['Status']):
                return ['background-color: #ffebee'] * len(row)
            else:
                return ['background-color: #e8f5e9'] * len(row)
        
        styled_df = logs_df.style.apply(highlight_status, axis=1)
        
        st.dataframe(
            styled_df,
            hide_index=True,
            use_container_width=True,
            height=400
        )
        
        st.caption(f"Showing {len(all_logs)} access events")
        
        # Severity breakdown
        st.markdown("###")
        st.markdown("**🚨 Blocked Actions by Severity**")
        
        severity_counts = {}
        for action in blocked_actions:
            severity = action.get('severity', 'UNKNOWN')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        if severity_counts:
            cols = st.columns(len(severity_counts))
            for i, (severity, count) in enumerate(severity_counts.items()):
                with cols[i]:
                    color = {
                        'CRITICAL': '#F44336',
                        'HIGH': '#FF9800',
                        'MEDIUM': '#FFC107',
                        'LOW': '#4CAF50'
                    }.get(severity, '#9E9E9E')
                    
                    st.markdown(f"""
                    <div style='padding: 15px; background-color: {color}15; border-radius: 10px;
                         border: 2px solid {color}; text-align: center; color: #333'>
                        <h4 style='margin: 0; color: {color}'>{severity}</h4>
                        <p style='font-size: 2em; margin: 10px 0; font-weight: bold; color: #333'>{count}</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    with tab2:
        st.subheader("📈 Anomaly Detection Timeline")
        
        # Generate timeline data
        dates, anomaly_counts = generate_anomaly_timeline()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=anomaly_counts,
            mode='lines+markers',
            name='Anomalies Detected',
            line=dict(color='#F44336', width=3),
            marker=dict(size=8),
            fill='tozeroy',
            fillcolor='rgba(244, 67, 54, 0.2)'
        ))
        
        # Add threshold line
        fig.add_hline(
            y=3,
            line_dash="dash",
            line_color="#FF9800",
            annotation_text="Alert Threshold",
            annotation_position="right"
        )
        
        fig.update_layout(
            title='Security Anomalies - Last 30 Days',
            xaxis_title='Date',
            yaxis_title='Anomaly Count',
            template='plotly_white',
            hovermode='x unified',
            height=400
        )
        
        fig.update_xaxes(tickangle=-45)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Stats
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Total Anomalies", sum(anomaly_counts))
        with col_b:
            st.metric("Peak Day", max(anomaly_counts))
        with col_c:
            st.metric("Avg per Day", f"{sum(anomaly_counts)/len(anomaly_counts):.1f}")
    
    with tab3:
        st.subheader("🔥 Agent × Resource Access Heatmap")
        
        # Create activity matrix
        agents = list(set([log['Agent'] for log in all_logs]))
        resources = list(set([log['Resource'] for log in all_logs]))
        
        # Build matrix
        matrix = []
        for agent in agents:
            row = []
            for resource in resources:
                # Count accesses (allowed + blocked)
                count = sum(1 for log in all_logs 
                           if log['Agent'] == agent and log['Resource'] == resource)
                row.append(count)
            matrix.append(row)
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=matrix,
            x=resources,
            y=agents,
            colorscale='RdYlGn_r',
            text=matrix,
            texttemplate='%{text}',
            textfont={"size": 12},
            colorbar=dict(title="Access Count")
        ))
        
        fig.update_layout(
            title='Agent-Resource Access Pattern',
            xaxis_title='Resource',
            yaxis_title='Agent',
            template='plotly_white',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("""
        **Heatmap Interpretation:**
        - 🟢 Green: Low access frequency (normal)
        - 🟡 Yellow: Moderate access frequency
        - 🔴 Red: High access frequency (may indicate unusual activity)
        """)
    
    st.markdown("---")
    
    # Security Recommendations
    st.subheader("🛡️ Security Recommendations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**✅ Best Practices**")
        st.success("""
        - Agents have appropriate permissions
        - Access patterns follow principle of least privilege
        - Regular audit reviews conducted
        - Anomaly detection is active
        """)
    
    with col2:
        st.markdown("**⚠️ Action Items**")
        if blocked_count > 0:
            st.warning(f"""
            - Review {blocked_count} blocked access attempts
            - Investigate high-severity violations
            - Update access policies if needed
            - Train agents on compliance
            """)
        else:
            st.success("No action items - all systems compliant!")
    
    st.markdown("---")
    
    # Additional Info
    with st.expander("ℹ️ About UEBA Security Monitoring"):
        st.markdown("""
        ### User and Entity Behavior Analytics
        
        UEBA monitors access patterns to detect security threats and ensure compliance.
        
        **Key Features:**
        - **Access Control** - Monitor who accesses what resources
        - **Anomaly Detection** - Identify unusual behavior patterns
        - **Compliance Tracking** - Ensure policy adherence
        - **Audit Trail** - Complete record of all access events
        
        **Security Levels:**
        - 🔴 **CRITICAL** - Immediate action required
        - 🟡 **HIGH** - Review within 24 hours
        - 🟠 **MEDIUM** - Review within week
        - 🟢 **LOW** - Log for analysis
        
        **Monitored Entities:**
        - DiagnosisAgent
        - SchedulingAgent
        - CustomerAgent
        - ManufacturingAgent
        
        **Protected Resources:**
        - telematics_data
        - booking_slots
        - dialogue_history
        - maintenance_records
        """)


if __name__ == "__main__":
    main()
