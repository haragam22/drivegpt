"""
Chart Utilities

Plotly-based visualization functions for the dashboard.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np


def risk_bar_chart(risk_profile):
    """
    Create a bar chart showing component risk scores.
    
    Args:
        risk_profile: Dict containing risk scores
        
    Returns:
        plotly.graph_objects.Figure
    """
    # Extract component risks (exclude overall_risk)
    components = []
    risks = []
    
    for key, value in risk_profile.items():
        if key != 'overall_risk':
            component_name = key.replace('_risk', '').replace('_', ' ').title()
            components.append(component_name)
            risks.append(value)
    
    # Create color scale based on risk level
    colors = ['#2ecc71' if r < 0.3 else '#f39c12' if r < 0.7 else '#e74c3c' for r in risks]
    
    fig = go.Figure(data=[
        go.Bar(
            x=components,
            y=risks,
            marker=dict(
                color=colors,
                line=dict(color='rgba(0,0,0,0.3)', width=1)
            ),
            text=[f'{r:.2%}' for r in risks],
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title='Component Risk Scores',
        xaxis_title='Component',
        yaxis_title='Risk Score',
        yaxis=dict(range=[0, 1.1]),
        template='plotly_white',
        showlegend=False,
        height=400
    )
    
    return fig


def component_trend_line(telematics_df):
    """
    Create trend lines for component metrics over time.
    
    Args:
        telematics_df: DataFrame with telematics data
        
    Returns:
        plotly.graph_objects.Figure
    """
    # Ensure timestamp is datetime
    df = telematics_df.copy()
    if 'timestamp' not in df.columns:
        return go.Figure()
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    
    fig = go.Figure()
    
    # Add engine temperature trend
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['coolant_temp_c'],
        mode='lines',
        name='Engine Temp (°C)',
        line=dict(color='#e74c3c', width=2)
    ))
    
    # Add battery voltage trend (scaled for visibility)
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['battery_voltage'] * 7,  # Scale up for visibility
        mode='lines',
        name='Battery Voltage (×7)',
        line=dict(color='#3498db', width=2),
        yaxis='y2'
    ))
    
    # Add brake wear trend (scaled)
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['brake_wear'] * 100,  # Convert to percentage
        mode='lines',
        name='Brake Wear (%)',
        line=dict(color='#f39c12', width=2),
        yaxis='y3'
    ))
    
    fig.update_layout(
        title='Component Metrics Over Time',
        xaxis_title='Time',
        yaxis=dict(title='Engine Temp (°C)', side='left'),
        yaxis2=dict(title='Battery (V×7)', overlaying='y', side='right'),
        yaxis3=dict(title='Brake Wear (%)', overlaying='y', side='right', position=0.95),
        template='plotly_white',
        hovermode='x unified',
        height=450,
        legend=dict(x=0.01, y=0.99)
    )
    
    return fig


def forecast_line_chart(forecast_dict):
    """
    Create a line chart for service load forecasting.
    
    Args:
        forecast_dict: Dict with forecast data including 'forecast_7_days' or 'forecast_30_days'
        
    Returns:
        plotly.graph_objects.Figure
    """
    # Use 7-day forecast if available, otherwise 30-day
    if 'forecast_7_days' in forecast_dict:
        forecast_data = forecast_dict['forecast_7_days']
        title = '7-Day Service Load Forecast'
    elif 'forecast_30_days' in forecast_dict:
        forecast_data = forecast_dict['forecast_30_days']
        title = '30-Day Service Load Forecast'
    else:
        return go.Figure()
    
    dates = [item['date'] for item in forecast_data]
    loads = [item['predicted_load'] for item in forecast_data]
    
    fig = go.Figure()
    
    # Add forecasted load
    fig.add_trace(go.Scatter(
        x=dates,
        y=loads,
        mode='lines+markers',
        name='Predicted Load',
        line=dict(color='#3498db', width=3),
        marker=dict(size=6),
        fill='tozeroy',
        fillcolor='rgba(52, 152, 219, 0.2)'
    ))
    
    # Add average line
    avg_load = np.mean(loads)
    fig.add_hline(
        y=avg_load,
        line_dash="dash",
        line_color="#95a5a6",
        annotation_text=f"Avg: {avg_load:.1f}",
        annotation_position="right"
    )
    
    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title='Service Load (vehicles)',
        template='plotly_white',
        hovermode='x unified',
        height=400,
        showlegend=True
    )
    
    fig.update_xaxes(tickangle=-45)
    
    return fig


def capacity_heatmap(center_data):
    """
    Create a heatmap showing service center capacity utilization.
    
    Args:
        center_data: Dict or list with scheduling/slot data
        
    Returns:
        plotly.graph_objects.Figure
    """
    # Extract slots data
    if isinstance(center_data, dict) and 'slots' in center_data:
        slots = center_data['slots']
    elif isinstance(center_data, list):
        slots = center_data
    else:
        return go.Figure()
    
    # Create DataFrame for heatmap
    df = pd.DataFrame(slots)
    
    # Create pivot table: centers × dates
    if 'center' in df.columns and 'date' in df.columns:
        # Count booked slots (where available = False)
        pivot = df.groupby(['center', 'date']).agg({
            'available': lambda x: sum(~x)  # Count non-available (booked)
        }).reset_index()
        pivot = pivot.pivot(index='center', columns='date', values='available')
        pivot = pivot.fillna(0)
    else:
        return go.Figure()
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='RdYlGn_r',  # Red for high, green for low
        text=pivot.values,
        texttemplate='%{text}',
        textfont={"size": 12},
        colorbar=dict(title="Booked Slots")
    ))
    
    fig.update_layout(
        title='Service Center Capacity Utilization',
        xaxis_title='Date',
        yaxis_title='Service Center',
        template='plotly_white',
        height=400
    )
    
    return fig


def priority_bar_chart(map_scores):
    """
    Create a bar chart showing vehicle priority scores.
    
    Args:
        map_scores: List of MAP score dicts
        
    Returns:
        plotly.graph_objects.Figure
    """
    # Sort by priority score descending
    sorted_scores = sorted(map_scores, key=lambda x: x['priority_score'], reverse=True)
    
    # Take top 10
    top_scores = sorted_scores[:10]
    
    vehicle_ids = [item['vehicle_id'] for item in top_scores]
    scores = [item['priority_score'] for item in top_scores]
    categories = [item['category'] for item in top_scores]
    
    # Color by category
    color_map = {
        'URGENT': '#e74c3c',
        'HIGH': '#f39c12',
        'NORMAL': '#2ecc71'
    }
    colors = [color_map.get(cat, '#95a5a6') for cat in categories]
    
    fig = go.Figure(data=[
        go.Bar(
            x=vehicle_ids,
            y=scores,
            marker=dict(
                color=colors,
                line=dict(color='rgba(0,0,0,0.3)', width=1)
            ),
            text=[f'{s:.1f}' for s in scores],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Score: %{y:.1f}<extra></extra>'
        )
    ])
    
    # Add category zones
    fig.add_hline(y=80, line_dash="dash", line_color="red", 
                  annotation_text="URGENT Threshold", annotation_position="left")
    fig.add_hline(y=50, line_dash="dash", line_color="orange",
                  annotation_text="HIGH Threshold", annotation_position="left")
    
    fig.update_layout(
        title='Top 10 Vehicle Priorities (MAP Scores)',
        xaxis_title='Vehicle ID',
        yaxis_title='Priority Score',
        template='plotly_white',
        showlegend=False,
        height=450
    )
    
    return fig


if __name__ == "__main__":
    # Test charts with sample data
    print("Testing chart utilities...")
    
    # Test risk bar chart
    sample_risk = {
        'engine_risk': 0.45,
        'battery_risk': 0.72,
        'brake_risk': 0.31,
        'tyre_risk': 0.15,
        'overall_risk': 0.48
    }
    
    fig = risk_bar_chart(sample_risk)
    print("✓ Risk bar chart created")
    
    # Test priority bar chart
    sample_map = [
        {'vehicle_id': 'V01', 'priority_score': 85.5, 'category': 'URGENT'},
        {'vehicle_id': 'V02', 'priority_score': 72.3, 'category': 'HIGH'},
        {'vehicle_id': 'V03', 'priority_score': 45.2, 'category': 'NORMAL'}
    ]
    
    fig = priority_bar_chart(sample_map)
    print("✓ Priority bar chart created")
    
    print("\nAll chart utilities working!")
