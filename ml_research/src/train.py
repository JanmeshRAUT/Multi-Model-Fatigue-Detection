"""
Model Training Module
=====================
Handles model training with logging and monitoring.

Author: ML Research Team
"""

import pandas as pd
import numpy as np
import time
from typing import Tuple, Dict, Any
from .model import FatigueDetectionModel


class ModelTrainer:
    """Train and manage fatigue detection model."""
    
    def __init__(self, model: FatigueDetectionModel, verbose: bool = True):
        """
        Initialize trainer.
        
        Args:
            model: FatigueDetectionModel instance
            verbose: Print training information
        """
        self.model = model
        self.verbose = verbose
        
        self.training_time = None
        self.training_history = {}
    
    def train(self, X_train: pd.DataFrame, y_train: np.ndarray) -> Dict[str, Any]:
        """
        Train the model.
        
        Args:
            X_train: Training features
            y_train: Training labels (encoded)
            
        Returns:
            dict: Training results and timing
        """
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"MODEL TRAINING")
            print(f"{'='*60}")
            print(f"Training samples: {len(X_train)}")
            print(f"Number of features: {X_train.shape[1]}")
            print(f"Unique classes: {len(np.unique(y_train))}")
        
        # Record start time
        start_time = time.time()
        
        if self.verbose:
            print(f"\nTraining in progress...")
        
        # Train the model
        self.model.get_model().fit(X_train, y_train)
        
        # Record end time
        end_time = time.time()
        self.training_time = end_time - start_time
        
        # Calculate training accuracy
        train_accuracy = self.model.get_model().score(X_train, y_train)
        
        if self.verbose:
            print(f"✓ Training complete!")
            print(f"  • Training time: {self.training_time:.2f} seconds")
            print(f"  • Training accuracy: {train_accuracy:.4f}")
        
        # Store training history
        self.training_history = {
            'training_time': self.training_time,
            'training_accuracy': train_accuracy,
            'num_samples': len(X_train),
            'num_features': X_train.shape[1],
            'num_classes': len(np.unique(y_train))
        }
        
        # Mark model as trained
        self.model.set_trained(True)
        
        if self.verbose:
            print(f"{'='*60}\n")
        
        return self.training_history
    
    def evaluate_on_train_test(self, 
                               X_train: pd.DataFrame, 
                               y_train: np.ndarray,
                               X_test: pd.DataFrame, 
                               y_test: np.ndarray) -> Dict[str, float]:
        """
        Evaluate model on both training and test sets.
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_test: Test features
            y_test: Test labels
            
        Returns:
            dict: Accuracy scores
        """
        if not self.model.is_trained:
            raise ValueError("Model not trained. Call train() first.")
        
        train_acc = self.model.get_model().score(X_train, y_train)
        test_acc = self.model.get_model().score(X_test, y_test)
        
        scores = {
            'train_accuracy': train_acc,
            'test_accuracy': test_acc,
            'accuracy_difference': abs(train_acc - test_acc)
        }
        
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"TRAINING VS TEST ACCURACY")
            print(f"{'='*60}")
            print(f"Training Accuracy: {train_acc:.4f}")
            print(f"Testing Accuracy: {test_acc:.4f}")
            print(f"Difference: {scores['accuracy_difference']:.4f}")
            
            # Check for overfitting
            if scores['accuracy_difference'] > 0.10:
                print(f"⚠️  Potential overfitting detected (>10% difference)")
            else:
                print(f"✓ Good generalization")
            
            print(f"{'='*60}\n")
        
        return scores
    
    def get_feature_importance(self, feature_names: list) -> pd.DataFrame:
        """
        Get feature importance from trained model.
        
        Args:
            feature_names: Names of features
            
        Returns:
            DataFrame: Features ranked by importance
        """
        if not self.model.is_trained:
            raise ValueError("Model not trained. Call train() first.")
        
        importances = self.model.get_model().feature_importances_
        
        # Create dataframe
        feature_importance_df = pd.DataFrame({
            'Feature': feature_names,
            'Importance': importances
        }).sort_values('Importance', ascending=False).reset_index(drop=True)
        
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"FEATURE IMPORTANCE")
            print(f"{'='*60}")
            for idx, row in feature_importance_df.iterrows():
                bar_length = int(row['Importance'] * 50)
                bar = '█' * bar_length
                print(f"{row['Feature']:20s} {bar} {row['Importance']:.4f}")
            print(f"{'='*60}\n")
        
        return feature_importance_df
    
    def get_training_info(self) -> Dict[str, Any]:
        """
        Get comprehensive training information.
        
        Returns:
            dict: Training details
        """
        return {
            'training_time': self.training_time,
            'is_trained': self.model.is_trained,
            'training_history': self.training_history
        }
