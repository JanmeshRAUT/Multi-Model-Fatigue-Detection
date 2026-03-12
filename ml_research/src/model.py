"""
Model Definition Module
=======================
Defines and initializes the Random Forest classifier.

Author: ML Research Team
"""

from sklearn.ensemble import RandomForestClassifier
from typing import Dict, Any


class FatigueDetectionModel:
    """Random Forest classifier for fatigue detection."""
    
    def __init__(self, 
                 n_estimators: int = 200,
                 max_depth: int = None,
                 min_samples_split: int = 2,
                 min_samples_leaf: int = 1,
                 random_state: int = 42,
                 n_jobs: int = -1,
                 verbose: bool = True):
        """
        Initialize Random Forest model.
        
        Args:
            n_estimators: Number of trees in forest
            max_depth: Maximum depth of trees (None for unlimited)
            min_samples_split: Minimum samples required to split
            min_samples_leaf: Minimum samples required at leaf
            random_state: Random seed for reproducibility
            n_jobs: Number of parallel jobs (-1 for all cores)
            verbose: Print initialization info
        """
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.random_state = random_state
        self.n_jobs = n_jobs
        self.verbose = verbose
        
        # Initialize the model
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            random_state=random_state,
            n_jobs=n_jobs,
            verbose=0
        )
        
        self.is_trained = False
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"MODEL INITIALIZATION")
            print(f"{'='*60}")
            print(f"Model Type: Random Forest Classifier")
            print(f"Configuration:")
            print(f"  • n_estimators: {n_estimators}")
            print(f"  • max_depth: {max_depth if max_depth else 'Unlimited'}")
            print(f"  • min_samples_split: {min_samples_split}")
            print(f"  • min_samples_leaf: {min_samples_leaf}")
            print(f"  • random_state: {random_state}")
            print(f"  • n_jobs: {n_jobs}")
            print(f"{'='*60}\n")
    
    def get_model(self) -> RandomForestClassifier:
        """
        Get the underlying scikit-learn model.
        
        Returns:
            RandomForestClassifier: The model
        """
        return self.model
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get model configuration.
        
        Returns:
            dict: Model hyperparameters
        """
        return {
            'model_type': 'RandomForestClassifier',
            'n_estimators': self.n_estimators,
            'max_depth': self.max_depth,
            'min_samples_split': self.min_samples_split,
            'min_samples_leaf': self.min_samples_leaf,
            'random_state': self.random_state,
            'n_jobs': self.n_jobs,
            'is_trained': self.is_trained
        }
    
    def set_trained(self, value: bool):
        """
        Set training status flag.
        
        Args:
            value: Training status
        """
        self.is_trained = value
