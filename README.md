# Parkinson's Disease Predictor — Neural Network from Scratch

A feedforward neural network built **from scratch with raw PyTorch tensors** (no `nn.Module`, no built-in optimizers) that predicts Parkinson's disease from voice biomarker data. Served via a FastAPI REST endpoint.

NOTE: This is for learning purpose, the dataset used here is highly imbalanced and significantly insufficient for generalization.
I picked this one intentionally, that too for learning stuff, nothing else.

---

## How It Works

Voice recordings contain measurable acoustic properties that differ between healthy individuals and those with Parkinson's. This model learns to classify those differences using 7 key features selected through feature engineering.

**Architecture:** `input(7) → Linear → ReLU → Linear(6) → ReLU → Linear(4) → Sigmoid(1)`

Everything — weight initialization, forward pass, binary cross-entropy loss, gradient updates — is implemented manually without high-level abstractions.

---

## Project Structure

```
parkinsons-nn/
├── model.py                  # Neural network class (ParkinsonNet)
├── app.py                    # FastAPI inference server
├── test.py                   # Standalone prediction sanity check
├── feature_engg.ipynb        # Feature selection & EDA
├── model_training.ipynb      # Training loop & evaluation
├── requirements.txt
└── model/
    ├── model.pth             # Saved weights checkpoint
    ├── scaler.pkl            # Fitted StandardScaler
    └── important_features.json  # Ordered list of selected features
```

---

## Quickstart

```bash
# 1. Clone and install
git clone https://github.com/Pmskabir1234/Parkinsons-FP.git
cd Parkinsons-FP
pip install -r requirements.txt

# 2. Run a sanity check prediction
python test.py

# 3. Start the API server
uvicorn app:app --reload
```

The API will be live at `http://127.0.0.1:8000`.

---

## API Usage

**Endpoint:** `POST /predict`

**Request body:**
```json
{
  "data": {
    "MDVP:Fo(Hz)": 145.32,
    "MDVP:Flo(Hz)": 72.45,
    "MDVP:RAP": 0.0047,
    "spread1": -4.12,
    "spread2": 2.35,
    "D2": 2.98,
    "PPE": 0.214
  }
}
```

**Response:**
```json
{
  "prediction": 0.8423,
  "label": "Parkinson's Detected"
}
```

A score ≥ 0.5 is classified as **Parkinson's Detected**.

Interactive docs available at `http://127.0.0.1:8000/docs`. (after you run the backend)

---

## Model Evaluation & Results

### Methodology Improvements

The training pipeline was rebuilt with several critical engineering fixes over the naive baseline:

| Practice | What Changed | Impact |
|---|---|---|
| **Data Leakage Fix** | Scaler is now `fit` only on `X_train`, then `transform` applied to `X_test` | Eliminates inflated test metrics from information leakage |
| **Stratified Splitting** | `train_test_split` with `stratify=y` preserves the 75/25 class ratio | Prevents class-distribution mismatch between splits |
| **Weighted BCE Loss** | Minority class (healthy) upweighted ×1.5, majority ×0.4 | Counteracts the 3:1 class imbalance during training |
| **5-Fold Stratified CV** | `StratifiedKFold` (k=5) on SimpleNN for unbiased generalisation estimate | Validates stability across different data partitions |
| **Reproducibility** | Global seed (42) across `random`, `numpy`, `torch`, and `cudnn` | Fully deterministic results across runs |

### Hold-Out Test Set Performance (n = 49)

| Metric | Majority-Class | Logistic Regression | SimpleNN |
|:---|:---:|:---:|:---:|
| **Accuracy** | 75.51% | **75.51%** | 44.90% |
| **Precision** | 75.51% | **93.10%** | 67.86% |
| **Recall (Sensitivity)** | **100.00%** | 72.97% | 51.35% |
| **Specificity** | 0.00% | **83.33%** | 25.00% |
| **F1 Score** | 86.05% | **81.82%** | 58.46% |
| **MCC** | 0.0000 | **+0.4926** | −0.2055 |
| **AUC-ROC** | 0.5000 | **0.9324** | 0.3086 |

> **Confusion Matrix (Logistic Regression):** TP = 27 · TN = 10 · FP = 2 · FN = 10

### SimpleNN — 5-Fold Cross-Validation Summary

| Metric | Mean ± Std |
|:---|:---:|
| Accuracy | 49.96% ± 6.67% |
| Precision | 72.03% ± 3.46% |
| Recall | 54.54% ± 8.63% |
| Specificity | 35.71% ± 9.04% |
| F1 Score | 61.85% ± 6.57% |
| MCC | −0.084 ± 0.104 |
| AUC-ROC | 0.457 ± 0.154 |

### Key Takeaways

- **Logistic Regression** is the strongest model here — **93.1% precision** and **0.93 AUC-ROC** demonstrate strong discriminative ability with very few false positives (only 2 out of 49 test samples).
- **Majority-Class** baseline exposes the class imbalance problem: 75.5% accuracy by always predicting Parkinson's, but **zero specificity** and **zero MCC** — it cannot identify a single healthy patient.
- **SimpleNN** (hand-rolled, no `nn.Module`) underperforms both baselines on this small dataset (n = 195), which is expected — a from-scratch neural network without regularisation, batch normalisation, or hyperparameter tuning struggles with limited data. This model was built as a **learning exercise** in backpropagation mechanics, not as a production classifier.
- Fixing the **data leakage** in preprocessing was the most impactful methodological improvement — it ensures all reported metrics reflect genuine out-of-sample performance.

---

## Input Features

| Feature | Description |
|---|---|
| `MDVP:Fo(Hz)` | Average vocal fundamental frequency |
| `MDVP:Flo(Hz)` | Minimum vocal fundamental frequency |
| `MDVP:RAP` | Relative amplitude perturbation |
| `spread1` | Nonlinear measure of frequency variation |
| `spread2` | Nonlinear measure of frequency variation |
| `D2` | Correlation dimension (dynamical complexity) |
| `PPE` | Pitch period entropy |

These 7 features were selected from the full [UCI Parkinson's dataset](https://archive.ics.uci.edu/ml/datasets/parkinsons) during feature engineering.

---

## Dataset

[UCI Parkinson's Disease Dataset](https://archive.ics.uci.edu/ml/datasets/parkinsons) — 195 voice recordings, 23 features, binary label (`status`: 1 = Parkinson's, 0 = healthy).

---

## Tech Stack

- **PyTorch** — tensor ops, autograd
- **scikit-learn** — StandardScaler, train/test split
- **FastAPI + Uvicorn** — REST API
- **Jupyter** — feature engineering & training notebooks

---

> **Disclaimer:** This is an academic project. Not intended for clinical use.
