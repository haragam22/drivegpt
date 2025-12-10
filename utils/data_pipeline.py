"""
Data Pipeline for Telematics Processing with Dynamic Risk Scoring

This module implements a sophisticated risk scoring system that uses:
- Rolling baselines (mean/std) per vehicle
- EWMA smoothing to reduce noise
- Z-score deviation detection
- Percent-change trend detection
- Hard real-world thresholds
- Hysteresis to prevent false alarms
- Evidence-based explanations
"""

import pandas as pd
import numpy as np
from pathlib import Path


# Hard threshold constants (industry standards)
ENGINE_CRITICAL = 95.0  # °C
ENGINE_SAFE = 85.0      # °C
BATTERY_CRITICAL = 12.0  # V
BATTERY_SAFE = 13.0      # V
BRAKE_CRITICAL = 0.7
BRAKE_SAFE = 0.5

# Detection parameters
ROLLING_WINDOW_HOURS = 6
EWMA_SPAN = 7
Z_SCORE_THRESHOLD = 2.0
PERCENT_CHANGE_THRESHOLD = 10.0  # 10% change
HYSTERESIS_WINDOWS = 2  # Require N consecutive high-risk windows


def load_telematics(filepath="data/telematics_sample_1000.csv"):
    """
    Load raw telematics CSV and parse timestamps.
    
    Args:
        filepath: Path to the telematics CSV file
        
    Returns:
        pd.DataFrame: Loaded telematics data with parsed timestamps
    """
    df = pd.read_csv(filepath)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(['vehicle_id', 'timestamp']).reset_index(drop=True)
    return df


def compute_rolling_baselines(vehicle_df, window='6h'):
    """
    Compute rolling mean and std for each metric per vehicle.
    
    Args:
        vehicle_df: DataFrame for a single vehicle
        window: Rolling window size (e.g., '6H' for 6 hours)
        
    Returns:
        pd.DataFrame: DataFrame with added rolling statistics
    """
    df = vehicle_df.copy()
    df = df.set_index('timestamp')
    
    # Metrics to track
    metrics = ['coolant_temp_c', 'battery_voltage', 'brake_wear']
    
    for metric in metrics:
        # Rolling mean and std
        df[f'{metric}_rolling_mean'] = df[metric].rolling(window=window, min_periods=1).mean()
        df[f'{metric}_rolling_std'] = df[metric].rolling(window=window, min_periods=1).std()
        
        # EWMA smoothing
        df[f'{metric}_ewma'] = df[metric].ewm(span=EWMA_SPAN, adjust=False).mean()
        
        # Z-score (deviation from rolling baseline)
        std = df[f'{metric}_rolling_std'].replace(0, 1)  # Avoid division by zero
        df[f'{metric}_zscore'] = (df[metric] - df[f'{metric}_rolling_mean']) / std
        
        # Percent change over last 3 readings
        df[f'{metric}_pct_change'] = df[metric].pct_change(periods=3) * 100
    
    return df.reset_index()


