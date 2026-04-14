import torch

class SimpleNN():
    def __init__(self, input_shape):
        self.weights1 = torch.rand(input_shape, 6, requires_grad = True, dtype = torch.float64)
        self.bias1 = torch.zeros(6, requires_grad = True, dtype = torch.float64)
        self.weights2 = torch.rand(6, 4, requires_grad = True, dtype = torch.float64)
        self.bias2 = torch.zeros(4, requires_grad = True, dtype = torch.float64)
        self.weights3 = torch.rand(4, 1, requires_grad = True, dtype = torch.float64)
        self.bias3 = torch.zeros(1, requires_grad = True, dtype = torch.float64)

    def forward(self, X):
        z1 = torch.matmul(X, self.weights1) + self.bias1
        a1 = torch.relu(z1)
        
        z2 = torch.matmul(a1, self.weights2) + self.bias2
        a2 = torch.relu(z2)

        z3 = torch.matmul(a2, self.weights3) + self.bias3
        y_pred = torch.sigmoid(z3)

        return y_pred

    def loss_func(self, y_pred, y):
        epsilon = 1e-7
        y_pred = torch.clamp(y_pred, epsilon, 1-epsilon)
        # Corrected binary cross-entropy loss
        loss = -(y * torch.log(y_pred) + (1 - y) * torch.log(1 - y_pred)).mean()
        return loss