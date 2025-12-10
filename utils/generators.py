"""
Synthetic Data Generators

This module generates synthetic data for various dashboard modules
based on telematics risk profiles.
"""

import json
import random
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path


def save_json(data, filepath):
    """
    Save data to JSON file.
    
    Args:
        data: Data to save (dict or list)
        filepath: Path to save file
    """
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Saved: {filepath}")


def generate_diagnosis(risk_profiles):
    """
    Generate diagnosis data based on risk profiles.
    
    Maps highest-risk component to diagnosis with RUL, urgency,
    required parts, estimated cost, and service time.
    
    Args:
        risk_profiles: List of vehicle risk profiles
        
    Returns:
        list: Diagnosis records
    """
    diagnosis_mapping = {
        'battery_risk': {
            'diagnosis': 'Battery degradation',
            'parts': ['Battery replacement', 'Terminal cleaning'],
            'cost_range': (5000, 15000),
            'service_hours': 2
        },
        'engine_risk': {
            'diagnosis': 'Engine overheating risk',
            'parts': ['Coolant replacement', 'Thermostat', 'Radiator check'],
            'cost_range': (3000, 20000),
            'service_hours': 3
        },
        'brake_risk': {
            'diagnosis': 'Brake pad wear',
            'parts': ['Brake pads', 'Brake fluid', 'Rotor inspection'],
            'cost_range': (2000, 8000),
            'service_hours': 2
        },
        'tyre_risk': {
            'diagnosis': 'Tyre wear',
            'parts': ['Tyre replacement', 'Wheel alignment'],
            'cost_range': (4000, 12000),
            'service_hours': 1
        }
    }
    
    diagnosis_data = []
    
    for profile in risk_profiles:
        vehicle_id = profile['vehicle_id']
        risks = profile['risk_profile']
        severity = profile['severity']
        
        # Find highest risk component
        component_risks = {
            k: v for k, v in risks.items() 
            if k != 'overall_risk'
        }
        highest_component = max(component_risks, key=component_risks.get)
        highest_risk = component_risks[highest_component]
        
        # Get diagnosis template
        diag_template = diagnosis_mapping.get(highest_component, diagnosis_mapping['battery_risk'])
        
        # Compute RUL (Remaining Useful Life) in days
        # Higher risk = lower RUL
        if severity == "Critical":
            rul_days = random.randint(1, 7)
            urgency = "IMMEDIATE"
        elif severity == "Moderate":
            rul_days = random.randint(7, 30)
            urgency = "SOON"
        else:
            rul_days = random.randint(30, 90)
            urgency = "ROUTINE"
        
        # Cost and time estimation
        cost_min, cost_max = diag_template['cost_range']
        estimated_cost = random.randint(cost_min, cost_max)
        service_time = diag_template['service_hours']
        
        diagnosis_data.append({
            'vehicle_id': vehicle_id,
            'diagnosis': diag_template['diagnosis'],
            'severity': severity,
            'rul_days': rul_days,
            'urgency': urgency,
            'required_parts': diag_template['parts'],
            'estimated_cost': estimated_cost,
            'service_time_hours': service_time,
            'risk_score': round(highest_risk, 3),
            'primary_issue': highest_component.replace('_risk', ''),
            'generated_at': datetime.now().isoformat()
        })
    
    return diagnosis_data


def generate_forecasting(df, risk_profiles):
    """
    Generate 7-day and 30-day service load forecasts.
    
    Args:
        df: Telematics DataFrame
        risk_profiles: List of vehicle risk profiles
        
    Returns:
        dict: Forecasting data with predictions
    """
    # Count moderate and critical vehicles
    moderate_count = sum(1 for p in risk_profiles if p['severity'] == 'Moderate')
    critical_count = sum(1 for p in risk_profiles if p['severity'] == 'Critical')
    
    # Generate 7-day forecast
    forecast_7d = []
    for i in range(7):
        date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
        base_load = random.randint(4, 12)
        
        # Add additional load based on risk
        additional_load = (moderate_count * 0.3) + (critical_count * 0.5)
        predicted_load = int(base_load + additional_load)
        
        forecast_7d.append({
            'date': date,
            'predicted_load': predicted_load,
            'base_load': base_load,
            'risk_based_addition': int(additional_load)
        })
    
    # Generate 30-day forecast
    forecast_30d = []
    for i in range(30):
        date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
        base_load = random.randint(4, 12)
        
        # Add trend and seasonality
        trend = i * 0.1  # Slight upward trend
        seasonal = 2 * np.sin(2 * np.pi * i / 7)  # Weekly pattern
        
        additional_load = (moderate_count * 0.3) + (critical_count * 0.5)
        predicted_load = int(base_load + additional_load + trend + seasonal)
        
        forecast_30d.append({
            'date': date,
            'predicted_load': max(0, predicted_load)
        })
    
    return {
        'forecast_7_days': forecast_7d,
        'forecast_30_days': forecast_30d,
        'total_vehicles': len(risk_profiles),
        'critical_vehicles': critical_count,
        'moderate_vehicles': moderate_count,
        'generated_at': datetime.now().isoformat()
    }


