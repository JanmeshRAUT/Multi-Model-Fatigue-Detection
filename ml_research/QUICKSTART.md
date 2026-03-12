# Quick Start Guide - Fatigue Detection ML Research Project

## Complete Setup in 3 Minutes

### Step 1: Install Dependencies (1 min)
```bash
pip install -r requirements.txt
```

### Step 2: Create Sample Dataset (30 sec)
```bash
python create_sample_dataset.py
```

This generates a synthetic 500-sample dataset in `data/fatigue_dataset.csv`

### Step 3: Run Complete Pipeline (2 min)
```bash
python main.py
```

**That's it!** 🎉 The entire ML workflow will execute:
- ✅ Data loading and validation
- ✅ Preprocessing and normalization
- ✅ Model training (200 trees)
- ✅ Comprehensive evaluation
- ✅ 7 research-quality graphs
- ✅ Detailed metrics and reports

---

## Expected Output

### Console Output
```
======================================================================
                    FATIGUE DETECTION MODEL
              Training & Evaluation Pipeline
======================================================================

📍 STEP 1: DATA LOADING
...

📍 STEP 2: DATA PREPROCESSING
...

📍 STEP 3: MODEL INITIALIZATION
...

[... training progress ...]

======================================================================
                         PIPELINE COMPLETE!
              Check results/ directory for outputs
======================================================================
```

### Generated Files
```
results/
├── figures/
│   ├── accuracy_comparison.png
│   ├── confusion_matrix.png
│   ├── feature_importance.png
│   ├── class_performance.png
│   ├── roc_curves.png
│   ├── learning_curves.png
│   └── correlation_matrix.png
│
└── metrics/
    ├── model_metrics.json
    ├── classification_report.txt
    ├── preprocessing_info.json
    ├── model_config.json
    ├── training_info.json
    └── feature_importance.csv
```

---

## Using Your Own Dataset

### Option 1: Place in data/ directory
1. Copy your CSV file to `data/` folder
2. Run: `python main.py`
3. Script auto-detects your data

### Option 2: Expected CSV Format
```csv
PERCLOS,Blink_Rate,EAR,Head_Yaw,Head_Pitch,Head_Roll,Heart_Rate,Temperature,SpO2,Fatigue_State
0.15,12.5,0.45,2.3,1.2,0.8,72,36.5,98,0
0.32,8.2,0.32,5.1,-2.3,2.1,68,37.0,96,1
0.65,3.8,0.18,10.2,-8.5,5.3,55,37.5,94,2
...
```

### Option 3: Custom Dataset Script
Modify `create_sample_dataset.py` to load your actual data:
```python
def create_sample_dataset():
    df = pd.read_csv('your_dataset.csv')
    return df
```

---

## Understanding the Results

### Key Metrics (in console and JSON)
- **Accuracy**: Overall correct classifications
- **Precision**: How many predicted alerts were correct
- **Recall**: How many actual alerts were found
- **F1-Score**: Balance between precision and recall
- **AUC-ROC**: Multi-class ROC-AUC scores

### Graphs Explained

1. **Accuracy Comparison** - Shows if model overfits
   - Gap < 10% = Good generalization

2. **Confusion Matrix** - Shows where model makes mistakes
   - Diagonal = Correct predictions
   - Off-diagonal = Misclassifications

3. **Feature Importance** - Which features matter most
   - Higher bar = More important
   - Use for feature selection

4. **Class Performance** - Per-class metrics
   - Compare precision/recall for each fatigue state

5. **ROC Curves** - Multi-class classification performance
   - Area under curve (AUC) = Discrimination ability
   - Perfect classifier = AUC = 1.0

6. **Learning Curves** - Model convergence
   - Lines converging = Good learning
   - Large gap = Underfitting

7. **Correlation Matrix** - Feature relationships
   - Dark red = Positively correlated
   - Dark blue = Negatively correlated

---

## Common Tasks

### Tune Model Hyperparameters
Edit in `main.py`:
```python
model = FatigueDetectionModel(
    n_estimators=300,      # Increase trees
    max_depth=15,          # Limit depth
    min_samples_leaf=5     # Prevent overfitting
)
```

### Use Different Test Split
In `main.py`:
```python
preprocessor = DataPreprocessor(
    test_size=0.20,  # 80/20 split instead of 70/30
    random_state=42
)
```

### Generate Only Specific Graphs
```python
from src.visualize import ModelVisualizer

viz = ModelVisualizer('results/figures')
viz.plot_feature_importance(feature_df)  # Only this graph
```

### Extract Metrics Programmatically
```python
import json

with open('results/metrics/model_metrics.json') as f:
    metrics = json.load(f)
    
accuracy = metrics['overall_metrics']['accuracy']
f1_scores = metrics['per_class_metrics']['f1_score']
print(f"Accuracy: {accuracy}")
```

---

## Troubleshooting

### Module Not Found
```
ModuleNotFoundError: No module named 'sklearn'
```
→ Run: `pip install -r requirements.txt`

### Dataset Not Found
```
FileNotFoundError: Dataset not found
```
→ Run: `python create_sample_dataset.py`
→ Or place CSV in `data/` folder

### Permission Denied (Results folder)
→ Run: `mkdir -p results/figures results/metrics`
→ Make sure you have write permissions

### Out of Memory
→ Use smaller `test_size` in preprocessing
→ Or reduce number of samples for testing

---

## For Research Papers

### Citation
```bibtex
@software{fatigue_detection_2024,
  title={Fatigue Detection: Random Forest Multimodal Classification},
  year={2024}
}
```

### Export Results
All metrics and graphs are saved:
- **Graphs**: `results/figures/*.png` (300 DPI, publication-ready)
- **Metrics**: `results/metrics/*.json` (machine-readable)
- **Reports**: `results/metrics/*.txt` (human-readable)

### Include in Paper
```
This work uses a Random Forest classifier with 200 trees trained on 
7 multimodal features (PERCLOS, Blink Rate, EAR, Head Pose, Heart Rate, 
Temperature, SpO2) to classify three fatigue states (Alert, Drowsy, 
Fatigued). The model achieves [see accuracy_comparison.png] accuracy 
on a [n] sample dataset with [see confusion_matrix.png] class-wise 
performance.
```

---

## Next Steps

1. **Run pipeline**: `python main.py`
2. **Check results**: Open HTML report (coming soon)
3. **Analyze metrics**: `results/metrics/model_metrics.json`
4. **Use graphs**: `results/figures/*.png`
5. **Integrate model**: Import from `src/model.py`

---

## Contact & Support
For issues or questions about the pipeline, refer to:
- `README.md` - Complete documentation
- Code docstrings - Function-level documentation
- Example usage in each module

---

**Happy Researching! 🧬📊**
