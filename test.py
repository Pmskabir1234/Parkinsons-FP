import json
import torch
import pickle
import numpy as np

with open('model/important_features.json', 'r') as f:
    features = json.load(f)

with open('model/scaler.pkl', 'rb') as f:
    scale = pickle.load(f)

print(f'Features: {features}\n')


sample_data = {
    'MDVP:Fo(Hz)': 145.32,   # Fundamental frequency in Hz
    'MDVP:Flo(Hz)': 72.45,   # Minimum fundamental frequency in Hz
    'MDVP:RAP': 0.0047,      # Relative amplitude perturbation
    'spread1': -4.12,        # Nonlinear measure of variation
    'spread2': 2.35,         # Another spread measure
    'D2': 2.98,              # Dynamical complexity measure
    'PPE': 0.214             # Pitch period entropy
}
values = [sample_data[feat] for feat in features]

print(f"Values: {values}\n")
to_scale = np.array(values).reshape(1,7)

scaled_input = scale.transform(to_scale)
print(f'Scaled : {scaled_input}\n')
print(f'Scale Mean: {scale.mean_}\n')
print(f'Scale Scale: {scale.scale_}\n')
# ts = torch.tensor(scaled_input, dtype=torch.float64)
# print(ts)


# def input_data_cehck(data_dict):
#     try:
#         values = [data_dict[feat] for feat in features]
        
#     except KeyError as e:
#         raise ValueError(f"Missing feature: {e}")
    
#     to_scale = np.array(values).reshape(1,7)
#     scaled_input = scale.transform(to_scale)
#     return torch.tensor(scaled_input, dtype=torch.float64)
    
    
    

# x = input_data_cehck(sample_data)
# print(x)