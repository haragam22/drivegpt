"""
MAP Prioritization Page

Interactive dashboard for Maintenance Action Priority scoring
with adjustable weights and scheduling simulation.
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.loaders import load_json
from utils.charts import priority_bar_chart


# Page config
st.set_page_config(
    page_title="MAP Prioritization",
    page_icon="🎯",
    layout="wide"
)


def recalculate_priority(vehicle_data, severity_weight, tier_weight, fleet_weight):
    """
    Recalculate priority score with custom weights.
    
    Args:
        vehicle_data: Original vehicle MAP data
        severity_weight: Weight for base risk score (0-100)
        tier_weight: Weight for customer tier bonus (0-100)
        fleet_weight: Weight for fleet bonus (0-100)
    
    Returns:
        float: New priority score
    """
    # Get base components
    base_risk = vehicle_data['base_risk_score']
    tier_bonus = vehicle_data['tier_bonus']
    fleet_bonus = vehicle_data['fleet_bonus']
    
    # Normalize weights to percentages
    total_weight = severity_weight + tier_weight + fleet_weight
    if total_weight == 0:
        total_weight = 1
    
    severity_pct = severity_weight / total_weight
    tier_pct = tier_weight / total_weight
    fleet_pct = fleet_weight / total_weight
    
    # Calculate new score
    new_score = (
        base_risk * severity_pct +
        tier_bonus * tier_pct +
        fleet_bonus * fleet_pct
    )
    
    return new_score


def categorize_priority(score):
    """Categorize priority based on score"""
    if score > 80:
        return "URGENT", "🔴"
    elif score > 50:
        return "HIGH", "🟡"
    else:
        return "NORMAL", "🟢"


def main():
    """MAP Prioritization Dashboard Page"""
    
    st.title("🎯 MAP Prioritization")
    st.markdown("Maintenance Action Priority - Optimize service scheduling based on customizable scoring")
    st.markdown("---")
    
    # Load data
    try:
        map_scores = load_json('data/map_scores.json')
    except FileNotFoundError:
        st.error("❌ Data files not found. Please regenerate data from the home page.")
        return
    
    # Sidebar - Weight Adjustment
    st.sidebar.markdown("## ⚙️ Priority Weight Configuration")
    st.sidebar.markdown("Adjust weights to customize priority scoring:")
    
    severity_weight = st.sidebar.slider(
        "🔴 Severity Weight",
        min_value=0,
        max_value=100,
        value=70,
        help="Weight for vehicle risk severity"
    )
    
    tier_weight = st.sidebar.slider(
        "⭐ Customer Tier Weight",
        min_value=0,
        max_value=100,
        value=20,
        help="Weight for customer tier bonus (GOLD/SILVER/BRONZE)"
    )
    
    fleet_weight = st.sidebar.slider(
        "🚙 Fleet Weight",
        min_value=0,
        max_value=100,
        value=10,
        help="Weight for fleet vehicle bonus"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info(f"""
    **Current Distribution:**
    - Severity: {severity_weight}%
    - Tier: {tier_weight}%
    - Fleet: {fleet_weight}%
    
    Total: {severity_weight + tier_weight + fleet_weight}
    """)
    
    # Recalculate scores with new weights
    recalculated_data = []
    for vehicle in map_scores:
        new_score = recalculate_priority(vehicle, severity_weight, tier_weight, fleet_weight)
        category, icon = categorize_priority(new_score)
        
        recalculated_data.append({
            'vehicle_id': vehicle['vehicle_id'],
            'original_score': vehicle['priority_score'],
            'new_score': new_score,
            'category': category,
            'icon': icon,
            'severity': vehicle['severity'],
            'customer_tier': vehicle['customer_tier'],
            'is_fleet': vehicle['is_fleet'],
            'base_risk_score': vehicle['base_risk_score'],
            'tier_bonus': vehicle['tier_bonus'],
            'fleet_bonus': vehicle['fleet_bonus']
        })
    
    # Sort by new score
    recalculated_data.sort(key=lambda x: x['new_score'], reverse=True)
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    urgent_count = sum(1 for v in recalculated_data if v['category'] == 'URGENT')
    high_count = sum(1 for v in recalculated_data if v['category'] == 'HIGH')
    normal_count = sum(1 for v in recalculated_data if v['category'] == 'NORMAL')
    
    with col1:
        st.metric("Total Vehicles", len(recalculated_data))
    with col2:
        st.metric("🔴 Urgent", urgent_count)
    with col3:
        st.metric("🟡 High", high_count)
    with col4:
        st.metric("🟢 Normal", normal_count)
    
    st.markdown("---")
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["📊 Priority Table", "📈 Priority Chart", "🗓️ Scheduling Simulation"])
    
    with tab1:
        st.subheader("Priority Rankings (Recalculated)")
        
        # Create DataFrame
        display_df = pd.DataFrame([{
            'Rank': i + 1,
            'Vehicle ID': v['vehicle_id'],
            'Priority': f"{v['icon']} {v['category']}",
            'Score': f"{v['new_score']:.1f}",
            'Original': f"{v['original_score']:.1f}",
            'Severity': v['severity'],
            'Tier': v['customer_tier'],
            'Fleet': '✓' if v['is_fleet'] else '✗'
        } for i, v in enumerate(recalculated_data)])
        
        # Color coding function
        def highlight_priority(row):
            if '🔴' in str(row['Priority']):
                return ['background-color: #ffebee'] * len(row)
            elif '🟡' in str(row['Priority']):
                return ['background-color: #fff3e0'] * len(row)
            else:
                return [''] * len(row)
        
        styled_df = display_df.style.apply(highlight_priority, axis=1)
        
        st.dataframe(
            styled_df,
            hide_index=True,
            use_container_width=True,
            height=500
        )
        
        st.caption(f"Showing {len(recalculated_data)} vehicles sorted by recalculated priority")
    
    with tab2:
        st.subheader("Top 10 Priority Vehicles")
        
        # Use top 10 for chart
        top_10 = recalculated_data[:10]
        
        # Convert to format expected by chart function
        chart_data = [{
            'vehicle_id': v['vehicle_id'],
            'priority_score': v['new_score'],
            'category': v['category']
        } for v in top_10]
        
        chart = priority_bar_chart(chart_data)
        st.plotly_chart(chart, use_container_width=True)
        
        st.info("""
        **Chart Legend:**
        - 🔴 Red bars: URGENT (>80)
        - 🟡 Orange bars: HIGH (>50)
        - 🟢 Green bars: NORMAL (≤50)
        """)
    
    with tab3:
        st.subheader("🗓️ Scheduling Order Simulation")
        
        st.markdown("""
        Based on the current weight configuration, vehicles would be scheduled in the following order.
        This simulation assumes 4 service bays with 2-hour service windows.
        """)
        
        # Simulate scheduling
        bays = 4
        hours_per_service = 2
        services_per_day = 8 // hours_per_service  # 8-hour workday
        
        schedule_simulation = []
        current_day = 1
        current_slot = 1
        
        for i, vehicle in enumerate(recalculated_data):
            # Calculate day and slot
            services_today = (i % (bays * services_per_day))
            
            if i > 0 and services_today == 0:
                current_day += 1
                current_slot = 1
            
            bay = (i % bays) + 1
            time_slot = ((i // bays) % services_per_day) * hours_per_service + 9  # Start at 9 AM
            
            schedule_simulation.append({
                'Day': current_day,
                'Time': f"{time_slot:02d}:00",
                'Bay': bay,
                'Vehicle': vehicle['vehicle_id'],
                'Priority': f"{vehicle['icon']} {vehicle['category']}",
                'Score': f"{vehicle['new_score']:.1f}"
            })
        
        # Display simulation for first 20 services
        sim_df = pd.DataFrame(schedule_simulation[:20])
        
        st.dataframe(
            sim_df,
            hide_index=True,
            use_container_width=True,
            height=400
        )
        
        st.caption(f"Showing first 20 services out of {len(recalculated_data)} total")
        
        # Summary stats
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Days Required", max(s['Day'] for s in schedule_simulation))
        with col_b:
            st.metric("Services per Day", bays * services_per_day)
        with col_c:
            st.metric("Service Bays", bays)
    
    st.markdown("---")
    
    # Comparison Section
    with st.expander("📊 Score Comparison: Original vs Recalculated"):
        st.markdown("### Impact of Weight Adjustment")
        
        # Show vehicles with biggest changes
        comparison = []
        for v in recalculated_data:
            diff = v['new_score'] - v['original_score']
            comparison.append({
                'Vehicle': v['vehicle_id'],
                'Original Score': f"{v['original_score']:.1f}",
                'New Score': f"{v['new_score']:.1f}",
                'Change': f"{diff:+.1f}",
                'Details': f"Tier: {v['customer_tier']}, Fleet: {'Yes' if v['is_fleet'] else 'No'}"
            })
        
        # Sort by absolute change
        comparison.sort(key=lambda x: abs(float(x['Change'])), reverse=True)
        comp_df = pd.DataFrame(comparison[:10])
        
        st.dataframe(comp_df, hide_index=True, use_container_width=True)
        st.caption("Top 10 vehicles with biggest score changes")
    
    # Additional Info
    with st.expander("ℹ️ About MAP Prioritization"):
        st.markdown("""
        ### Maintenance Action Priority (MAP)
        
        MAP scoring helps optimize service scheduling by considering multiple factors:
        
        **Score Components:**
        1. **Base Risk Score (0-100)** - Vehicle health severity from telematics analysis
        2. **Customer Tier Bonus** - GOLD (+15), SILVER (+10), BRONZE (+5), REGULAR (0)
        3. **Fleet Bonus** - Fleet vehicles (+10) for business continuity
        
        **Default Weights:**
        - Severity: 70% (most important)
        - Customer Tier: 20% (loyalty consideration)
        - Fleet: 10% (business impact)
        
        **Priority Categories:**
        - 🔴 **URGENT** (>80): Schedule immediately
        - 🟡 **HIGH** (50-80): Schedule within 1-2 days
        - 🟢 **NORMAL** (≤50): Regular scheduling
        
        **Use the sliders** to adjust weights based on business priorities!
        """)


if __name__ == "__main__":
    main()