def compute_component_risk(vehicle_df):
    """
    Compute component risks using z-scores, trends, and hard thresholds.
    
    Args:
        vehicle_df: DataFrame with rolling baselines computed
        
    Returns:
        dict: Component risk scores and evidence
    """
    # Use the most recent readings for risk assessment
    latest = vehicle_df.iloc[-1]
    
    risk_scores = {}
    evidence = []
    
    # === ENGINE TEMPERATURE RISK ===
    engine_temp = latest['coolant_temp_c']
    engine_zscore = abs(latest['coolant_temp_c_zscore']) if not pd.isna(latest['coolant_temp_c_zscore']) else 0
    engine_pct_change = abs(latest['coolant_temp_c_pct_change']) if not pd.isna(latest['coolant_temp_c_pct_change']) else 0
    
    # Z-score component (70% weight)
    zscore_risk_engine = min(1.0, engine_zscore / (Z_SCORE_THRESHOLD * 2))
    
    # Percent change component (30% weight)
    pct_change_risk_engine = min(1.0, engine_pct_change / (PERCENT_CHANGE_THRESHOLD * 2))
    
    # Hard threshold component
    if engine_temp > ENGINE_CRITICAL:
        threshold_risk_engine = min(1.0, (engine_temp - ENGINE_SAFE) / 20)
        evidence.append("engine_above_critical")
    elif engine_temp > ENGINE_SAFE:
        threshold_risk_engine = (engine_temp - ENGINE_SAFE) / (ENGINE_CRITICAL - ENGINE_SAFE)
    else:
        threshold_risk_engine = 0.0
    
    # Combine: 70% z-score, 30% trend, plus threshold override
    engine_risk = max(
        0.7 * zscore_risk_engine + 0.3 * pct_change_risk_engine,
        threshold_risk_engine
    )
    
    if engine_zscore > Z_SCORE_THRESHOLD:
        evidence.append("engine_high_temp_spike")
    if engine_pct_change > PERCENT_CHANGE_THRESHOLD:
        evidence.append("engine_temp_rapid_increase")
    
    risk_scores['engine_risk'] = engine_risk
    
    # === BATTERY VOLTAGE RISK ===
    battery_voltage = latest['battery_voltage']
    battery_zscore = abs(latest['battery_voltage_zscore']) if not pd.isna(latest['battery_voltage_zscore']) else 0
    battery_pct_change = abs(latest['battery_voltage_pct_change']) if not pd.isna(latest['battery_voltage_pct_change']) else 0
    
    # Z-score component (70% weight)
    zscore_risk_battery = min(1.0, battery_zscore / (Z_SCORE_THRESHOLD * 2))
    
    # Percent change component (30% weight)
    pct_change_risk_battery = min(1.0, battery_pct_change / (PERCENT_CHANGE_THRESHOLD * 2))
    
    # Hard threshold component (inverted - lower is worse)
    if battery_voltage < BATTERY_CRITICAL:
        threshold_risk_battery = min(1.0, (BATTERY_SAFE - battery_voltage) / 2)
        evidence.append("battery_below_critical")
    elif battery_voltage < BATTERY_SAFE:
        threshold_risk_battery = (BATTERY_SAFE - battery_voltage) / (BATTERY_SAFE - BATTERY_CRITICAL)
    else:
        threshold_risk_battery = 0.0
    
    # Combine
    battery_risk = max(
        0.7 * zscore_risk_battery + 0.3 * pct_change_risk_battery,
        threshold_risk_battery
    )
    
    if battery_zscore > Z_SCORE_THRESHOLD:
        evidence.append("battery_voltage_abnormal")
    if battery_pct_change > PERCENT_CHANGE_THRESHOLD:
        evidence.append("battery_voltage_drop")
    
    risk_scores['battery_risk'] = battery_risk
    
    # === BRAKE WEAR RISK ===
    brake_wear = latest['brake_wear']
    brake_zscore = abs(latest['brake_wear_zscore']) if not pd.isna(latest['brake_wear_zscore']) else 0
    brake_pct_change = abs(latest['brake_wear_pct_change']) if not pd.isna(latest['brake_wear_pct_change']) else 0
    
    # Z-score component (70% weight)
    zscore_risk_brake = min(1.0, brake_zscore / (Z_SCORE_THRESHOLD * 2))
    
    # Percent change component (30% weight)
    pct_change_risk_brake = min(1.0, brake_pct_change / (PERCENT_CHANGE_THRESHOLD * 2))
    
    # Hard threshold component
    if brake_wear > BRAKE_CRITICAL:
        threshold_risk_brake = min(1.0, (brake_wear - BRAKE_SAFE) / 0.3)
        evidence.append("brake_wear_critical")
    elif brake_wear > BRAKE_SAFE:
        threshold_risk_brake = (brake_wear - BRAKE_SAFE) / (BRAKE_CRITICAL - BRAKE_SAFE)
    else:
        threshold_risk_brake = 0.0
    
    # Combine
    brake_risk = max(
        0.7 * zscore_risk_brake + 0.3 * pct_change_risk_brake,
        threshold_risk_brake
    )
    
    if brake_zscore > Z_SCORE_THRESHOLD:
        evidence.append("brake_wear_abnormal")
    if brake_pct_change > PERCENT_CHANGE_THRESHOLD:
        evidence.append("brake_wear_accelerating")
    
    risk_scores['brake_risk'] = brake_risk
    
    # === TYRE RISK (based on mileage) ===
    total_km = latest['odometer_km'] - vehicle_df.iloc[0]['odometer_km']
    tyre_risk = min(1.0, total_km / 50000)
    
    if total_km > 40000:
        evidence.append("high_mileage_tyre_replacement_due")
    
    risk_scores['tyre_risk'] = tyre_risk
    
    return risk_scores, evidence


def compute_overall_severity(risk_scores):
    """
    Compute overall severity from component risks with weighted average.
    
    Weights:
    - Battery: 35%
    - Engine: 35%
    - Brakes: 20%
    - Tyres: 10%
    
    Args:
        risk_scores: Dict of component risk scores
        
    Returns:
        tuple: (overall_risk, severity_label)
    """
    # Weighted average
    overall_risk = (
        risk_scores['battery_risk'] * 0.35 +
        risk_scores['engine_risk'] * 0.35 +
        risk_scores['brake_risk'] * 0.20 +
        risk_scores['tyre_risk'] * 0.10
    )
    
    # Critical override: any single component > 0.85 = instant critical
    if any(risk > 0.85 for risk in [
        risk_scores['battery_risk'],
        risk_scores['engine_risk'],
        risk_scores['brake_risk']
    ]):
        severity = "Critical"
        overall_risk = max(overall_risk, 0.85)
    elif overall_risk >= 0.7:
        severity = "Critical"
    elif overall_risk >= 0.3:
        severity = "Moderate"
    else:
        severity = "Routine"
    
    return overall_risk, severity


