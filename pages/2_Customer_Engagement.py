"""
Customer Engagement Page

Interactive dashboard for viewing customer conversations
and generating AI service advisor scripts.
"""

import streamlit as st
import sys
from pathlib import Path
import random

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.loaders import load_json


# Page config
st.set_page_config(
    page_title="Customer Engagement",
    page_icon="💬",
    layout="wide"
)


def generate_service_script(vehicle_id, diagnosis_data):
    """Generate friendly AI service advisor script"""
    
    # Find diagnosis for this vehicle
    vehicle_diag = next(
        (d for d in diagnosis_data if d['vehicle_id'] == vehicle_id),
        None
    )
    
    if not vehicle_diag:
        return "Hello! How can I assist you with your vehicle today?"
    
    severity = vehicle_diag['severity']
    diagnosis = vehicle_diag['diagnosis']
    rul_days = vehicle_diag['rul_days']
    cost = vehicle_diag['estimated_cost']
    
    # Generate friendly scripts based on severity
    if severity == "Critical":
        scripts = [
            f"Hi! I noticed your vehicle needs immediate attention. We've detected {diagnosis.lower()} that requires service right away. Your vehicle has approximately {rul_days} days of safe operation remaining. Can we schedule you for service today?",
            f"Hello! I'm reaching out because your vehicle's diagnostics show {diagnosis.lower()} that needs urgent care. For your safety, we recommend service within the next {rul_days} days. The estimated cost is ₹{cost:,}. Would you like to book an appointment?",
            f"Good day! Your vehicle health monitoring has flagged {diagnosis.lower()} as a critical issue. We want to ensure your safety - can we get you scheduled for service this week? Estimated time: {vehicle_diag['service_time_hours']} hours."
        ]
    elif severity == "Moderate":
        scripts = [
            f"Hi there! Your vehicle is showing signs of {diagnosis.lower()}. While not urgent, we recommend addressing this within {rul_days} days to prevent further wear. Estimated cost: ₹{cost:,}. Shall I help you schedule?",
            f"Hello! Just a friendly reminder - your vehicle could benefit from service soon. We've noticed {diagnosis.lower()} developing. You have about {rul_days} days, but early service can save you money in the long run!",
            f"Good day! Your vehicle's health check indicates {diagnosis.lower()}. No immediate danger, but scheduling service in the next few weeks would be wise. Can I help you find a convenient time?"
        ]
    else:
        scripts = [
            f"Hi! Your vehicle is in great shape overall! Just a routine reminder that maintenance is due in {rul_days} days. Would you like to pre-book to avoid waiting?",
            f"Hello! Everything looks good with your vehicle. We recommend routine service in about {rul_days} days. Want to secure a preferred time slot now?",
            f"Good day! Your vehicle health is excellent. Let's keep it that way with routine maintenance in the coming weeks. Shall I check available appointments?"
        ]
    
    return random.choice(scripts)