def generate_map_scores(risk_profiles):
    """
    Generate MAP (Maintenance Action Priority) scores.
    
    Computes priority score from highest risk, fleet bonus, and customer tier.
    
    Args:
        risk_profiles: List of vehicle risk profiles
        
    Returns:
        list: MAP scoring data
    """
    customer_tiers = ['GOLD', 'SILVER', 'BRONZE', 'REGULAR']
    fleet_types = ['FLEET', 'INDIVIDUAL']
    
    map_data = []
    
    for profile in risk_profiles:
        vehicle_id = profile['vehicle_id']
        overall_risk = profile['risk_profile']['overall_risk']
        severity = profile['severity']
        
        # Base priority from risk (0-100 scale)
        base_priority = overall_risk * 100
        
        # Fleet bonus (+10 if fleet vehicle)
        is_fleet = random.choice([True, False])
        fleet_bonus = 10 if is_fleet else 0
        
        # Customer tier bonus
        customer_tier = random.choice(customer_tiers)
        tier_bonus = {
            'GOLD': 15,
            'SILVER': 10,
            'BRONZE': 5,
            'REGULAR': 0
        }[customer_tier]
        
        # Total priority score
        priority_score = base_priority + fleet_bonus + tier_bonus
        
        # Categorize
        if priority_score > 80:
            category = "URGENT"
        elif priority_score > 50:
            category = "HIGH"
        else:
            category = "NORMAL"
        
        map_data.append({
            'vehicle_id': vehicle_id,
            'priority_score': round(priority_score, 2),
            'category': category,
            'severity': severity,
            'base_risk_score': round(base_priority, 2),
            'fleet_bonus': fleet_bonus,
            'customer_tier': customer_tier,
            'tier_bonus': tier_bonus,
            'is_fleet': is_fleet,
            'generated_at': datetime.now().isoformat()
        })
    
    # Sort by priority score (highest first)
    map_data.sort(key=lambda x: x['priority_score'], reverse=True)
    
    return map_data


def generate_scheduling(map_scores):
    """
    Generate scheduling data with service slots.
    
    Creates 10 dummy slots per service center and assigns
    highest-priority vehicles to earliest slots.
    
    Args:
        map_scores: MAP scoring data
        
    Returns:
        dict: Scheduling data
    """
    service_centers = ['Center_North', 'Center_South', 'Center_East', 'Center_West']
    
    # Generate available slots
    slots = []
    slot_id = 1
    for center in service_centers:
        for day_offset in range(3):  # Next 3 days
            date = (datetime.now() + timedelta(days=day_offset)).strftime('%Y-%m-%d')
            for hour in [9, 11, 14, 16]:  # 4 slots per day
                slots.append({
                    'slot_id': f'SLOT_{slot_id:03d}',
                    'center': center,
                    'date': date,
                    'time': f'{hour}:00',
                    'available': True,
                    'assigned_vehicle': None
                })
                slot_id += 1
    
    # Assign highest-priority vehicles to earliest available slots
    assignments = []
    slot_index = 0
    
    for map_entry in map_scores:
        if map_entry['category'] in ['URGENT', 'HIGH'] and slot_index < len(slots):
            slot = slots[slot_index]
            slot['available'] = False
            slot['assigned_vehicle'] = map_entry['vehicle_id']
            
            assignments.append({
                'vehicle_id': map_entry['vehicle_id'],
                'slot_id': slot['slot_id'],
                'center': slot['center'],
                'date': slot['date'],
                'time': slot['time'],
                'priority': map_entry['category'],
                'confirmed': True
            })
            
            slot_index += 1
    
    return {
        'slots': slots,
        'assignments': assignments,
        'total_slots': len(slots),
        'booked_slots': len(assignments),
        'available_slots': len(slots) - len(assignments),
        'generated_at': datetime.now().isoformat()
    }


