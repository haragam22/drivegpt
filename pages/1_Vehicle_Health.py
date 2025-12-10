"""
Vehicle Health Overview Page

Interactive dashboard for monitoring individual vehicle health,
component risks, and diagnostic insights.
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.loaders import load_json, load_csv
from utils.charts import risk_bar_chart, component_trend_line


# Page config
st.set_page_config(
    page_title="Vehicle Health",
    page_icon="🔧",
    layout="wide"
)


def main():
    """Vehicle Health Dashboard Page"""
    
    st.title("🔧 Vehicle Health Overview")
    st.markdown("Monitor component health, risk scores, and diagnostic insights")
    st.markdown("---")
    
    # Load data
    try:
        risk_profiles = load_json('data/risk_profiles.json')
        telematics_df = load_csv('data/telematics_sample_1000.csv')
    except FileNotFoundError:
        st.error("❌ Data files not found. Please regenerate data from the home page.")
        return
    
    # Vehicle selector
    vehicle_ids = [profile['vehicle_id'] for profile in risk_profiles]
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        selected_vehicle = st.selectbox(
            "🚗 Select Vehicle",
            vehicle_ids,
            help="Choose a vehicle to view detailed health metrics"
        )
    
    # Find selected vehicle profile
    vehicle_profile = next(
        (p for p in risk_profiles if p['vehicle_id'] == selected_vehicle),
        None
    )
    
    if not vehicle_profile:
        st.warning("Vehicle data not found")
        return
    
    # Get vehicle telematics data
    vehicle_telemetrics = telematics_df[
        telematics_df['vehicle_id'] == selected_vehicle
    ].copy()
    
    # Severity badge
    severity = vehicle_profile['severity']
    severity_colors = {
        'Critical': '🔴',
        'Moderate': '🟡',
        'Routine': '🟢'
    }
    
    with col2:
        st.metric(
            label="Severity",
            value=f"{severity_colors.get(severity, '⚪')} {severity}"
        )
    
    with col3:
        overall_risk = vehicle_profile['risk_profile']['overall_risk']
        st.metric(
            label="Overall Risk",
            value=f"{overall_risk:.1%}"
        )
    
    st.markdown("---")
    
    # Main layout: 2 columns
    left_col, right_col = st.columns([2, 1])
    
    # LEFT COLUMN - Charts
    with left_col:
        # Risk Bar Chart
        st.subheader("📊 Component Risk Breakdown")
        risk_chart = risk_bar_chart(vehicle_profile['risk_profile'])
        st.plotly_chart(risk_chart, use_container_width=True)
        
        st.markdown("---")
        
        # Component Trend Lines
        st.subheader("📈 Component Metrics Over Time")
        if len(vehicle_telemetrics) > 0:
            trend_chart = component_trend_line(vehicle_telemetrics)
            st.plotly_chart(trend_chart, use_container_width=True)
        else:
            st.info("Not enough historical data for trends")
    
    # RIGHT COLUMN - Summary Cards
    with right_col:
        st.subheader("📋 Summary")
        
        # Severity Card
        severity_color_map = {
            'Critical': 'red',
            'Moderate': 'orange',
            'Routine': 'green'
        }
        severity_color = severity_color_map.get(severity, 'gray')
        
        st.markdown(f"""
        <div style='padding: 15px; border-radius: 10px; background-color: {severity_color}15; border-left: 5px solid {severity_color}'>
            <h4 style='margin: 0; color: {severity_color}'>Status: {severity}</h4>
            <p style='margin: 5px 0 0 0; font-size: 0.9em; color: #333'>
                Overall risk score: <strong>{overall_risk:.1%}</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("###")
        
        # Evidence Tags
        st.markdown("**🔍 Evidence & Alerts**")
        evidence = vehicle_profile.get('evidence', [])
        
        if evidence and evidence != ['All systems normal']:
            for item in evidence:
                # Color code evidence by severity
                if 'critical' in item.lower() or 'above' in item.lower():
                    badge_color = 'red'
                    icon = '🔴'
                elif 'abnormal' in item.lower() or 'spike' in item.lower():
                    badge_color = 'orange'
                    icon = '🟡'
                else:
                    badge_color = 'blue'
                    icon = '🔵'
                
                st.markdown(f"""
                <span style='display: inline-block; margin: 3px; padding: 5px 10px; 
                      background-color: {badge_color}15; color: {badge_color}; 
                      border-radius: 15px; font-size: 0.85em; border: 1px solid {badge_color}40'>
                    {icon} {item.replace('_', ' ').title()}
                </span>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ All systems normal")
        
        st.markdown("###")
        
        # Component Details
        st.markdown("**⚙️ Component Details**")
        
        metrics = vehicle_profile.get('metrics', {})
        risks = vehicle_profile['risk_profile']
        
        # Engine
        with st.expander("🔥 Engine", expanded=True):
            engine_temp = metrics.get('engine_temp', 'N/A')
            engine_risk = risks.get('engine_risk', 0)
            st.metric("Temperature", f"{engine_temp}°C" if engine_temp != 'N/A' else 'N/A')
            st.progress(engine_risk)
            st.caption(f"Risk: {engine_risk:.1%}")
        
        # Battery
        with st.expander("🔋 Battery", expanded=True):
            battery_voltage = metrics.get('battery_voltage', 'N/A')
            battery_risk = risks.get('battery_risk', 0)
            st.metric("Voltage", f"{battery_voltage}V" if battery_voltage != 'N/A' else 'N/A')
            st.progress(battery_risk)
            st.caption(f"Risk: {battery_risk:.1%}")
        
        # Brakes
        with st.expander("🛑 Brakes", expanded=True):
            brake_wear = metrics.get('brake_wear', 'N/A')
            brake_risk = risks.get('brake_risk', 0)
            st.metric("Wear Level", f"{brake_wear:.2f}" if brake_wear != 'N/A' else 'N/A')
            st.progress(brake_risk)
            st.caption(f"Risk: {brake_risk:.1%}")
        
        # Tyres
        with st.expander("🛞 Tyres", expanded=True):
            total_km = metrics.get('total_km', 'N/A')
            tyre_risk = risks.get('tyre_risk', 0)
            st.metric("Mileage", f"{total_km:,.0f} km" if total_km != 'N/A' else 'N/A')
            st.progress(tyre_risk)
            st.caption(f"Risk: {tyre_risk:.1%}")
    
    st.markdown("---")
    
    # Additional Info
    with st.expander("ℹ️ About Risk Scoring"):
        st.markdown("""
        ### Dynamic Risk Scoring System
        
        This dashboard uses a sophisticated multi-factor risk assessment:
        
        - **Rolling Baselines** - Compares current metrics to vehicle's own history
        - **Z-Score Detection** - Identifies statistical anomalies (>2σ deviations)
        - **Trend Analysis** - Detects rapid changes (>10% in 3 readings)
        - **Hard Thresholds** - Industry standards (95°C, 12V, 0.7 brake wear)
        - **Hysteresis** - Requires 2 consecutive high-risk windows to prevent false alarms
        
        **Risk Levels:**
        - 🟢 **Routine** (<30%): Normal operation
        - 🟡 **Moderate** (30-70%): Service recommended soon
        - 🔴 **Critical** (>70%): Immediate attention required
        """)


if __name__ == "__main__":
    main()