def main():
    """Customer Engagement Dashboard Page"""
    
    st.title("💬 Customer Engagement")
    st.markdown("AI-powered service conversations and recommendations")
    st.markdown("---")
    
    # Load data
    try:
        engagement_logs = load_json('data/engagement_logs.json')
        diagnosis_data = load_json('data/diagnosis.json')
    except FileNotFoundError:
        st.error("❌ Data files not found. Please regenerate data from the home page.")
        return
    
    # Vehicle selector
    vehicle_ids = [log['vehicle_id'] for log in engagement_logs]
    
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_vehicle = st.selectbox(
            "🚗 Select Vehicle",
            vehicle_ids,
            help="Choose a vehicle to view conversation history"
        )
    
    # Find selected vehicle conversation
    vehicle_log = next(
        (log for log in engagement_logs if log['vehicle_id'] == selected_vehicle),
        None
    )
    
    if not vehicle_log:
        st.warning("No conversation found for this vehicle")
        return
    
    # Show severity badge
    severity = vehicle_log['severity']
    severity_colors = {
        'Critical': '🔴',
        'Moderate': '🟡',
        'Routine': '🟢'
    }
    
    with col2:
        st.metric(
            label="Service Priority",
            value=f"{severity_colors.get(severity, '⚪')} {severity}"
        )
    
    st.markdown("---")
    
    # Main layout: 2 columns
    left_col, right_col = st.columns([3, 2])
    
    # LEFT COLUMN - Conversation Timeline
    with left_col:
        st.subheader("📱 Conversation Timeline")
        
        messages = vehicle_log.get('messages', [])
        
        # Display messages in chat bubble style
        for msg in messages:
            role = msg['role']
            message = msg['message']
            
            if role == 'agent':
                # Agent message (left-aligned, blue)
                st.markdown(f"""
                <div style='margin: 10px 0; padding: 12px 18px; background-color: #E3F2FD; 
                     border-radius: 18px; max-width: 80%; display: inline-block;
                     border: 1px solid #2196F3; color: #0D47A1'>
                    <strong style='color: #0D47A1'>🤖 Service Advisor</strong><br/>
                    <span style='color: #1565C0'>{message}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                # User message (right-aligned, green)
                st.markdown(f"""
                <div style='margin: 10px 0; padding: 12px 18px; background-color: #E8F5E9; 
                     border-radius: 18px; max-width: 80%; display: inline-block; float: right;
                     border: 1px solid #4CAF50; color: #1B5E20'>
                    <strong style='color: #1B5E20'>👤 Customer</strong><br/>
                    <span style='color: #2E7D32'>{message}</span>
                </div>
                <div style='clear: both'></div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br/><br/>", unsafe_allow_html=True)
    
    # RIGHT COLUMN - AI Script Generator
    with right_col:
        st.subheader("🤖 AI Service Advisor Script")
        
        st.markdown("""
        Generate a personalized service recommendation script based on 
        the vehicle's current health status.
        """)
        
        # Store script in session state
        if 'generated_script' not in st.session_state:
            st.session_state.generated_script = generate_service_script(
                selected_vehicle, 
                diagnosis_data
            )
        
        # Regenerate button
        if st.button("🔄 Regenerate Script", use_container_width=True):
            st.session_state.generated_script = generate_service_script(
                selected_vehicle,
                diagnosis_data
            )
            st.rerun()
        
        st.markdown("###")
        
        # Display generated script
        st.markdown("""
        <div style='padding: 20px; background-color: #F5F5F5; border-radius: 10px;
             border-left: 4px solid #2196F3; margin: 10px 0; color: #333'>
        """, unsafe_allow_html=True)
        
        st.markdown(f"**<span style='color: #333'>Suggested Script:</span>**", unsafe_allow_html=True)
        st.write(st.session_state.generated_script)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("###")
        
        # Quick Actions
        st.markdown("**⚡ Quick Actions**")
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📞 Call Customer", use_container_width=True):
                st.success("Initiating call...")
        
        with col_b:
            if st.button("📧 Send Email", use_container_width=True):
                st.success("Email sent!")
        
        st.markdown("###")
        
        # Customer Info Card
        st.markdown("**👤 Customer Profile**")
        
        # Get diagnosis for additional info
        vehicle_diag = next(
            (d for d in diagnosis_data if d['vehicle_id'] == selected_vehicle),
            None
        )
        
        if vehicle_diag:
            st.info(f"""
            **Vehicle:** {selected_vehicle}  
            **Issue:** {vehicle_diag['diagnosis']}  
            **Urgency:** {vehicle_diag['urgency']}  
            **Est. Cost:** ₹{vehicle_diag['estimated_cost']:,}  
            **Service Time:** {vehicle_diag['service_time_hours']} hours
            """)
    
    st.markdown("---")
    
    # Engagement Tips
    with st.expander("💡 Best Practices for Customer Engagement"):
        st.markdown("""
        ### Effective Communication Tips
        
        1. **Be Empathetic** - Acknowledge customer concerns and show understanding
        2. **Be Clear** - Explain technical issues in simple, non-jargon language
        3. **Be Proactive** - Reach out before issues become critical
        4. **Offer Solutions** - Always provide next steps and options
        5. **Follow Up** - Check in after service to ensure satisfaction
        
        ### Script Customization
        
        The AI generates scripts based on:
        - Vehicle health severity (Critical/Moderate/Routine)
        - Remaining useful life (RUL)
        - Estimated repair costs
        - Customer history and preferences
        
        Feel free to customize the generated script to match your personal style!
        """)


if __name__ == "__main__":
    main()
