"""
Manufacturing Insights Page

Dashboard for quality analysis, root cause analysis (RCA),
and corrective/preventive actions (CAPA).
"""

import streamlit as st
import sys
from pathlib import Path
import plotly.graph_objects as go

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.loaders import load_json


# Page config
st.set_page_config(
    page_title="Manufacturing Insights",
    page_icon="🏭",
    layout="wide"
)


def main():
    """Manufacturing Insights Dashboard Page"""
    
    st.title("🏭 Manufacturing Insights")
    st.markdown("Quality Analysis, Root Cause Analysis (RCA) & Corrective Actions (CAPA)")
    st.markdown("---")
    
    # Load data
    try:
        manufacturing_data = load_json('data/manufacturing.json')
    except FileNotFoundError:
        st.error("❌ Data files not found. Please regenerate data from the home page.")
        return
    
    # RCA Section
    st.subheader("🔍 Root Cause Analysis (RCA)")
    
    rca_data = manufacturing_data.get('rca_example', {})
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # RCA Details
        st.markdown(f"""
        <div style='padding: 20px; background-color: #FFF3E0; border-radius: 10px; 
             border-left: 5px solid #FF9800; margin: 10px 0; color: #333'>
            <h3 style='margin-top: 0; color: #E65100'>📋 {rca_data.get('incident_id', 'N/A')}</h3>
            <p style='color: #333'><strong>Issue:</strong> {rca_data.get('issue', 'N/A')}</p>
            <p style='color: #333'><strong>Root Cause:</strong> {rca_data.get('root_cause', 'N/A')}</p>
            <p style='color: #333'><strong>Analysis:</strong> {rca_data.get('analysis', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**📎 Evidence:**")
        for evidence in rca_data.get('evidence', []):
            st.markdown(f"- {evidence}")
    
    with col2:
        st.markdown("**🚗 Affected Vehicles**")
        affected = rca_data.get('affected_vehicles', [])
        
        for vehicle in affected:
            st.markdown(f"""
            <div style='padding: 10px; margin: 5px; background-color: #FFEBEE; 
                 border-radius: 8px; border: 1px solid #F44336; color: #333'>
                <strong style='color: #D32F2F'>{vehicle}</strong>
            </div>
            """, unsafe_allow_html=True)
        
        st.metric("Total Affected", len(affected))
    
    st.markdown("---")
    
    # CAPA Section
    st.subheader("✅ Corrective & Preventive Actions (CAPA)")
    
    capa_data = manufacturing_data.get('capa_example', {})
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("**🔧 Corrective Action**")
        st.info(capa_data.get('corrective_action', 'N/A'))
        
        st.markdown("**📊 Status**")
        status = capa_data.get('status', 'UNKNOWN')
        status_color = {
            'COMPLETED': 'green',
            'IN_PROGRESS': 'orange',
            'PENDING': 'gray'
        }.get(status, 'gray')
        
        st.markdown(f"""
        <div style='padding: 15px; background-color: {status_color}15; 
             border-radius: 10px; border: 2px solid {status_color}; color: #333'>
            <h3 style='margin: 0; color: {status_color}'>{status}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col_b:
        st.markdown("**🛡️ Preventive Action**")
        st.success(capa_data.get('preventive_action', 'N/A'))
        
        st.markdown("**📅 Timeline**")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Responsible", capa_data.get('responsible', 'N/A'))
        with col2:
            st.metric("Deadline", capa_data.get('deadline', 'N/A'))
    
    st.markdown(f"**✓ Verification:** {capa_data.get('verification', 'N/A')}")
    
    st.markdown("---")
    
    # Quality Metrics
    st.subheader("📊 Quality Metrics & Impact")
    
    quality_metrics = manufacturing_data.get('quality_metrics', {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        defect_rate = quality_metrics.get('defect_rate', 0) * 100
        st.metric("Defect Rate", f"{defect_rate:.2f}%", delta="-0.5%" if defect_rate < 3 else "+0.3%")
    
    with col2:
        batch_rejection = quality_metrics.get('batch_rejection', 0)
        st.metric("Batch Rejections", batch_rejection, delta="-1")
    
    with col3:
        supplier_score = quality_metrics.get('supplier_score', 0)
        st.metric("Supplier Score", f"{supplier_score:.1f}/100", delta="+2.5")
    
    with col4:
        trend = quality_metrics.get('trend', 'stable')
        trend_emoji = {'improving': '📈', 'declining': '📉', 'stable': '➡️'}.get(trend, '➡️')
        st.metric("Trend", f"{trend_emoji} {trend.title()}")
    
    st.markdown("###")
    
    # Warranty Claim Reduction Chart
    st.markdown("**💰 Warranty Claim Reduction Impact**")
    
    # Sample data showing improvement after corrective action
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    claims_before = [45, 48, 52, 50, 47, 43]
    claims_after = [43, 38, 32, 28, 25, 22]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=months,
        y=claims_before,
        name='Before CAPA',
        marker_color='#EF5350',
        opacity=0.7
    ))
    
    fig.add_trace(go.Bar(
        x=months,
        y=claims_after,
        name='After CAPA',
        marker_color='#66BB6A',
        opacity=0.7
    ))
    
    fig.update_layout(
        title='Monthly Warranty Claims: Before vs After Corrective Action',
        xaxis_title='Month',
        yaxis_title='Number of Claims',
        template='plotly_white',
        barmode='group',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Calculate reduction
    reduction_pct = ((claims_before[-1] - claims_after[-1]) / claims_before[-1]) * 100
    st.success(f"✅ Warranty claims reduced by **{reduction_pct:.1f}%** after implementing CAPA")
    
    st.markdown("---")
    
    # Affected Models Cluster
    st.subheader("🚗 Affected Vehicle Models")
    
    # Sample affected models
    models = [
        {"model": "Model X-200", "units": 156, "severity": "High"},
        {"model": "Model Y-150", "units": 89, "severity": "Medium"},
        {"model": "Model Z-300", "units": 23, "severity": "Low"}
    ]
    
    cols = st.columns(3)
    
    for i, model in enumerate(models):
        with cols[i]:
            severity_color = {
                'High': '#F44336',
                'Medium': '#FF9800',
                'Low': '#4CAF50'
            }.get(model['severity'], '#9E9E9E')
            
            st.markdown(f"""
            <div style='padding: 20px; margin: 10px 0; background-color: {severity_color}15; 
                 border-radius: 12px; border: 2px solid {severity_color}; text-align: center; color: #333'>
                <h3 style='margin: 0; color: {severity_color}'>{model['model']}</h3>
                <p style='font-size: 2em; margin: 10px 0; font-weight: bold; color: #333'>{model['units']}</p>
                <p style='margin: 0; color: #555'>Units Affected</p>
                <p style='margin: 5px 0; color: {severity_color}; font-weight: bold'>
                    {model['severity']} Severity
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Additional Info
    with st.expander("ℹ️ About Manufacturing Quality Process"):
        st.markdown("""
        ### Quality Management System
        
        **RCA (Root Cause Analysis):**
        - Systematic investigation of product failures
        - Identification of underlying issues
        - Evidence-based analysis
        - Impact assessment
        
        **CAPA (Corrective & Preventive Actions):**
        - **Corrective**: Fix existing problems
        - **Preventive**: Prevent future occurrences
        - **Verification**: Ensure effectiveness
        - **Documentation**: Track progress and outcomes
        
        **Quality Metrics:**
        - Defect rate monitoring
        - Supplier performance tracking
        - Batch quality control
        - Continuous improvement trends
        
        This integrated approach ensures product quality and customer satisfaction.
        """)


if __name__ == "__main__":
    main()
