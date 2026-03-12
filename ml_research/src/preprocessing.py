"""
Data Preprocessing Module
=========================
Handles data cleaning, normalization, and feature engineering.

Author: ML Research Team
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from typing import Tuple, Dict, Any


class DataPreprocessor:
    """Preprocess and prepare data for model training."""
    
    def __init__(self, random_state: int = 42, test_size: float = 0.30, verbose: bool = True):
        """
        Initialize preprocessor.
        
        Args:
            random_state: Random seed for reproducibility
            test_size: Fraction of data to use for testing
            verbose: Print processing information
        """
        self.random_state = random_state
        self.test_size = test_size
        self.verbose = verbose
        
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
        self.feature_names = None
        self.scaler_fitted = False
        self.encoder_fitted = False
    
    def handle_missing_values(self, X: pd.DataFrame, strategy: str = 'mean') -> pd.DataFrame:
        """
        Handle missing values in features.
        
        Args:
            X: Feature dataframe
            strategy: Strategy for imputation ('mean', 'median', 'drop')
            
        Returns:
            DataFrame: Data with missing values handled
        """
        if self.verbose:
            missing_count = X.isnull().sum().sum()
            print(f"🔧 Handling missing values (strategy: {strategy})")
            print(f"   Found {missing_count} missing values")
        
        X_clean = X.copy()
        
        if strategy == 'mean':
            X_clean = X_clean.fillna(X_clean.mean())
        elif strategy == 'median':
            X_clean = X_clean.fillna(X_clean.median())
        elif strategy == 'drop':
            X_clean = X_clean.dropna()
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        if self.verbose:
            remaining_missing = X_clean.isnull().sum().sum()
            print(f"✓ Remaining missing values: {remaining_missing}")
        
        return X_clean
    
    def normalize_features(self, X: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        """
        Normalize features using StandardScaler.
        
        Args:
            X: Feature dataframe
            fit: Whether to fit the scaler (True for training data)
            
        Returns:
            DataFrame: Normalized features
        """
        if self.verbose:
            print(f"🔧 Normalizing features using StandardScaler")
        
        if fit:
            X_normalized = pd.DataFrame(
                self.scaler.fit_transform(X),
                columns=X.columns,
                index=X.index
            )
            self.scaler_fitted = True
        else:
            if not self.scaler_fitted:
                raise ValueError("Scaler not fitted. Call with fit=True on training data first.")
            X_normalized = pd.DataFrame(
                self.scaler.transform(X),
                columns=X.columns,
                index=X.index
            )
        
        if self.verbose:
            print(f"✓ Features normalized (mean≈0, std≈1)")
        
        return X_normalized
    
    def encode_labels(self, y: pd.Series, fit: bool = True) -> np.ndarray:
        """
        Encode categorical labels to integers.
        
        Args:
            y: Target series
            fit: Whether to fit the encoder (True for training data)
            
        Returns:
            ndarray: Encoded labels
        """
        if self.verbose:
            print(f"🔧 Encoding categorical labels")
            print(f"   Unique classes: {sorted(y.unique())}")
        
        if fit:
            y_encoded = self.label_encoder.fit_transform(y)
            self.encoder_fitted = True
            if self.verbose:
                print(f"   Mapping: {dict(zip(self.label_encoder.classes_, self.label_encoder.transform(self.label_encoder.classes_)))}")
        else:
            if not self.encoder_fitted:
                raise ValueError("Encoder not fitted. Call with fit=True on training data first.")
            y_encoded = self.label_encoder.transform(y)
        
        if self.verbose:
            print(f"✓ Labels encoded")
        
        return y_encoded
    
    def preprocess(self, X: pd.DataFrame, y: pd.Series) -> Tuple[pd.DataFrame, np.ndarray]:
        """
        Complete preprocessing pipeline.
        
        Args:
            X: Features
            y: Target
            
        Returns:
            Tuple: Cleaned and normalized features, encoded target
        """
        if self.verbose:
            print("\n" + "="*60)
            print("DATA PREPROCESSING PIPELINE")
            print("="*60)
        
        # Store feature names
        self.feature_names = X.columns.tolist()
        
        # Handle missing values
        X_clean = self.handle_missing_values(X, strategy='mean')
        
        # Normalize features
        X_normalized = self.normalize_features(X_clean, fit=True)
        
        # Encode labels
        y_encoded = self.encode_labels(y, fit=True)
        
        if self.verbose:
            print("✓ Preprocessing complete\n")
        
        return X_normalized, y_encoded
    
    def split_data(self, X: pd.DataFrame, y: np.ndarray) -> Tuple[
        pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray
    ]:
        """
        Split data into training and testing sets.
        
        Args:
            X: Features (should be preprocessed)
            y: Target (should be encoded)
            
        Returns:
            Tuple: X_train, X_test, y_train, y_test
        """
        if self.verbose:
            print(f"🔧 Splitting data (train: {1-self.test_size:.0%}, test: {self.test_size:.0%})")
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=self.test_size,
            random_state=self.random_state,
            stratify=y  # Maintain class distribution
        )
        
        if self.verbose:
            print(f"✓ Training set: {len(X_train)} samples")
            print(f"✓ Testing set: {len(X_test)} samples")
        
        return X_train, X_test, y_train, y_test
    
    def get_preprocessing_info(self) -> Dict[str, Any]:
        """
        Get preprocessing configuration and state.
        
        Returns:
            dict: Preprocessing information
        """
        return {
            'random_state': self.random_state,
            'test_size': self.test_size,
            'scaler_fitted': self.scaler_fitted,
            'encoder_fitted': self.encoder_fitted,
            'feature_names': self.feature_names,
            'classes': self.label_encoder.classes_.tolist() if self.encoder_fitted else None
        }
