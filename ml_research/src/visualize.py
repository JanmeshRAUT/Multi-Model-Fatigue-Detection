"""
Visualization Module
====================
Generates research-quality graphs and figures for fatigue detection model.

Author: ML Research Team
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, roc_curve, auc
from scipy.stats import pearsonr
from typing import Dict, Any, List
import os


class ModelVisualizer:
    """Generate and save research-quality visualizations."""
    
    # Style configuration
    STYLE = 'seaborn-v0_8-darkgrid'
    FIGSIZE_LARGE = (14, 8)
    FIGSIZE_MEDIUM = (12, 7)
    FIGSIZE_SMALL = (10, 6)
    DPI = 300
    COLORS = ['#2ecc71', '#f39c12', '#e74c3c']  # Alert, Drowsy, Fatigued
    
    def __init__(self, output_dir: str = 'results/figures', verbose: bool = True):
        """
        Initialize visualizer.
        
        Args:
            output_dir: Directory to save figures
            verbose: Print saving information
        """
        self.output_dir = output_dir
        self.verbose = verbose
        
        # Create output directory if not exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Set style
        plt.style.use(self.STYLE)
        sns.set_palette("husl")
    
    def plot_accuracy_comparison(self, 
                                 train_acc: float, 
                                 test_acc: float,
                                 filename: str = 'accuracy_comparison.png'):
        """
        Plot training vs test accuracy.
        
        Args:
            train_acc: Training accuracy
            test_acc: Test accuracy
            filename: Output filename
        """
        fig, ax = plt.subplots(figsize=self.FIGSIZE_SMALL)
        
        accuracies = [train_acc, test_acc]
        labels = ['Training', 'Test']
        colors = ['#3498db', '#e74c3c']
        
        bars = ax.bar(labels, accuracies, color=colors, width=0.6, edgecolor='black', linewidth=1.5)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.4f}',
                   ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        ax.set_ylabel('Accuracy', fontsize=12, fontweight='bold')
        ax.set_title('Training vs Test Accuracy', fontsize=14, fontweight='bold', pad=20)
        ax.set_ylim([0, 1.0])
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=self.DPI, bbox_inches='tight')
        plt.close()
        
        if self.verbose:
            print(f"✓ Saved: {filename}")
    
    def plot_confusion_matrix(self, 
                              y_true: np.ndarray, 
                              y_pred: np.ndarray,
                              classes: List[str],
                              filename: str = 'confusion_matrix.png'):
        """
        Plot confusion matrix heatmap.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            classes: Class names
            filename: Output filename
        """
        cm = confusion_matrix(y_true, y_pred)
        
        fig, ax = plt.subplots(figsize=self.FIGSIZE_SMALL)
        
        # Normalize for percentages
        cm_percent = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        
        # Create heatmap
        sns.heatmap(cm_percent, 
                   annot=cm,  # Show counts
                   fmt='d',
                   cmap='Blues',
                   xticklabels=classes,
                   yticklabels=classes,
                   cbar_kws={'label': 'Proportion'},
                   ax=ax,
                   linewidths=0.5)
        
        ax.set_xlabel('Predicted Label', fontsize=12, fontweight='bold')
        ax.set_ylabel('True Label', fontsize=12, fontweight='bold')
        ax.set_title('Confusion Matrix (Counts shown)', fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=self.DPI, bbox_inches='tight')
        plt.close()
        
        if self.verbose:
            print(f"✓ Saved: {filename}")
    
    def plot_feature_importance(self, 
                               feature_importance_df: pd.DataFrame,
                               top_n: int = 15,
                               filename: str = 'feature_importance.png'):
        """
        Plot feature importance bar chart.
        
        Args:
            feature_importance_df: DataFrame with features and importances
            top_n: Number of top features to display
            filename: Output filename
        """
        top_features = feature_importance_df.head(top_n)
        
        fig, ax = plt.subplots(figsize=self.FIGSIZE_MEDIUM)
        
        bars = ax.barh(range(len(top_features)), top_features['Importance'].values,
                       color=plt.cm.viridis(np.linspace(0.3, 0.9, len(top_features))),
                       edgecolor='black', linewidth=1)
        
        ax.set_yticks(range(len(top_features)))
        ax.set_yticklabels(top_features['Feature'].values)
        ax.set_xlabel('Importance Score', fontsize=12, fontweight='bold')
        ax.set_title(f'Top {top_n} Feature Importance', fontsize=14, fontweight='bold', pad=20)
        ax.invert_yaxis()
        
        # Add value labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                   f'{width:.4f}',
                   ha='left', va='center', fontsize=9, fontweight='bold')
        
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=self.DPI, bbox_inches='tight')
        plt.close()
        
        if self.verbose:
            print(f"✓ Saved: {filename}")
    
    def plot_class_performance(self,
                              precision: List[float],
                              recall: List[float],
                              f1: List[float],
                              classes: List[str],
                              filename: str = 'class_performance.png'):
        """
        Plot precision/recall/f1 by class.
        
        Args:
            precision: Precision scores per class
            recall: Recall scores per class
            f1: F1 scores per class
            classes: Class names
            filename: Output filename
        """
        x = np.arange(len(classes))
        width = 0.25
        
        fig, ax = plt.subplots(figsize=self.FIGSIZE_MEDIUM)
        
        bars1 = ax.bar(x - width, precision, width, label='Precision', 
                      color='#3498db', edgecolor='black', linewidth=1)
        bars2 = ax.bar(x, recall, width, label='Recall', 
                      color='#2ecc71', edgecolor='black', linewidth=1)
        bars3 = ax.bar(x + width, f1, width, label='F1-Score', 
                      color='#f39c12', edgecolor='black', linewidth=1)
        
        ax.set_ylabel('Score', fontsize=12, fontweight='bold')
        ax.set_title('Class-wise Performance Metrics', fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(classes)
        ax.legend(fontsize=11, loc='lower right')
        ax.set_ylim([0, 1.1])
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=self.DPI, bbox_inches='tight')
        plt.close()
        
        if self.verbose:
            print(f"✓ Saved: {filename}")
    
    def plot_roc_curves(self,
                       y_true: np.ndarray,
                       y_proba: np.ndarray,
                       classes: List[str],
                       filename: str = 'roc_curves.png'):
        """
        Plot ROC curves for multi-class.
        
        Args:
            y_true: True labels
            y_proba: Predicted probabilities
            classes: Class names
            filename: Output filename
        """
        from sklearn.preprocessing import label_binarize
        
        n_classes = len(classes)
        y_bin = label_binarize(y_true, classes=np.arange(n_classes))
        
        fig, ax = plt.subplots(figsize=self.FIGSIZE_MEDIUM)
        
        colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12']
        
        for i in range(n_classes):
            fpr, tpr, _ = roc_curve(y_bin[:, i], y_proba[:, i])
            roc_auc = auc(fpr, tpr)
            
            ax.plot(fpr, tpr, color=colors[i], lw=2.5,
                   label=f'{classes[i]} (AUC = {roc_auc:.4f})')
        
        # Plot diagonal
        ax.plot([0, 1], [0, 1], 'k--', lw=2, label='Random Classifier')
        
        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.05])
        ax.set_xlabel('False Positive Rate', fontsize=12, fontweight='bold')
        ax.set_ylabel('True Positive Rate', fontsize=12, fontweight='bold')
        ax.set_title('ROC Curves (Multi-class)', fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc="lower right", fontsize=11)
        ax.grid(alpha=0.3)
        
        plt.tight_layout()
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=self.DPI, bbox_inches='tight')
        plt.close()
        
        if self.verbose:
            print(f"✓ Saved: {filename}")
    
    def plot_correlation_matrix(self,
                               X: pd.DataFrame,
                               filename: str = 'correlation_matrix.png'):
        """
        Plot feature correlation heatmap.
        
        Args:
            X: Feature dataframe
            filename: Output filename
        """
        corr_matrix = X.corr()
        
        fig, ax = plt.subplots(figsize=self.FIGSIZE_LARGE)
        
        sns.heatmap(corr_matrix, 
                   annot=True, 
                   fmt='.2f',
                   cmap='coolwarm',
                   center=0,
                   square=True,
                   linewidths=0.5,
                   cbar_kws={'label': 'Correlation'},
                   ax=ax)
        
        ax.set_title('Feature Correlation Matrix', fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=self.DPI, bbox_inches='tight')
        plt.close()
        
        if self.verbose:
            print(f"✓ Saved: {filename}")
    
    def plot_learning_curves(self,
                            train_sizes: List[int],
                            train_scores: List[float],
                            test_scores: List[float],
                            filename: str = 'learning_curves.png'):
        """
        Plot learning curves.
        
        Args:
            train_sizes: Training set sizes
            train_scores: Training scores
            test_scores: Validation scores
            filename: Output filename
        """
        train_mean = np.mean(train_scores, axis=1)
        train_std = np.std(train_scores, axis=1)
        test_mean = np.mean(test_scores, axis=1)
        test_std = np.std(test_scores, axis=1)
        
        fig, ax = plt.subplots(figsize=self.FIGSIZE_MEDIUM)
        
        ax.plot(train_sizes, train_mean, 'o-', color='#3498db', 
               linewidth=2.5, markersize=8, label='Training Score')
        ax.fill_between(train_sizes, train_mean - train_std, train_mean + train_std,
                       alpha=0.2, color='#3498db')
        
        ax.plot(train_sizes, test_mean, 'o-', color='#e74c3c',
               linewidth=2.5, markersize=8, label='Validation Score')
        ax.fill_between(train_sizes, test_mean - test_std, test_mean + test_std,
                       alpha=0.2, color='#e74c3c')
        
        ax.set_xlabel('Training Set Size', fontsize=12, fontweight='bold')
        ax.set_ylabel('Accuracy Score', fontsize=12, fontweight='bold')
        ax.set_title('Learning Curves', fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='lower right', fontsize=11)
        ax.grid(alpha=0.3)
        ax.set_ylim([0, 1.05])
        
        plt.tight_layout()
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=self.DPI, bbox_inches='tight')
        plt.close()
        
        if self.verbose:
            print(f"✓ Saved: {filename}")
