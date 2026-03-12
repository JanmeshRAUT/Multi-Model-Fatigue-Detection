"""
Data Loading Module
====================
Handles loading and validation of fatigue detection datasets.
Supports multiple dataset formats and sources.

Author: ML Research Team
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path
from typing import Tuple, Optional


class DataLoader:
    """Load and validate fatigue detection datasets."""
    
    # Expected feature columns
    EXPECTED_FEATURES = [
        'PERCLOS', 'Blink_Rate', 'EAR', 
        'Head_Yaw', 'Head_Pitch', 'Head_Roll',
        'Heart_Rate', 'Temperature', 'SpO2'
    ]
    
    # Target column name
    TARGET_COLUMN = 'Fatigue_State'
    
    def __init__(self, dataset_path: str, verbose: bool = True):
        """
        Initialize data loader.
        
        Args:
            dataset_path: Path to CSV dataset
            verbose: Print loading information
        """
        self.dataset_path = dataset_path
        self.verbose = verbose
        self.data = None
        self.feature_names = None
        self.target_name = None
        
    def load(self) -> pd.DataFrame:
        """
        Load dataset from CSV.
        
        Returns:
            DataFrame: Loaded dataset
            
        Raises:
            FileNotFoundError: If dataset file doesn't exist
            ValueError: If dataset structure is invalid
        """
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"Dataset not found: {self.dataset_path}")
        
        if self.verbose:
            print(f"📂 Loading dataset from: {self.dataset_path}")
        
        self.data = pd.read_csv(self.dataset_path)
        
        if self.verbose:
            print(f"✓ Dataset loaded: {self.data.shape[0]} samples, {self.data.shape[1]} columns")
        
        return self.data
    
    def validate(self) -> bool:
        """
        Validate dataset structure and contents.
        
        Returns:
            bool: True if valid, raises exception otherwise
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load() first.")
        
        # Check for target column (flexible naming)
        if self.TARGET_COLUMN not in self.data.columns and 'Label' not in self.data.columns:
            if 'Fatigue' not in self.data.columns and 'Class' not in self.data.columns:
                raise ValueError(f"Target column not found. Expected one of: {self.TARGET_COLUMN}, Label, Fatigue, Class")
        
        # Auto-detect target column
        if self.TARGET_COLUMN in self.data.columns:
            self.target_name = self.TARGET_COLUMN
        elif 'Label' in self.data.columns:
            self.target_name = 'Label'
        elif 'Fatigue' in self.data.columns:
            self.target_name = 'Fatigue'
        elif 'Class' in self.data.columns:
            self.target_name = 'Class'
        
        # Identify feature columns (all except target)
        self.feature_names = [col for col in self.data.columns if col != self.target_name]
        
        if self.verbose:
            print(f"✓ Target column detected: '{self.target_name}'")
            print(f"✓ Number of features: {len(self.feature_names)}")
            print(f"✓ Feature columns: {self.feature_names}")
        
        return True
    
    def get_features_and_target(self) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Extract features and target from loaded data.
        
        Returns:
            Tuple[DataFrame, Series]: Features and target
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load() first.")
        
        if self.target_name is None:
            self.validate()
        
        X = self.data[self.feature_names].copy()
        y = self.data[self.target_name].copy()
        
        return X, y
    
    def get_data_info(self) -> dict:
        """
        Get comprehensive dataset information.
        
        Returns:
            dict: Dataset statistics and metadata
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load() first.")
        
        X, y = self.get_features_and_target()
        
        return {
            'total_samples': len(self.data),
            'num_features': len(self.feature_names),
            'num_targets': len(np.unique(y)),
            'feature_names': self.feature_names,
            'missing_values': self.data.isnull().sum().to_dict(),
            'target_distribution': y.value_counts().to_dict(),
            'feature_dtypes': self.data[self.feature_names].dtypes.to_dict(),
            'data_shape': self.data.shape
        }
    
    def print_summary(self):
        """Print dataset summary to console."""
        if self.data is None:
            raise ValueError("No data loaded. Call load() first.")
        
        info = self.get_data_info()
        
        print("\n" + "="*60)
        print("DATASET SUMMARY")
        print("="*60)
        print(f"Total Samples: {info['total_samples']}")
        print(f"Number of Features: {info['num_features']}")
        print(f"Number of Target Classes: {info['num_targets']}")
        
        print(f"\nFeatures: {', '.join(info['feature_names'])}")
        
        print(f"\nTarget Distribution:")
        for class_label, count in sorted(info['target_distribution'].items()):
            percentage = (count / info['total_samples']) * 100
            print(f"  Class {class_label}: {count} samples ({percentage:.2f}%)")
        
        print(f"\nMissing Values:")
        missing_dict = info['missing_values']
        if any(missing_dict.values()):
            for col, count in missing_dict.items():
                if count > 0:
                    print(f"  {col}: {count} ({(count/info['total_samples'])*100:.2f}%)")
        else:
            print("  None")
        
        print("="*60 + "\n")
