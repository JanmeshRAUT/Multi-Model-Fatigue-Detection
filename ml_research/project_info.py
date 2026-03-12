"""
Project Information & Setup Verification
===========================================
Displays information about the project and verifies setup.

Usage:
    python project_info.py
"""

import os
import sys
from pathlib import Path


def print_header():
    """Print header."""
    print("\n" + "="*70)
    print("FATIGUE DETECTION ML RESEARCH PROJECT")
    print("="*70 + "\n")


def print_project_structure():
    """Print project structure."""
    print("📁 PROJECT STRUCTURE")
    print("-" * 70)
    
    structure = """
ml_research/
├── 📄 ENTRY POINTS
│   ├── main.py                    → Run complete ML pipeline
│   ├── create_sample_dataset.py   → Generate test data
│   └── project_info.py            → This file
│
├── 📄 CONFIGURATION
│   ├── config.py                  → Hyperparameters & presets
│   ├── requirements.txt           → Python dependencies
│   └── .env (optional)            → Environment variables
│
├── 📂 SOURCE CODE (src/)
│   ├── data_loader.py             → Load & validate datasets
│   ├── preprocessing.py           → Cleaning & normalization
│   ├── model.py                   → Model definition
│   ├── train.py                   → Training logic
│   ├── evaluate.py                → Evaluation metrics
│   └── visualize.py               → Graph generation
│
├── 📂 DATA (data/)
│   └── fatigue_dataset.csv        → Your dataset here
│
├── 📂 RESULTS (results/)
│   ├── figures/                   → Generated graphs (PNG)
│   └── metrics/                   → JSON, CSV, TXT outputs
│
└── 📚 DOCUMENTATION
    ├── README.md                  → Complete documentation
    ├── QUICKSTART.md              → 3-minute setup guide
    └── PROJECT_SUMMARY.md         → Detailed summary
    """
    
    print(structure)


def print_file_descriptions():
    """Print file descriptions."""
    print("\n📄 KEY FILES EXPLAINED")
    print("-" * 70)
    
    files = {
        "main.py": "Complete pipeline in one command",
        "create_sample_dataset.py": "Generate 500 synthetic samples",
        "config.py": "Configure all parameters",
        "data_loader.py": "Load CSV, auto-detect structure",
        "preprocessing.py": "Clean, normalize, encode data",
        "model.py": "Random Forest definition",
        "train.py": "Train & monitor model",
        "evaluate.py": "Calculate 10+ metrics",
        "visualize.py": "Generate 7 publication graphs",
        "requirements.txt": "Install: pip install -r requirements.txt"
    }
    
    for file, desc in files.items():
        print(f"  {file:30s} → {desc}")


def print_quick_commands():
    """Print quick commands."""
    print("\n⚡ QUICK COMMANDS")
    print("-" * 70)
    
    commands = [
        ("pip install -r requirements.txt", "Install dependencies"),
        ("python create_sample_dataset.py", "Generate test dataset"),
        ("python main.py", "Run complete ML pipeline"),
        ("python config.py", "Show configuration presets"),
        ("python project_info.py", "Show this information"),
    ]
    
    for cmd, desc in commands:
        print(f"  {cmd:40s} → {desc}")


def verify_setup():
    """Verify project setup."""
    print("\n✓ SETUP VERIFICATION")
    print("-" * 70)
    
    checks = {
        'README.md': 'Documentation',
        'QUICKSTART.md': 'Quick start guide',
        'PROJECT_SUMMARY.md': 'Project summary',
        'main.py': 'Main pipeline script',
        'create_sample_dataset.py': 'Sample data generator',
        'config.py': 'Configuration system',
        'requirements.txt': 'Dependencies',
        'src/data_loader.py': 'Data loading module',
        'src/preprocessing.py': 'Preprocessing module',
        'src/model.py': 'Model definition module',
        'src/train.py': 'Training module',
        'src/evaluate.py': 'Evaluation module',
        'src/visualize.py': 'Visualization module',
    }
    
    all_good = True
    for file, desc in checks.items():
        exists = os.path.exists(file)
        status = "✓" if exists else "✗"
        print(f"  {status} {desc:30s} → {file}")
        if not exists:
            all_good = False
    
    if all_good:
        print("\n  ✅ All files present and ready!")
    else:
        print("\n  ⚠️  Some files missing. Verify installation.")
    
    return all_good


def print_next_steps():
    """Print next steps."""
    print("\n🚀 NEXT STEPS")
    print("-" * 70)
    
    steps = """
1. INSTALL DEPENDENCIES (1 minute)
   $ pip install -r requirements.txt

2. CREATE SAMPLE DATA (30 seconds)
   $ python create_sample_dataset.py
   This creates data/fatigue_dataset.csv with 500 samples

3. RUN PIPELINE (2 minutes)
   $ python main.py
   Complete ML workflow with all outputs

4. CHECK RESULTS
   results/figures/       → 7 publication-quality graphs
   results/metrics/       → Complete metrics & reports

5. CUSTOMIZE (Optional)
   - Edit config.py for hyperparameters
   - Modify presets in Presets class
   - Use your own dataset in data/
    """
    
    print(steps)


