"""
Main Pipeline Script
====================
Complete fatigue detection model training and evaluation pipeline.

Usage:
    python main.py

Author: ML Research Team
"""

import os
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_loader import DataLoader
from preprocessing import DataPreprocessor
from model import FatigueDetectionModel
from train import ModelTrainer
from evaluate import ModelEvaluator
from visualize import ModelVisualizer

import numpy as np
from sklearn.model_selection import learning_curve


def find_dataset():
    """Find available dataset in project."""
    # Check common locations
    possible_paths = [
        'data/fatigue_dataset.csv',
        '../ml_model/Dataset.csv',
        '../backend/Dataset.csv',
        '../backend/fatigue_dataset_80_accuracy.csv',
        'Dataset.csv'
    ]
    
    for path in possible_paths:
        full_path = os.path.join(os.path.dirname(__file__), path)
        if os.path.exists(full_path):
            return os.path.abspath(full_path)
    
    # If no dataset found, raise error
    raise FileNotFoundError(
        "Dataset not found. Please place a CSV file in data/ directory or specify path.\n"
        f"Searched in: {possible_paths}"
    )


def print_header():
    """Print pipeline header."""
    print("\n" + "="*70)
    print(" "*15 + "FATIGUE DETECTION MODEL")
    print(" "*10 + "Training & Evaluation Pipeline")
    print("="*70 + "\n")


def print_footer():
    """Print pipeline footer."""
    print("\n" + "="*70)
    print(" "*20 + "PIPELINE COMPLETE!")
    print(" "*10 + "Check results/ directory for outputs")
    print("="*70 + "\n")


def generate_learning_curves(model, X_train, y_train, output_dir='results/figures'):
    """
    Generate and plot learning curves.
    
    Args:
        model: Trained model
        X_train: Training features
        y_train: Training labels
        output_dir: Output directory
    """
    print("\n🔧 Generating learning curves...")
    
    train_sizes, train_scores, val_scores = learning_curve(
        model.get_model(),
        X_train, y_train,
        cv=5,
        train_sizes=np.linspace(0.1, 1.0, 10),
        n_jobs=-1,
        scoring='accuracy',
        verbose=0
    )
    
    visualizer = ModelVisualizer(output_dir=output_dir, verbose=False)
    visualizer.plot_learning_curves(train_sizes, train_scores, val_scores)
    
    return train_sizes, train_scores, val_scores


