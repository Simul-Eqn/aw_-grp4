import torch
from torch_model import TorchModel 

import pandas as pd 

# load model 
model = TorchModel() 
model.load_state_dict(torch.load('path'))
model.eval() 

x_cols = ['singaporean', 'race_chinese', 'race_malay', 'race_others', 'female', 'dist', 'IPSICU_match'] 

def get_model_score(nursedf:pd.DataFrame): 
    return model(nursedf[x_cols].values) 

def get_score(nursedf, required_skill, required_specialization): # these are dictionaries  

    model_score = get_model_score(nursedf) 

    nurse = nursedf.to_dict() # assumes only has 1 nurse 
 
    #make an experience_score 
    experience_score = 0 
    for k, v in nurse.items(): 
    # Check if the key is related to a specialization (starts with 'special_') 
        if k.startswith('experience_'): 
        # If the value is 1 (nurse has the specialization), increment experience score 
            if v == 1: 
                if required_skill in k: 
                    experience_score += 1 
     
    experience_score = experience_score*2 
 
 
    specialization_score = 0 
    for k, v in nurse.items(): 
        if k.startswith('special_'): 
            if required_specialization in k: 
                specialization_score += v 
    specialization_score = specialization_score*1.5 
 
 
    return experience_score + specialization_score + model_score 




