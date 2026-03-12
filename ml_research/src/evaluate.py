"""
Model Evaluation Module
======================
Calculates comprehensive evaluation metrics for fatigue detection model.

Author: ML Research Team
"""

import pandas as pd
import numpy as np
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_curve,
    auc,
    label_binarize
)
from sklearn.preprocessing import label_binarize as sk_label_binarize
from typing import Dict, Any, Tuple
import json


class ModelEvaluator:
    """Evaluate model performance with comprehensive metrics."""
    
    def __init__(self, model, label_encoder, verbose: bool = True):
        """
        Initialize evaluator.
        
        Args:
            model: Trained model
            label_encoder: Label encoder used during preprocessing
            verbose: Print evaluation information
        """
        self.model = model
        self.label_encoder = label_encoder
        self.verbose = verbose
        
        self.metrics = {}
        self.classification_report_text = None
    
    def calculate_metrics(self, X_test: pd.DataFrame, y_test: np.ndarray) -> Dict[str, Any]:
        """
        Calculate all evaluation metrics.
        
        Args:
            X_test: Test features
            y_test: Test labels (encoded)
            
        Returns:
            dict: All metrics
        """
        # Get predictions
        y_pred = self.model.get_model().predict(X_test)
        
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"MODEL EVALUATION")
            print(f"{'='*60}")
        
        # Overall accuracy
        accuracy = accuracy_score(y_test, y_pred)
        
        # Per-class metrics
        precision = precision_score(y_test, y_pred, average=None, zero_division=0)
        recall = recall_score(y_test, y_pred, average=None, zero_division=0)
        f1 = f1_score(y_test, y_pred, average=None, zero_division=0)
        
        # Macro averages
        macro_precision = precision_score(y_test, y_pred, average='macro', zero_division=0)
        macro_recall = recall_score(y_test, y_pred, average='macro', zero_division=0)
        macro_f1 = f1_score(y_test, y_pred, average='macro', zero_division=0)
        
        # Weighted averages
        weighted_precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        weighted_recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        weighted_f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        
        # Classification report
        report = classification_report(
            y_test, y_pred,
            target_names=self.label_encoder.classes_,
            output_dict=False
        )
        self.classification_report_text = report
        
        if self.verbose:
            print(f"\nOverall Metrics:")
            print(f"  • Accuracy: {accuracy:.4f}")
            print(f"\nMacro-Averaged Metrics:")
            print(f"  • Precision: {macro_precision:.4f}")
            print(f"  • Recall: {macro_recall:.4f}")
            print(f"  • F1-Score: {macro_f1:.4f}")
            print(f"\nWeighted-Averaged Metrics:")
            print(f"  • Precision: {weighted_precision:.4f}")
            print(f"  • Recall: {weighted_recall:.4f}")
            print(f"  • F1-Score: {weighted_f1:.4f}")
            print(f"\nConfusion Matrix Shape: {cm.shape}")
        
        # Store metrics
        self.metrics = {
            'accuracy': float(accuracy),
            'precision_per_class': precision.tolist(),
            'recall_per_class': recall.tolist(),
            'f1_per_class': f1.tolist(),
            'macro_precision': float(macro_precision),
            'macro_recall': float(macro_recall),
            'macro_f1': float(macro_f1),
            'weighted_precision': float(weighted_precision),
            'weighted_recall': float(weighted_recall),
            'weighted_f1': float(weighted_f1),
            'confusion_matrix': cm.tolist(),
            'classes': self.label_encoder.classes_.tolist(),
            'num_samples': len(X_test)
        }
        
        if self.verbose:
            print(f"\nClassification Report:")
            print(report)
            print(f"{'='*60}\n")
        
        return self.metrics
    
    def get_roc_data(self, X_test: pd.DataFrame, y_test: np.ndarray) -> Dict[str, Any]:
        """
        Calculate ROC curve data for multi-class classification.
        
        Args:
            X_test: Test features
            y_test: Test labels (encoded)
            
        Returns:
            dict: ROC curve data
        """
        # Get prediction probabilities
        y_proba = self.model.get_model().predict_proba(X_test)
        
        n_classes = len(self.label_encoder.classes_)
        
        # Binarize labels for multi-class ROC
        y_test_bin = sk_label_binarize(y_test, classes=np.arange(n_classes))
        
        roc_data = {
            'classes': self.label_encoder.classes_.tolist(),
            'fpr': {},
            'tpr': {},
            'auc': {}
        }
        
        # Calculate ROC for each class
        for i in range(n_classes):
            fpr, tpr, _ = roc_curve(y_test_bin[:, i], y_proba[:, i])
            roc_auc = auc(fpr, tpr)
            
            roc_data['fpr'][str(i)] = fpr.tolist()
            roc_data['tpr'][str(i)] = tpr.tolist()
            roc_data['auc'][str(i)] = float(roc_auc)
        
        if self.verbose:
            print(f"\nROC-AUC Scores:")
            for i, class_name in enumerate(self.label_encoder.classes_):
                print(f"  • {class_name}: {roc_data['auc'][str(i)]:.4f}")
        
        return roc_data
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get metrics dictionary for JSON export.
        
        Returns:
            dict: All metrics formatted for export
        """
        if not self.metrics:
            raise ValueError("No metrics calculated. Call calculate_metrics() first.")
        
        return {
            'overall_metrics': {
                'accuracy': self.metrics['accuracy'],
                'macro_precision': self.metrics['macro_precision'],
                'macro_recall': self.metrics['macro_recall'],
                'macro_f1': self.metrics['macro_f1'],
                'weighted_precision': self.metrics['weighted_precision'],
                'weighted_recall': self.metrics['weighted_recall'],
                'weighted_f1': self.metrics['weighted_f1']
            },
            'per_class_metrics': {
                'classes': self.metrics['classes'],
                'precision': self.metrics['precision_per_class'],
                'recall': self.metrics['recall_per_class'],
                'f1_score': self.metrics['f1_per_class']
            },
            'confusion_matrix': {
                'matrix': self.metrics['confusion_matrix'],
                'classes': self.metrics['classes']
            },
            'test_samples': self.metrics['num_samples']
        }
    
    def save_metrics(self, filepath: str):
        """
        Save metrics to JSON file.
        
        Args:
            filepath: Path to save metrics
        """
        if not self.metrics:
            raise ValueError("No metrics calculated. Call calculate_metrics() first.")
        
        metrics_dict = self.get_metrics_summary()
        
        with open(filepath, 'w') as f:
            json.dump(metrics_dict, f, indent=4)
        
        if self.verbose:
            print(f"✓ Metrics saved to: {filepath}")
    
    def save_classification_report(self, filepath: str):
        """
        Save classification report to text file.
        
        Args:
            filepath: Path to save report
        """
        if not self.classification_report_text:
            raise ValueError("No classification report generated. Call calculate_metrics() first.")
        
        with open(filepath, 'w') as f:
            f.write("CLASSIFICATION REPORT\n")
            f.write("="*60 + "\n\n")
            f.write(self.classification_report_text)
        
        if self.verbose:
            print(f"✓ Classification report saved to: {filepath}")