def generate_engagement_logs(risk_profiles, diagnosis):
    """
    Generate customer engagement conversation logs.
    
    Args:
        risk_profiles: List of vehicle risk profiles
        diagnosis: Diagnosis data
        
    Returns:
        list: Engagement conversation logs
    """
    templates = {
        'Critical': [
            {
                'agent': "Your {issue} health is critical. Immediate service recommended.",
                'user': "Is it safe to continue riding?",
                'agent_reply': "We recommend immediate inspection. Continuing may cause further damage."
            },
            {
                'agent': "We detected critical {issue} issues. RUL: {rul} days.",
                'user': "How much will it cost?",
                'agent_reply': "Estimated cost: ₹{cost}. We can schedule service today."
            }
        ],
        'Moderate': [
            {
                'agent': "Your {issue} needs attention soon. Service recommended within {rul} days.",
                'user': "Can I schedule for next week?",
                'agent_reply': "Yes, we have slots available. Shall I book one for you?"
            },
            {
                'agent': "Moderate {issue} wear detected. Estimated repair: ₹{cost}.",
                'user': "What parts need replacement?",
                'agent_reply': "Required: {parts}. Service time: {time} hours."
            }
        ],
        'Routine': [
            {
                'agent': "Your vehicle health looks good! Routine checkup recommended.",
                'user': "When should I come in?",
                'agent_reply': "Next routine service due in {rul} days. Want to pre-book?"
            }
        ]
    }
    
    logs = []
    
    for diag in diagnosis[:5]:  # Generate for top 5 vehicles
        vehicle_id = diag['vehicle_id']
        severity = diag['severity']
        
        template = random.choice(templates.get(severity, templates['Routine']))
        
        conversation = {
            'vehicle_id': vehicle_id,
            'timestamp': datetime.now().isoformat(),
            'severity': severity,
            'messages': [
                {
                    'role': 'agent',
                    'message': template['agent'].format(
                        issue=diag['primary_issue'],
                        rul=diag['rul_days'],
                        cost=diag['estimated_cost'],
                        parts=', '.join(diag['required_parts'][:2]),
                        time=diag['service_time_hours']
                    ),
                    'timestamp': datetime.now().isoformat()
                },
                {
                    'role': 'user',
                    'message': template['user'],
                    'timestamp': (datetime.now() + timedelta(seconds=30)).isoformat()
                },
                {
                    'role': 'agent',
                    'message': template['agent_reply'].format(
                        issue=diag['primary_issue'],
                        rul=diag['rul_days'],
                        cost=diag['estimated_cost'],
                        parts=', '.join(diag['required_parts'][:2]),
                        time=diag['service_time_hours']
                    ),
                    'timestamp': (datetime.now() + timedelta(seconds=45)).isoformat()
                }
            ]
        }
        
        logs.append(conversation)
    
    return logs


def generate_manufacturing_dummy(risk_profiles):
    """
    Generate manufacturing RCA/CAPA example data.
    
    Args:
        risk_profiles: List of vehicle risk profiles
        
    Returns:
        dict: Manufacturing quality data
    """
    return {
        'rca_example': {
            'incident_id': 'RCA_2024_001',
            'issue': 'Battery voltage drop in V01-V05 batch',
            'root_cause': 'Supplier quality issue - Terminal corrosion in batch QX2024',
            'affected_vehicles': ['V01', 'V02', 'V03'],
            'analysis': 'Chemical analysis reveals improper coating on battery terminals leading to accelerated corrosion',
            'evidence': [
                'Lab test results showing coating thickness 20% below spec',
                'Supplier audit findings',
                'Field failure correlation'
            ]
        },
        'capa_example': {
            'action_id': 'CAPA_2024_001',
            'corrective_action': 'Replace all affected batteries from batch QX2024',
            'preventive_action': 'Enhanced incoming quality inspection for battery terminals',
            'responsible': 'Quality Team',
            'deadline': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'status': 'IN_PROGRESS',
            'verification': 'Inspect next 100 batteries for coating thickness'
        },
        'quality_metrics': {
            'defect_rate': 0.023,
            'batch_rejection': 2,
            'supplier_score': 87.5,
            'trend': 'improving'
        },
        'generated_at': datetime.now().isoformat()
    }