def apply_hysteresis(vehicle_history, current_severity, window_size=HYSTERESIS_WINDOWS):
    """
    Apply hysteresis to prevent false alarms from single spikes.
    
    Args:
        vehicle_history: List of previous severity assessments
        current_severity: Current severity assessment
        window_size: Number of consecutive windows required
        
    Returns:
        str: Final severity after hysteresis
    """
    # Add current to history
    vehicle_history.append(current_severity)
    
    # Keep only last N windows
    if len(vehicle_history) > window_size:
        vehicle_history.pop(0)
    
    # Require N consecutive high-risk windows for Critical/Moderate
    if len(vehicle_history) >= window_size:
        if all(s == "Critical" for s in vehicle_history[-window_size:]):
            return "Critical"
        elif all(s in ["Critical", "Moderate"] for s in vehicle_history[-window_size:]):
            return "Moderate"
    
    # Otherwise return current (or downgrade)
    return current_severity if len(vehicle_history) < window_size else "Routine"


def compute_risk_profiles(filepath="data/telematics_sample_1000.csv"):
    """
    Complete pipeline with dynamic risk scoring.
    
    Args:
        filepath: Path to the telematics CSV file
        
    Returns:
        list: List of dictionaries containing vehicle risk profiles
    """
    # Load data
    df = load_telematics(filepath)
    
    risk_profiles = []
    vehicle_history = {}  # Track severity history per vehicle
    
    # Process each vehicle
    for vehicle_id in df['vehicle_id'].unique():
        vehicle_df = df[df['vehicle_id'] == vehicle_id].copy()
        
        # Skip if insufficient data
        if len(vehicle_df) < 3:
            continue
        
        # Compute rolling baselines
        vehicle_df = compute_rolling_baselines(vehicle_df)
        
        # Compute component risks
        risk_scores, evidence = compute_component_risk(vehicle_df)
        
        # Compute overall severity
        overall_risk, severity = compute_overall_severity(risk_scores)
        
        # Apply hysteresis
        if vehicle_id not in vehicle_history:
            vehicle_history[vehicle_id] = []
        
        final_severity = apply_hysteresis(vehicle_history[vehicle_id], severity)
        
        # Add metrics for display
        latest = vehicle_df.iloc[-1]
        
        risk_profiles.append({
            'vehicle_id': vehicle_id,
            'risk_profile': {
                'overall_risk': overall_risk,
                **risk_scores
            },
            'severity': final_severity,
            'evidence': evidence if evidence else ["All systems normal"],
            'metrics': {
                'engine_temp': latest['coolant_temp_c'],
                'battery_voltage': latest['battery_voltage'],
                'brake_wear': latest['brake_wear'],
                'total_km': latest['odometer_km'] - vehicle_df.iloc[0]['odometer_km']
            }
        })
    
    # Sort by overall risk (highest first)
    risk_profiles.sort(
        key=lambda x: x['risk_profile']['overall_risk'],
        reverse=True
    )
    
    return risk_profiles


if __name__ == "__main__":
    # Test the pipeline
    print("Testing dynamic risk scoring pipeline...\n")
    
    profiles = compute_risk_profiles()
    
    print(f"Processed {len(profiles)} vehicles\n")
    print("=" * 80)
    print("Top 5 highest risk vehicles:")
    print("=" * 80)
    
    for i, profile in enumerate(profiles[:5], 1):
        print(f"\n{i}. Vehicle: {profile['vehicle_id']}")
        print(f"   Severity: {profile['severity']}")
        print(f"   Overall Risk: {profile['risk_profile']['overall_risk']:.3f}")
        print(f"   Component Risks:")
        print(f"      - Engine: {profile['risk_profile']['engine_risk']:.3f}")
        print(f"      - Battery: {profile['risk_profile']['battery_risk']:.3f}")
        print(f"      - Brakes: {profile['risk_profile']['brake_risk']:.3f}")
        print(f"      - Tyres: {profile['risk_profile']['tyre_risk']:.3f}")
        print(f"   Metrics:")
        print(f"      - Engine temp: {profile['metrics']['engine_temp']:.1f}°C")
        print(f"      - Battery: {profile['metrics']['battery_voltage']:.2f}V")
        print(f"      - Brake wear: {profile['metrics']['brake_wear']:.2f}")
        print(f"      - Mileage: {profile['metrics']['total_km']:.0f} km")
        print(f"   Evidence: {', '.join(profile['evidence'])}")
