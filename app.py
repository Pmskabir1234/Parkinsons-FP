import json
import pickle
import torch
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from model import SimpleNN
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI(title="Parkinson's Disorder Prediction API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


_REQUIRED_CHECKPOINT_KEYS = {"input_size", "W1", "b1", "W2", "b2", "W3", "b3"}

try:
    checkpoint = torch.load("model/model.pth", map_location="cpu", weights_only=True)
except FileNotFoundError:
    raise RuntimeError(
        "model/model.pth not found. Run the training notebook first to generate the model file."
    )
except Exception as exc:
    raise RuntimeError(f"Failed to load model checkpoint: {exc}") from exc


missing_keys = _REQUIRED_CHECKPOINT_KEYS - checkpoint.keys()
if missing_keys:
    raise RuntimeError(
        f"Checkpoint is missing required keys: {missing_keys}. "
        "Re-run the training notebook to regenerate the model file."
    )

model = SimpleNN(checkpoint["input_size"])
model.weights1 = checkpoint["W1"]
model.weights2 = checkpoint["W2"]
model.weights3 = checkpoint["W3"]
model.bias1 = checkpoint["b1"]
model.bias2 = checkpoint["b2"]
model.bias3 = checkpoint["b3"]

try:
    with open("model/important_features.json", "r") as f:
        features = json.load(f)
except FileNotFoundError:
    raise RuntimeError(
        "model/important_features.json not found. The file must exist alongside the model."
    )

try:
    with open("model/scaler.pkl", "rb") as f:
        scaler = pickle.load(f)
except FileNotFoundError:
    raise RuntimeError(
        "model/scaler.pkl not found. Run the training notebook first to generate the scaler file."
    )

_N_FEATURES = len(features)


def input_data_check(data_dict: dict) -> torch.Tensor:
    """Extract, validate, scale, and tensorise an input feature dictionary.

    Raises ValueError with a descriptive message on any bad input.
    """
    # every required feature must appear
    try:
        values = [data_dict[feat] for feat in features]
    except KeyError as e:
        raise ValueError(f"Missing feature: {e}")

    # Fix #5 — type and finite-value validation; reject non-numeric / NaN / inf
    for feat, val in zip(features, values):
        if not isinstance(val, (int, float)):
            raise ValueError(
                f"Feature '{feat}' must be a numeric value; got {type(val).__name__!r}."
            )
        if not np.isfinite(val):
            raise ValueError(
                f"Feature '{feat}' contains a non-finite value ({val!r})."
            )


    arr = np.array(values, dtype=np.float64).reshape(1, _N_FEATURES)
    scaled = scaler.transform(arr)
    # Use torch.tensor() — avoids the NumPy 2.x ABI incompatibility with
    # torch.from_numpy() on this environment.
    return torch.tensor(np.ascontiguousarray(scaled), dtype=torch.float64)



# Request schema
class InputData(BaseModel):
    data: dict


# Routes
@app.get("/health")
def health():
    return {"status": "ok", "n_features": _N_FEATURES}


@app.post("/predict")
def predict(input: InputData):
    try:
        x = input_data_check(input.data)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    with torch.no_grad():
        y_prob = model(x)

    probability = float(y_prob.item())
    label = "Parkinson's Detected" if probability > 0.5 else "Healthy"

    return {
        "probability": probability,
        "label": label,
    }