def main():
    """Execute complete pipeline."""
    
    print_header()
    
    # =====================================================================
    # 1. DATA LOADING
    # =====================================================================
    print("📍 STEP 1: DATA LOADING")
    print("-" * 70)
    
    dataset_path = find_dataset()
    print(f"Found dataset: {dataset_path}\n")
    
    data_loader = DataLoader(dataset_path, verbose=True)
    data = data_loader.load()
    data_loader.validate()
    data_loader.print_summary()
    
    # Get features and target
    X, y = data_loader.get_features_and_target()
    feature_names = data_loader.feature_names
    
    # =====================================================================
    # 2. DATA PREPROCESSING
    # =====================================================================
    print("📍 STEP 2: DATA PREPROCESSING")
    print("-" * 70)
    
    preprocessor = DataPreprocessor(random_state=42, test_size=0.30, verbose=True)
    X_clean, y_encoded = preprocessor.preprocess(X, y)
    X_train, X_test, y_train, y_test = preprocessor.split_data(X_clean, y_encoded)
    
    # =====================================================================
    # 3. MODEL INITIALIZATION
    # =====================================================================
    print("📍 STEP 3: MODEL INITIALIZATION")
    print("-" * 70)
    
    model = FatigueDetectionModel(
        n_estimators=200,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        random_state=42,
        n_jobs=-1,
        verbose=True
    )
    
    # =====================================================================
    # 4. MODEL TRAINING
    # =====================================================================
    print("📍 STEP 4: MODEL TRAINING")
    print("-" * 70)
    
    trainer = ModelTrainer(model, verbose=True)
    training_info = trainer.train(X_train, y_train)
    
    # Evaluate on train/test
    accuracy_scores = trainer.evaluate_on_train_test(
        X_train, y_train,
        X_test, y_test
    )
    
    # Get feature importance
    feature_importance = trainer.get_feature_importance(feature_names)
    
    # =====================================================================
    # 5. MODEL EVALUATION
    # =====================================================================
    print("📍 STEP 5: MODEL EVALUATION")
    print("-" * 70)
    
    evaluator = ModelEvaluator(model, preprocessor.label_encoder, verbose=True)
    metrics = evaluator.calculate_metrics(X_test, y_test)
    
    # Get ROC data
    roc_data = evaluator.get_roc_data(X_test, y_test)
    
    # =====================================================================
    # 6. VISUALIZATION & RESULTS
    # =====================================================================
    print("📍 STEP 6: GENERATING VISUALIZATIONS")
    print("-" * 70)
    
    os.makedirs('results/figures', exist_ok=True)
    os.makedirs('results/metrics', exist_ok=True)
    
    visualizer = ModelVisualizer(output_dir='results/figures', verbose=True)
    
    # 1. Accuracy comparison
    visualizer.plot_accuracy_comparison(
        accuracy_scores['train_accuracy'],
        accuracy_scores['test_accuracy']
    )
    
    # 2. Confusion matrix
    y_pred = model.get_model().predict(X_test)
    visualizer.plot_confusion_matrix(
        y_test, y_pred,
        preprocessor.label_encoder.classes_
    )
    
    # 3. Feature importance
    visualizer.plot_feature_importance(feature_importance)
    
    # 4. Class performance
    visualizer.plot_class_performance(
        metrics['precision_per_class'],
        metrics['recall_per_class'],
        metrics['f1_per_class'],
        preprocessor.label_encoder.classes_
    )
    
    # 5. ROC curves
    y_proba = model.get_model().predict_proba(X_test)
    visualizer.plot_roc_curves(
        y_test, y_proba,
        preprocessor.label_encoder.classes_
    )
    
    # 6. Learning curves
    generate_learning_curves(model, X_train, y_train)
    
    # 7. Correlation matrix
    visualizer.plot_correlation_matrix(X_train)
    
    # =====================================================================
    # 7. SAVE METRICS & REPORTS
    # =====================================================================
    print("\n📍 STEP 7: SAVING METRICS & REPORTS")
    print("-" * 70)
    
    # Save metrics JSON
    evaluator.save_metrics('results/metrics/model_metrics.json')
    
    # Save classification report
    evaluator.save_classification_report('results/metrics/classification_report.txt')
    
    # Save preprocessing info
    with open('results/metrics/preprocessing_info.json', 'w') as f:
        json.dump(preprocessor.get_preprocessing_info(), f, indent=4)
    
    # Save model config
    with open('results/metrics/model_config.json', 'w') as f:
        json.dump(model.get_config(), f, indent=4)
    
    # Save training info
    with open('results/metrics/training_info.json', 'w') as f:
        json.dump(trainer.get_training_info(), f, indent=4)
    
    # Save feature importance
    feature_importance.to_csv('results/metrics/feature_importance.csv', index=False)
    
    # =====================================================================
    # 8. FINAL SUMMARY
    # =====================================================================
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    
    print(f"\n📊 Dataset Statistics:")
    print(f"  • Total samples: {len(data)}")
    print(f"  • Training samples: {len(X_train)}")
    print(f"  • Testing samples: {len(X_test)}")
    print(f"  • Number of features: {len(feature_names)}")
    print(f"  • Number of classes: {len(preprocessor.label_encoder.classes_)}")
    
    print(f"\n🎯 Model Performance:")
    print(f"  • Training Accuracy: {accuracy_scores['train_accuracy']:.4f}")
    print(f"  • Testing Accuracy: {accuracy_scores['test_accuracy']:.4f}")
    print(f"  • Macro F1-Score: {metrics['macro_f1']:.4f}")
    print(f"  • Weighted F1-Score: {metrics['weighted_f1']:.4f}")
    
    print(f"\n⏱️  Training Time: {trainer.training_time:.2f} seconds")
    
    print(f"\n📁 Output Files Generated:")
    print(f"  ✓ results/figures/ - All visualizations (7 graphs)")
    print(f"  ✓ results/metrics/model_metrics.json - Complete metrics")
    print(f"  ✓ results/metrics/classification_report.txt - Classification report")
    print(f"  ✓ results/metrics/preprocessing_info.json - Preprocessing details")
    print(f"  ✓ results/metrics/model_config.json - Model configuration")
    print(f"  ✓ results/metrics/training_info.json - Training details")
    print(f"  ✓ results/metrics/feature_importance.csv - Feature rankings")
    
    print_footer()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
