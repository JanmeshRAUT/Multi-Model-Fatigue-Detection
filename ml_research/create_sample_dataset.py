"""
Sample Dataset Generator
========================
Creates a synthetic sample dataset for testing the pipeline.

Usage:
    python create_sample_dataset.py
"""

import pandas as pd
import numpy as np
import os


def create_sample_dataset(n_samples=500):
    """
    Create a synthetic fatigue detection dataset.
    
    Args:
        n_samples: Number of samples to generate
        
    Returns:
        DataFrame: Sample dataset
    """
    np.random.seed(42)
    
    # Define fatigue state distributions with different feature patterns
    data = []
    
    # Class 0: Alert - Normal feature values
    n_alert = int(n_samples * 0.4)
    for _ in range(n_alert):
        data.append({
            'PERCLOS': np.random.normal(0.15, 0.05),
            'Blink_Rate': np.random.normal(12, 2),
            'EAR': np.random.normal(0.45, 0.05),
            'Head_Yaw': np.random.normal(0, 5),
            'Head_Pitch': np.random.normal(0, 5),
            'Head_Roll': np.random.normal(0, 3),
            'Heart_Rate': np.random.normal(70, 8),
            'Temperature': np.random.normal(36.5, 0.5),
            'SpO2': np.random.normal(98, 1.5),
            'Fatigue_State': 0
        })
    
    # Class 1: Drowsy - Elevated PERCLOS, lower EAR
    n_drowsy = int(n_samples * 0.35)
    for _ in range(n_drowsy):
        data.append({
            'PERCLOS': np.random.normal(0.35, 0.08),
            'Blink_Rate': np.random.normal(8, 2),
            'EAR': np.random.normal(0.32, 0.06),
            'Head_Yaw': np.random.normal(5, 8),
            'Head_Pitch': np.random.normal(-5, 8),
            'Head_Roll': np.random.normal(3, 5),
            'Heart_Rate': np.random.normal(65, 10),
            'Temperature': np.random.normal(37.0, 0.6),
            'SpO2': np.random.normal(96, 2),
            'Fatigue_State': 1
        })
    
    # Class 2: Fatigued - High PERCLOS, very low EAR
    n_fatigued = int(n_samples * 0.25)
    for _ in range(n_fatigued):
        data.append({
            'PERCLOS': np.random.normal(0.60, 0.10),
            'Blink_Rate': np.random.normal(4, 2),
            'EAR': np.random.normal(0.20, 0.05),
            'Head_Yaw': np.random.normal(10, 10),
            'Head_Pitch': np.random.normal(-10, 10),
            'Head_Roll': np.random.normal(5, 7),
            'Heart_Rate': np.random.normal(55, 12),
            'Temperature': np.random.normal(37.5, 0.8),
            'SpO2': np.random.normal(94, 2.5),
            'Fatigue_State': 2
        })
    
    df = pd.DataFrame(data)
    
    # Clip unrealistic values
    df['PERCLOS'] = df['PERCLOS'].clip(0, 1)
    df['EAR'] = df['EAR'].clip(0, 1)
    df['Blink_Rate'] = df['Blink_Rate'].clip(1, 30)
    df['Heart_Rate'] = df['Heart_Rate'].clip(40, 150)
    df['Temperature'] = df['Temperature'].clip(35, 40)
    df['SpO2'] = df['SpO2'].clip(85, 100)
    df['Head_Yaw'] = df['Head_Yaw'].clip(-90, 90)
    df['Head_Pitch'] = df['Head_Pitch'].clip(-90, 90)
    df['Head_Roll'] = df['Head_Roll'].clip(-90, 90)
    
    return df


def main():
    """Create and save sample dataset."""
    
    print("Generating synthetic fatigue detection dataset...")
    df = create_sample_dataset(n_samples=500)
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Save to CSV
    output_path = 'data/fatigue_dataset.csv'
    df.to_csv(output_path, index=False)
    
    print(f"\n✓ Sample dataset created: {output_path}")
    print(f"  • Total samples: {len(df)}")
    print(f"  • Features: {len(df.columns) - 1}")
    print(f"  • Classes: {df['Fatigue_State'].nunique()}")
    print(f"\nClass distribution:")
    print(df['Fatigue_State'].value_counts().sort_index().to_string())
    print(f"\nFirst few rows:")
    print(df.head())


if __name__ == '__main__':
    main()
