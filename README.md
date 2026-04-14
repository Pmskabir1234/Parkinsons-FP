# Parkinson's Disease Predictor — Neural Network from Scratch

A feedforward neural network built **from scratch with raw PyTorch tensors** (no `nn.Module`, no built-in optimizers) that predicts Parkinson's disease from voice biomarker data. Served via a FastAPI REST endpoint.

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

Interactive docs available at `http://127.0.0.1:8000/docs`.

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
