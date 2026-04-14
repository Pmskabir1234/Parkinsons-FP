import json
import pickle
import torch
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
from model import SimpleNN


app = FastAPI()


checkpoint = torch.load('model/model.pth', map_location='cpu')

model = SimpleNN(checkpoint['input_size'])

model.weights1 = checkpoint['W1']
model.weights2 = checkpoint['W2']
model.weights3 = checkpoint['W3']

model.bias1 = checkpoint['b1']
model.bias2 = checkpoint['b2']
model.bias3 = checkpoint['b3']

with open('model/important_features.json', 'r') as f:
    features = json.load(f)

with open('model/scaler.pkl', 'rb') as f:
    scale = pickle.load(f)

def input_data_check(data_dict):
        try:
            values = [data_dict[feat] for feat in features]
        
        except KeyError as e:
            raise ValueError(f"Missing feature: {e}")
    
        to_scale = np.array(values).reshape(1,7)
        scaled_input = scale.transform(to_scale)
        return torch.tensor(scaled_input, dtype=torch.float64)

class InputData(BaseModel):
    data : dict

@app.post('/predict')
def predict(input: InputData):
    x = input_data_check(input.data)

    with torch.no_grad():
        y_pred = model.forward(x)

    return {
        'prediction':float(y_pred.item())
    }