def generate_ueba_dummy():
    """
    Generate UEBA (User and Entity Behavior Analytics) logs.
    
    Returns:
        dict: UEBA access control logs
    """
    allowed_actions = [
        {
            'agent': 'CustomerAgent',
            'action': 'READ',
            'resource': 'dialogue_history',
            'status': 'ALLOWED',
            'reason': 'Agent has read permission for customer dialogue'
        },
        {
            'agent': 'DiagnosisAgent',
            'action': 'READ',
            'resource': 'telematics_data',
            'status': 'ALLOWED',
            'reason': 'Required for diagnosis generation'
        },
        {
            'agent': 'SchedulingAgent',
            'action': 'WRITE',
            'resource': 'booking_slots',
            'status': 'ALLOWED',
            'reason': 'Agent manages scheduling'
        }
    ]
    
    blocked_actions = [
        {
            'agent': 'DiagnosisAgent',
            'action': 'READ',
            'resource': 'booking_slots',
            'status': 'BLOCKED',
            'reason': 'Diagnosis agent should not access booking data',
            'severity': 'MEDIUM'
        },
        {
            'agent': 'SchedulingAgent',
            'action': 'MODIFY',
            'resource': 'telematics_data',
            'status': 'BLOCKED',
            'reason': 'Scheduling agent cannot modify sensor data',
            'severity': 'HIGH'
        },
        {
            'agent': 'CustomerAgent',
            'action': 'DELETE',
            'resource': 'maintenance_records',
            'status': 'BLOCKED',
            'reason': 'Customer agent lacks delete permissions',
            'severity': 'CRITICAL'
        }
    ]
    
    return {
        'allowed_actions': allowed_actions,
        'blocked_actions': blocked_actions,
        'total_events': len(allowed_actions) + len(blocked_actions),
        'blocked_count': len(blocked_actions),
        'generated_at': datetime.now().isoformat()
    }


def generate_all_from_telematics(telematics_path="data/telematics_sample_1000.csv"):
    """
    Master function: Generate all synthetic data and save to JSON files.
    
    Args:
        telematics_path: Path to telematics CSV file
    """
    print("=" * 80)
    print("GENERATING ALL SYNTHETIC DATA")
    print("=" * 80)
    
    # Import here to avoid circular dependency
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from utils.data_pipeline import load_telematics, compute_risk_profiles
    
    # Step 1: Load telematics and compute risk profiles
    print("\n1. Computing risk profiles...")
    risk_profiles = compute_risk_profiles(telematics_path)
    save_json(risk_profiles, 'data/risk_profiles.json')
    
    # Step 2: Generate diagnosis
    print("\n2. Generating diagnosis...")
    diagnosis = generate_diagnosis(risk_profiles)
    save_json(diagnosis, 'data/diagnosis.json')
    
    # Step 3: Generate forecasting
    print("\n3. Generating forecasting...")
    df = load_telematics(telematics_path)
    forecasting = generate_forecasting(df, risk_profiles)
    save_json(forecasting, 'data/forecasting.json')
    
    # Step 4: Generate MAP scores
    print("\n4. Generating MAP scores...")
    map_scores = generate_map_scores(risk_profiles)
    save_json(map_scores, 'data/map_scores.json')
    
    # Step 5: Generate scheduling
    print("\n5. Generating scheduling...")
    scheduling = generate_scheduling(map_scores)
    save_json(scheduling, 'data/scheduling.json')
    
    # Step 6: Generate engagement logs
    print("\n6. Generating engagement logs...")
    engagement = generate_engagement_logs(risk_profiles, diagnosis)
    save_json(engagement, 'data/engagement_logs.json')
    
    # Step 7: Generate manufacturing data
    print("\n7. Generating manufacturing data...")
    manufacturing = generate_manufacturing_dummy(risk_profiles)
    save_json(manufacturing, 'data/manufacturing.json')
    
    # Step 8: Generate UEBA logs
    print("\n8. Generating UEBA logs...")
    ueba = generate_ueba_dummy()
    save_json(ueba, 'data/ueba_logs.json')
    
    print("\n" + "=" * 80)
    print("ALL DATA GENERATED SUCCESSFULLY!")
    print("=" * 80)
    print(f"\nGenerated files in data/ directory:")
    print("  - risk_profiles.json")
    print("  - diagnosis.json")
    print("  - forecasting.json")
    print("  - map_scores.json")
    print("  - scheduling.json")
    print("  - engagement_logs.json")
    print("  - manufacturing.json")
    print("  - ueba_logs.json")


if __name__ == "__main__":
    generate_all_from_telematics()
