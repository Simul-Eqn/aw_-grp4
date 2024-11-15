import torch
import torch.nn as nn 

device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu') 

class TorchModel(nn.Module): 
    def __init__(self, in_dim=7, hidden_dim=3, out_dim=1, activation=nn.Sigmoid(), final=nn.Sigmoid(), device=device): 
        super(TorchModel, self).__init__() 
        self.l1 = nn.Linear(in_dim, hidden_dim, device=device) 
        self.l2 = nn.Linear(hidden_dim, out_dim, device=device) 
        self.activation = activation 
        self.final = final 
        self.device = device 
        # outputs are from 0 to 5 
    
    def forward(self, x): 
        x = self.l1(x) 
        x = self.activation(x) 
        x = self.l2(x) 
        x = self.final(x) 
        return x*5 # sigmoid() makes it 0-1, then *5 makes it 0-5 



