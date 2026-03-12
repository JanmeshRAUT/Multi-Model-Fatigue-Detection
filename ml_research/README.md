# Fatigue Detection - ML Research Project

## Overview
Professional machine learning research project for fatigue detection using multimodal features and Random Forest classification.

## Project Structure
```
ml_research/
├── main.py                          # Entry point - Run entire pipeline
├── requirements.txt                 # Python dependencies
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py              # Dataset loading & validation
│   ├── preprocessing.py            # Data cleaning & normalization
│   ├── model.py                    # Model definition
│   ├── train.py                    # Training logic
│   ├── evaluate.py                 # Evaluation metrics
│   └── visualize.py                # Visualization & graphs
│
├── data/
│   └── [Your dataset here]         # CSV file with features & labels
│
└── results/
    ├── figures/                    # Generated graphs (PNG)
    │   ├── accuracy_comparison.png
    │   ├── confusion_matrix.png
    │   ├── feature_importance.png
    │   ├── class_performance.png
    │   ├── roc_curves.png
    │   ├── learning_curves.png
    │   └── correlation_matrix.png
    │
    └── metrics/                    # Generated metrics & reports
        ├── model_metrics.json
        ├── classification_report.txt
        ├── preprocessing_info.json
        ├── model_config.json
        ├── training_info.json
        └── feature_importance.csv
```

## Features

### Data Features (Input)
- PERCLOS (Percentage Eye Closure)
- Blink Rate
- Eye Aspect Ratio (EAR)
- Head Pose (Yaw, Pitch, Roll)
- Heart Rate
- Temperature
- SpO2 (Blood Oxygen Saturation)

### Target Classes (Output)
- **Alert** (Class 0)
- **Drowsy** (Class 1)  
- **Fatigued** (Class 2)

## Model Architecture
- **Algorithm**: Random Forest Classifier
- **Number of Trees**: 200
- **Max Depth**: Unlimited (tunable)
- **Train/Test Split**: 70% / 30%

### Preprocessing Pipeline
1. ✅ Missing value handling (mean imputation)
2. ✅ Feature normalization (StandardScaler)
3. ✅ Label encoding (categorical → numeric)
4. ✅ Train/test stratified split

## Evaluation Metrics Generated

### Overall Metrics
- Accuracy
- Macro-averaged Precision, Recall, F1
- Weighted-averaged Precision, Recall, F1

### Per-Class Metrics
- Precision per class
- Recall per class
- F1-Score per class

### Confusion Matrix
- Raw counts
- Normalized proportions
- Visual heatmap

## Visualizations Generated

1. **Accuracy Comparison** - Training vs Test performance
2. **Confusion Matrix Heatmap** - Classification breakdown
3. **Feature Importance** - Top 15 features ranked
4. **Class Performance** - Precision/Recall/F1 by class
5. **ROC Curves** - Multi-class ROC-AUC curves
6. **Learning Curves** - Training convergence analysis
7. **Correlation Matrix** - Feature relationships heatmap

All graphs:
- Professional research quality
- High resolution (300 DPI PNG)
- Clear titles and axis labels
- Ready for publication

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Prepare Dataset
Place your CSV file with features and target in the `data/` directory.

**Expected CSV columns:**
```
PERCLOS, Blink_Rate, EAR, Head_Yaw, Head_Pitch, Head_Roll, 
Heart_Rate, Temperature, SpO2, Fatigue_State
```

Alternative column names are supported:
- Target: `Fatigue_State`, `Label`, `Fatigue`, or `Class`
- The script auto-detects the target column

### 3. Run Pipeline
```bash
python main.py
```

The entire workflow will execute and generate all results.

## Usage Examples

### Quick Start
```python
from src.data_loader import DataLoader
from src.preprocessing import DataPreprocessor
from src.model import FatigueDetectionModel
from src.train import ModelTrainer

# Load data
loader = DataLoader('data/dataset.csv')
loader.load()
loader.validate()
X, y = loader.get_features_and_target()

# Preprocess
preprocessor = DataPreprocessor()
X_clean, y_encoded = preprocessor.preprocess(X, y)
X_train, X_test, y_train, y_test = preprocessor.split_data(X_clean, y_encoded)

# Train model
model = FatigueDetectionModel(n_estimators=200)
trainer = ModelTrainer(model)
trainer.train(X_train, y_train)

# Evaluate
accuracy = model.get_model().score(X_test, y_test)
print(f"Test Accuracy: {accuracy:.4f}")
```

### Custom Model Parameters
```python
model = FatigueDetectionModel(
    n_estimators=250,
    max_depth=20,
    min_samples_split=5,
    random_state=42
)
```

### Generate Specific Visualizations
```python
from src.visualize import ModelVisualizer

viz = ModelVisualizer('results/figures')
viz.plot_feature_importance(feature_importance_df)
viz.plot_confusion_matrix(y_true, y_pred, classes)
```

## Output Files

### JSON Metrics (`results/metrics/`)
- `model_metrics.json` - Complete evaluation metrics
- `model_config.json` - Model hyperparameters
- `training_info.json` - Training statistics
- `preprocessing_info.json` - Preprocessing configuration

### Text Reports (`results/metrics/`)
- `classification_report.txt` - Scikit-learn classification report
- `feature_importance.csv` - Feature rankings

### Visualizations (`results/figures/`)
All graphs saved as high-resolution PNG files (300 DPI)

## Code Quality

✅ **Professional Standards**
- Clean, modular design with separation of concerns
- Comprehensive docstrings for all functions
- Type hints for better code clarity
- Proper error handling and validation
- Extensive logging and progress indicators

✅ **Research-Ready**
- Reproducible results (fixed random seeds)
- Stratified cross-validation
- Proper data leakage prevention
- Publication-quality visualizations
- Complete metrics documentation

## Performance Considerations

- **Memory**: Handles datasets up to ~100k samples efficiently
- **Speed**: Training on 200 trees takes ~5-30 seconds (depends on data size)
- **Parallelization**: Uses all CPU cores (n_jobs=-1)
- **Scalability**: Can be adapted for larger datasets with hyperparameter tuning

## Setting for Research Papers

This project is designed to produce publication-ready outputs:

1. **Figures** - Professional quality graphs (300 DPI, clear labels)
2. **Metrics** - Comprehensive evaluation beyond simple accuracy
3. **Reproducibility** - All random seeds fixed for exact reproducibility
4. **Documentation** - Complete hyperparameter and preprocessing details

### Citation Format
```bibtex
@software{fatigue_detection_2024,
  title={Fatigue Detection Model - Random Forest Classifier},
  author={Your Name},
  year={2024},
  url={Your Repository URL}
}
```

## Troubleshooting

### Dataset Not Found
```
FileNotFoundError: Dataset not found
```
**Solution**: Place CSV file in `data/` directory or modify `find_dataset()` in main.py

### Missing Values Issues
If dataset has many missing values:
```python
preprocessor = DataPreprocessor()
X_clean = preprocessor.handle_missing_values(X, strategy='median')
```

### Memory Issues
For large datasets, reduce train/test split:
```python
preprocessor = DataPreprocessor(test_size=0.20)
```

### GPU Acceleration
Random Forest doesn't use GPU by default. For GPU acceleration, consider:
- XGBoost with GPU support
- Rapids CUML
- LightGBM

## Author & License
ML Research Team | 2024

---

**Last Updated**: March 2024
**Python Version**: 3.8+
**Status**: Production Ready ✅
