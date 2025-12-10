"""
Data Loaders

Utility functions for loading JSON and CSV files.
"""

import json
import pandas as pd


def load_json(path):
    """
    Load and parse JSON file.
    
    Args:
        path: Path to JSON file
        
    Returns:
        dict or list: Parsed JSON data
    """
    with open(path, 'r') as f:
        data = json.load(f)
    return data


def load_csv(path):
    """
    Load CSV file as pandas DataFrame.
    
    Args:
        path: Path to CSV file
        
    Returns:
        pd.DataFrame: Loaded data
    """
    df = pd.read_csv(path)
    return df
