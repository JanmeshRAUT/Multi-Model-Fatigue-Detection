"""
Configuration File
==================
Central place to manage all hyperparameters and settings.

Usage:
    from config import Config
    config = Config()
    print(config.model_params)
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class DataConfig:
    """Data loading and preprocessing configuration."""
    
    # Dataset
    dataset_path: str = 'data/fatigue_dataset.csv'
    
    # Preprocessing
    test_size: float = 0.30
    random_state: int = 42
    missing_value_strategy: str = 'mean'  # 'mean', 'median', 'drop'
    normalize_features: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'dataset_path': self.dataset_path,
            'test_size': self.test_size,
            'random_state': self.random_state,
            'missing_value_strategy': self.missing_value_strategy,
            'normalize_features': self.normalize_features
        }


@dataclass
class ModelConfig:
    """Random Forest model hyperparameters."""
    
    # Tree settings
    n_estimators: int = 200
    max_depth: int = None  # None for unlimited
    min_samples_split: int = 2
    min_samples_leaf: int = 1
    
    # Fit settings
    random_state: int = 42
    n_jobs: int = -1  # Use all cores
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'n_estimators': self.n_estimators,
            'max_depth': self.max_depth,
            'min_samples_split': self.min_samples_split,
            'min_samples_leaf': self.min_samples_leaf,
            'random_state': self.random_state,
            'n_jobs': self.n_jobs
        }


@dataclass
class EvaluationConfig:
    """Model evaluation settings."""
    
    # Cross-validation
    cv_folds: int = 5
    
    # Reporting
    save_metrics_json: bool = True
    save_classification_report: bool = True
    save_feature_importance: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'cv_folds': self.cv_folds,
            'save_metrics_json': self.save_metrics_json,
            'save_classification_report': self.save_classification_report,
            'save_feature_importance': self.save_feature_importance
        }


@dataclass
class VisualizationConfig:
    """Visualization settings."""
    
    # Output
    output_dir: str = 'results/figures'
    dpi: int = 300  # Resolution
    save_format: str = 'png'
    
    # Style
    style: str = 'seaborn-v0_8-darkgrid'
    figsize_large: tuple = (14, 8)
    figsize_medium: tuple = (12, 7)
    figsize_small: tuple = (10, 6)
    
    # Content
    show_titles: bool = True
    show_labels: bool = True
    show_values: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'output_dir': self.output_dir,
            'dpi': self.dpi,
            'save_format': self.save_format,
            'style': self.style,
            'figsize_large': self.figsize_large,
            'figsize_medium': self.figsize_medium,
            'figsize_small': self.figsize_small,
            'show_titles': self.show_titles,
            'show_labels': self.show_labels,
            'show_values': self.show_values
        }


class Config:
    """Master configuration class."""
    
    def __init__(self):
        """Initialize all configurations."""
        self.data = DataConfig()
        self.model = ModelConfig()
        self.evaluation = EvaluationConfig()
        self.visualization = VisualizationConfig()
    
    @property
    def data_params(self) -> Dict[str, Any]:
        """Get data parameters."""
        return self.data.to_dict()
    
    @property
    def model_params(self) -> Dict[str, Any]:
        """Get model parameters."""
        return self.model.to_dict()
    
    @property
    def evaluation_params(self) -> Dict[str, Any]:
        """Get evaluation parameters."""
        return self.evaluation.to_dict()
    
    @property
    def visualization_params(self) -> Dict[str, Any]:
        """Get visualization parameters."""
        return self.visualization.to_dict()
    
    def print_all(self):
        """Print all configurations."""
        print("\n" + "="*60)
        print("CONFIGURATION SUMMARY")
        print("="*60)
        
        print("\n📊 Data Configuration:")
        for key, value in self.data_params.items():
            print(f"  • {key}: {value}")
        
        print("\n🤖 Model Configuration:")
        for key, value in self.model_params.items():
            print(f"  • {key}: {value}")
        
        print("\n📈 Evaluation Configuration:")
        for key, value in self.evaluation_params.items():
            print(f"  • {key}: {value}")
        
        print("\n🎨 Visualization Configuration:")
        for key, value in self.visualization_params.items():
            print(f"  • {key}: {value}")
        
        print("="*60 + "\n")


# Preset configurations for different use cases
class Presets:
    """Pre-defined configuration presets."""
    
    @staticmethod
    def fast_training() -> Config:
        """Fast training with fewer trees."""
        config = Config()
        config.model.n_estimators = 50
        config.model.max_depth = 10
        config.data.test_size = 0.20
        return config
    
    @staticmethod
    def balanced() -> Config:
        """Balanced configuration (default)."""
        return Config()
    
    @staticmethod
    def high_accuracy() -> Config:
        """High accuracy with more trees and depth."""
        config = Config()
        config.model.n_estimators = 500
        config.model.max_depth = None
        config.model.min_samples_leaf = 2
        config.data.test_size = 0.30
        return config
    
    @staticmethod
    def overfit_check() -> Config:
        """Configuration to detect overfitting."""
        config = Config()
        config.model.n_estimators = 200
        config.model.max_depth = 50
        config.data.test_size = 0.30
        return config


if __name__ == '__main__':
    # Example usage
    print("Default Configuration:")
    config = Config()
    config.print_all()
    
    print("\n\nFast Training Preset:")
    fast_config = Presets.fast_training()
    fast_config.print_all()
    
    print("\n\nHigh Accuracy Preset:")
    acc_config = Presets.high_accuracy()
    acc_config.print_all()
