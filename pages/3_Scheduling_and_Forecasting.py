"""
Scheduling and Forecasting Page

Interactive dashboard for service capacity planning,
slot management, and demand forecasting.
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import random

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.loaders import load_json
from utils.charts import forecast_line_chart, capacity_heatmap


# Page config
st.set_page_config(
    page_title="Scheduling & Forecasting",
    page_icon="📅",
    layout="wide"
)


def main():
    """Scheduling and Forecasting Dashboard Page"""
    
    st.title("📅 Scheduling & Forecasting")
    st.markdown("Optimize service capacity and manage bookings efficiently")
    st.markdown("---")
    
    # Load data
    try:
        scheduling_data = load_json('data/scheduling.json')
        forecasting_data = load_json('data/forecasting.json')
    except FileNotFoundError:
        st.error("❌ Data files not found. Please regenerate data from the home page.")
        return
    
    # Service center selector
    slots = scheduling_data.get('slots', [])
    centers = list(set([slot['center'] for slot in slots]))
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        selected_center = st.selectbox(
            "🏢 Select Service Center",
            ["All Centers"] + sorted(centers),
            help="Choose a service center to view details"
        )
    
    # Summary metrics
    total_slots = scheduling_data.get('total_slots', 0)
    booked_slots = scheduling_data.get('booked_slots', 0)
    available_slots = scheduling_data.get('available_slots', 0)
    
    with col2:
        st.metric(
            label="Booked Slots",
            value=f"{booked_slots}/{total_slots}",
            delta=f"{(booked_slots/total_slots*100):.0f}% utilization" if total_slots > 0 else "0%"
        )
    
    with col3:
        st.metric(
            label="Available Slots",
            value=available_slots,
            delta=f"{(available_slots/total_slots*100):.0f}% capacity" if total_slots > 0 else "0%"
        )
    
    st.markdown("---")
    
    # Forecasting Section
    st.subheader("📈 Service Load Forecasting")
    
    tab1, tab2 = st.tabs(["📊 7-Day Forecast", "📊 30-Day Forecast"])
    
    with tab1:
        if 'forecast_7_days' in forecasting_data:
            col_a, col_b = st.columns([3, 1])
            
            with col_a:
                forecast_chart = forecast_line_chart(forecasting_data)
                st.plotly_chart(forecast_chart, use_container_width=True)
            
            with col_b:
                st.markdown("**📋 Summary**")
                
                forecast_7d = forecasting_data['forecast_7_days']
                avg_load = sum(f['predicted_load'] for f in forecast_7d) / len(forecast_7d)
                max_load = max(f['predicted_load'] for f in forecast_7d)
                
                st.metric("Avg Daily Load", f"{avg_load:.1f}")
                st.metric("Peak Load", f"{max_load}")
                
                st.info(f"""
                **Next 7 Days**
                
                Critical: {forecasting_data.get('critical_vehicles', 0)}  
                Moderate: {forecasting_data.get('moderate_vehicles', 0)}  
                Total: {forecasting_data.get('total_vehicles', 0)}
                """)
        else:
            st.info("7-day forecast data not available")
    
    with tab2:
        if 'forecast_30_days' in forecasting_data:
            # Create modified forecast dict for 30-day chart
            forecast_30d_dict = {
                'forecast_30_days': forecasting_data['forecast_30_days']
            }
            forecast_chart_30d = forecast_line_chart(forecast_30d_dict)
            st.plotly_chart(forecast_chart_30d, use_container_width=True)
            
            forecast_30d = forecasting_data['forecast_30_days']
            avg_load_30 = sum(f['predicted_load'] for f in forecast_30d) / len(forecast_30d)
            
            st.info(f"**30-Day Average Load:** {avg_load_30:.1f} vehicles/day")
        else:
            st.info("30-day forecast data not available")
    
    st.markdown("---")
    
    # Capacity Heatmap
    st.subheader("🗓️ Service Center Capacity Utilization")
    heatmap = capacity_heatmap(scheduling_data)
    st.plotly_chart(heatmap, use_container_width=True)
    
    st.markdown("---")
    
    # Slots and Bookings Section
    col_left, col_right = st.columns(2)
    
    # LEFT - Available Slots
    with col_left:
        st.subheader("🟢 Available Slots")
        
        # Filter slots
        if selected_center != "All Centers":
            filtered_slots = [s for s in slots if s['center'] == selected_center and s['available']]
        else:
            filtered_slots = [s for s in slots if s['available']]
        
        if filtered_slots:
            # Convert to DataFrame
            slots_df = pd.DataFrame(filtered_slots)
            slots_df = slots_df[['slot_id', 'center', 'date', 'time']]
            slots_df = slots_df.sort_values(['date', 'time'])
            
            # Display table
            st.dataframe(
                slots_df,
                hide_index=True,
                use_container_width=True,
                height=400
            )
            
            st.caption(f"Showing {len(filtered_slots)} available slots")
        else:
            st.info("No available slots for selected center")
    
    # RIGHT - Existing Bookings
    with col_right:
        st.subheader("📋 Existing Bookings")
        
        assignments = scheduling_data.get('assignments', [])
        
        # Filter assignments
        if selected_center != "All Centers":
            filtered_assignments = [a for a in assignments if a['center'] == selected_center]
        else:
            filtered_assignments = assignments
        
        if filtered_assignments:
            # Convert to DataFrame
            bookings_df = pd.DataFrame(filtered_assignments)
            bookings_df = bookings_df[['vehicle_id', 'center', 'date', 'time', 'priority']]
            bookings_df = bookings_df.sort_values(['date', 'time'])
            
            # Add color coding for priority
            def highlight_priority(row):
                if row['priority'] == 'URGENT':
                    return ['background-color: #ffebee'] * len(row)
                elif row['priority'] == 'HIGH':
                    return ['background-color: #fff3e0'] * len(row)
                else:
                    return [''] * len(row)
            
            styled_df = bookings_df.style.apply(highlight_priority, axis=1)
            
            st.dataframe(
                styled_df,
                hide_index=True,
                use_container_width=True,
                height=400
            )
            
            st.caption(f"Showing {len(filtered_assignments)} bookings")
        else:
            st.info("No bookings for selected center")
    
    st.markdown("---")
    
    # Parts Availability Section
    st.subheader("🔧 Parts Availability Status")
    
    # Generate sample parts availability
    parts_data = [
        {"part": "Battery", "stock": random.randint(15, 50), "min_stock": 10, "status": "✅ In Stock"},
        {"part": "Brake Pads", "stock": random.randint(20, 60), "min_stock": 15, "status": "✅ In Stock"},
        {"part": "Air Filter", "stock": random.randint(25, 80), "min_stock": 20, "status": "✅ In Stock"},
        {"part": "Engine Oil (L)", "stock": random.randint(100, 300), "min_stock": 50, "status": "✅ In Stock"},
        {"part": "Coolant (L)", "stock": random.randint(30, 100), "min_stock": 25, "status": "✅ In Stock"},
        {"part": "Tyres", "stock": random.randint(10, 40), "min_stock": 12, "status": "✅ In Stock"},
        {"part": "Spark Plugs", "stock": random.randint(5, 15), "min_stock": 8, "status": "⚠️ Low Stock"},
        {"part": "Wiper Blades", "stock": random.randint(3, 10), "min_stock": 5, "status": "⚠️ Low Stock"},
    ]
    
    # Adjust status based on actual stock
    for part in parts_data:
        if part['stock'] < part['min_stock']:
            part['status'] = "🔴 Critical"
        elif part['stock'] < part['min_stock'] * 1.5:
            part['status'] = "⚠️ Low Stock"
        else:
            part['status'] = "✅ In Stock"
    
    parts_df = pd.DataFrame(parts_data)
    
    # Display in columns
    col1, col2, col3, col4 = st.columns(4)
    
    for i, part in enumerate(parts_data):
        col = [col1, col2, col3, col4][i % 4]
        
        with col:
            # Determine color based on status
            if "Critical" in part['status']:
                color = "#ffebee"
                border_color = "#f44336"
            elif "Low" in part['status']:
                color = "#fff3e0"
                border_color = "#ff9800"
            else:
                color = "#e8f5e9"
                border_color = "#4caf50"
            
            st.markdown(f"""
            <div style='padding: 15px; margin: 5px; background-color: {color}; 
                 border-radius: 10px; border-left: 4px solid {border_color}; color: #333'>
                <h4 style='margin: 0; font-size: 0.9em; color: #333'>{part['part']}</h4>
                <p style='margin: 5px 0; font-size: 1.2em; color: #333'><strong>{part['stock']}</strong> units</p>
                <p style='margin: 0; font-size: 0.8em; color: #555'>{part['status']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Additional Info
    with st.expander("ℹ️ About Scheduling & Forecasting"):
        st.markdown("""
        ### Capacity Planning
        
        This dashboard helps optimize service center operations through:
        
        - **Demand Forecasting** - Predicts service load based on vehicle risk profiles
        - **Slot Management** - Real-time tracking of available and booked slots
        - **Utilization Metrics** - Monitor center capacity and efficiency
        - **Parts Planning** - Ensure inventory availability for scheduled services
        
        ### Forecasting Model
        
        The system uses historical telematics data combined with risk assessments to predict:
        - Daily service demand (7-day and 30-day windows)
        - Additional load from Critical and Moderate severity vehicles
        - Seasonal patterns and trends
        
        ### Priority Booking
        
        Vehicles are scheduled based on MAP (Maintenance Action Priority) scores:
        - 🔴 **URGENT** - Critical issues, immediate booking
        - 🟡 **HIGH** - Moderate issues, priority scheduling
        - 🟢 **NORMAL** - Routine maintenance
        """)


if __name__ == "__main__":
    main()