def print_dataset_format():
    """Print expected dataset format."""
    print("\n📊 DATASET FORMAT")
    print("-" * 70)
    
    format_info = """
Expected CSV columns (auto-detected):
  PERCLOS, Blink_Rate, EAR, Head_Yaw, Head_Pitch, Head_Roll, 
  Heart_Rate, Temperature, SpO2, [TARGET_COLUMN]

Target column auto-detection:
  Looks for: Fatigue_State, Label, Fatigue, or Class

Example:
  PERCLOS  Blink_Rate  EAR   Head_Yaw  ...  Temperature  SpO2  Fatigue_State
  0.15     12.5       0.45  2.3       ...  36.5         98    0
  0.35     8.2        0.32  5.1       ...  37.0         96    1
  0.65     3.8        0.18  10.2      ...  37.5         94    2

Supported formats:
  ✓ CSV files
  ✓ Any feature column names (auto-detected)
  ✓ Any target column name (auto-detected)
  ✓ Missing values (auto-imputed)
    """
    
    print(format_info)


def print_features_and_targets():
    """Print features and target classes."""
    print("\n🎯 FEATURES & TARGET CLASSES")
    print("-" * 70)
    
    info = """
INPUT FEATURES (9 total):
  1. PERCLOS              → Percentage Eye Closure (0-1)
  2. Blink_Rate           → Blinks per minute
  3. EAR                  → Eye Aspect Ratio (0-1)
  4. Head_Yaw             → Head rotation (degrees)
  5. Head_Pitch           → Head tilt (degrees)
  6. Head_Roll            → Head lateral tilt (degrees)
  7. Heart_Rate           → Beats per minute
  8. Temperature          → Body temperature (°C)
  9. SpO2                 → Blood oxygen saturation (%)

TARGET CLASSES (3 total):
  Class 0: Alert       → Fully awake, attentive
  Class 1: Drowsy      → Showing drowsiness signs
  Class 2: Fatigued    → Severe fatigue, critical
    """
    
    print(info)


def print_model_info():
    """Print model information."""
    print("\n🤖 MODEL CONFIGURATION")
    print("-" * 70)
    
    info = """
Algorithm: Random Forest Classifier

Default Parameters:
  • n_estimators: 200 trees
  • max_depth: None (unlimited)
  • min_samples_split: 2
  • min_samples_leaf: 1
  • random_state: 42 (reproducible)
  • n_jobs: -1 (use all cores)

Train/Test Split:
  • Training: 70% of data
  • Testing: 30% of data
  • Stratified: Maintains class distribution

Preprocessing:
  • Missing values: Mean imputation
  • Feature scaling: StandardScaler (z-score)
  • Label encoding: Categorical → Numeric
    """
    
    print(info)


def print_outputs():
    """Print expected outputs."""
    print("\n📊 EXPECTED OUTPUTS")
    print("-" * 70)
    
    info = """
GRAPHS (PNG, 300 DPI, Publication-Quality):
  1. accuracy_comparison.png      → Train vs Test bars
  2. confusion_matrix.png         → Classification heatmap
  3. feature_importance.png       → Top 15 features
  4. class_performance.png        → Precision/Recall/F1 by class
  5. roc_curves.png              → Multi-class ROC-AUC
  6. learning_curves.png          → Training convergence
  7. correlation_matrix.png       → Feature correlation

METRICS & REPORTS:
  • model_metrics.json            → Complete metrics
  • classification_report.txt     → Detailed report
  • feature_importance.csv        → Feature rankings
  • preprocessing_info.json       → Preprocessing details
  • model_config.json            → Model parameters
  • training_info.json           → Training statistics

CONSOLE OUTPUT:
  • Detailed pipeline progress
  • Dataset statistics
  • Model performance metrics
  • Training time
  • File location summary
    """
    
    print(info)


def print_research_integration():
    """Print research paper integration info."""
    print("\n📚 RESEARCH PAPER INTEGRATION")
    print("-" * 70)
    
    info = """
READY FOR PUBLICATION:
  ✓ Comprehensive evaluation metrics
  ✓ Publication-quality graphs (300 DPI)
  ✓ Reproducible results (fixed random seeds)
  ✓ Complete methodology documentation
  ✓ Per-class performance breakdown

WHAT TO INCLUDE IN PAPER:
  • Methods: Model config + preprocessing details
  • Results: Accuracy, F1-scores, per-class metrics
  • Tables: Classification report, feature importance
  • Figures: All graphs from results/figures/

CITE THIS PROJECT:
  @software{fatigue_detection_2024,
    title={Fatigue Detection: Multimodal RF Classifier},
    author={Your Name},
    year={2024}
  }
    """
    
    print(info)


def print_footer():
    """Print footer."""
    print("\n" + "="*70)
    print("Ready to start? Run: python main.py")
    print("="*70 + "\n")


def main():
    """Main function."""
    print_header()
    print_project_structure()
    print_file_descriptions()
    print_quick_commands()
    print_dataset_format()
    print_features_and_targets()
    print_model_info()
    print_outputs()
    print_research_integration()
    verify_setup()
    print_next_steps()
    print_footer()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
