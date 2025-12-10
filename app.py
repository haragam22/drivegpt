"""
Telematics Dashboard - Main Entry Point

Multi-page Streamlit dashboard for vehicle health monitoring,
predictive maintenance, and service optimization.
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.generators import generate_all_from_telematics


# Page configuration
st.set_page_config(
    page_title="Telematics Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    """Main dashboard homepage"""
    
    # Header
    st.title("🚗 Telematics Intelligence Dashboard")
    st.markdown("### AI-Powered Vehicle Health Monitoring & Predictive Maintenance")
    
    st.markdown("---")
    
    # Introduction
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ## Welcome to the Telematics Dashboard
        
        This comprehensive dashboard provides real-time insights into:
        
        - 🔧 **Vehicle Health Monitoring** - Track component wear and predict failures
        - 📊 **Predictive Analytics** - Forecast service demand and optimize capacity
        - 🎯 **Smart Scheduling** - Prioritize maintenance with MAP scoring
        - 💬 **Customer Engagement** - AI-powered service recommendations
        - 🏭 **Manufacturing Insights** - Root cause analysis and quality tracking
        - 🔒 **UEBA Monitoring** - Secure access control and compliance
        
        Navigate through the sidebar to explore different modules.
        """)
    
    with col2:
        st.info("""
        **Quick Stats**
        
        📈 Dynamic Risk Scoring  
        🔄 Rolling Baselines  
        🤖 EWMA Smoothing  
        📉 Z-Score Detection  
        ⚡ Real-time Analysis
        """)
    
    st.markdown("---")
    
    # Data Management Section
    st.markdown("## 🔄 Data Management")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        ### Refresh Analytics Data
        
        Click the button below to regenerate all analytics from the telematics dataset.
        This will:
        - Compute risk profiles using dynamic scoring
        - Generate diagnosis and RUL predictions
        - Create forecasting models
        - Compute MAP priority scores
        - Generate scheduling and engagement data
        """)
        
        if st.button("🔄 Regenerate All Data", type="primary", use_container_width=True):
            with st.spinner("Generating data... This may take a few moments."):
                try:
                    generate_all_from_telematics()
                    st.success("✅ All data regenerated successfully!")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Error generating data: {str(e)}")
    
    with col2:
        st.markdown("""
        ### Data Pipeline
        
        The system processes telematics data through multiple stages:
        
        1. **Load & Parse** - Read CSV with timestamp parsing
        2. **Rolling Baselines** - Compute per-vehicle statistics
        3. **Risk Scoring** - Multi-factor risk assessment
        4. **Evidence Generation** - Identify specific issues
        5. **Analytics Generation** - Create supporting datasets
        6. **Export to JSON** - Save for dashboard consumption
        """)
    
    st.markdown("---")
    
    # Sidebar instructions
    with st.sidebar:
        st.markdown("## 📋 Navigation Guide")
        
        st.markdown("""
        ### Available Modules
        
        **1. Vehicle Health**  
        Monitor component risks and diagnostics
        
        **2. Customer Engagement**  
        Review AI-powered conversations
        
        **3. Scheduling & Forecasting**  
        Optimize service capacity
        
        **4. MAP Prioritization**  
        Priority-based maintenance planning
        
        **5. Manufacturing Insights**  
        Quality analysis and RCA/CAPA
        
        **6. UEBA Monitoring**  
        Access control and security
        """)
        
        st.markdown("---")
        
        st.markdown("""
        ### 💡 Tips
        
        - Use the data regeneration button to refresh all insights
        - Each page has interactive visualizations
        - Hover over charts for detailed information
        - Export data using built-in Streamlit features
        """)
        
        st.markdown("---")
        st.caption("Built with Streamlit • Powered by AI")


if __name__ == "__main__":
    main()
