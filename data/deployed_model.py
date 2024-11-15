default_model_path = './torchmodels/saved2_torchmodel_epoch500.pt'

import torch
from torch_model import TorchModel 

import pandas as pd 
import numpy as np 

device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu') 

# load model 
model = TorchModel() 

def load_model(model_path): 
    global model 
    model.load_state_dict(torch.load(model_path))
    model.eval() 

x_cols = ['singaporean', 'race_chinese', 'race_malay', 'race_others', 'female', 'dist', 'IPSICU_match'] 

def get_model_score(nursedf:pd.DataFrame): 
    return model(torch.tensor(nursedf[x_cols].values, dtype=torch.float32, device=device)).item() 

def get_score(nursedf, required_skill, required_specialization): # these are dictionaries  

    model_score = get_model_score(nursedf) 

    nurse = nursedf.loc[0].to_dict() # assumes only has 1 nurse 
    print("NURSE DICT") 
    print(nurse) 
 
    #make an experience_score 
    experience_score = 0 
    for k, v in nurse.items(): 
    # Check if the key is related to a skill (starts with 'experience_') 
        if k.startswith('experience_'): 
        # If the value is 1 (nurse has the skill), increment experience score 
            if abs(v - 1.0) < 1e-7: 
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






load_model(default_model_path) 


# flask 
from flask import Flask, request, Response 

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def main():
    return "HIIII" 

@app.route('/loadmodel', methods=['GET'])
def flask_load_model(): 
    modelname = request.args.get('modelname')
    load_model(modelname) 
    return Response("finished loading", 200) 


fields = ['name', 'singaporean', 'race_chinese', 'race_malay', 'race_others',
       'female', 'experience_nurshingHome', 'experience_emergencyClinic',
       'experience_ICU', 'experience_nursery', 'experience_dayWard',
       'special_Podiatrist', 'special_Psychology', 'special_Eye',
       'special_Critical care nurse', 'special_Paediatrics',
       'special_Occupational therapist', 'special_Dietitian',
       'special_Physiotherapist', 'special_Diagnostic Radiographer', 'dist',
       'IPSICU_match', 'rating', 'comments', 'recommend'] 
field_dtypes = ["np.dtype('O')", "np.dtype('int32')", "np.dtype('int32')", "np.dtype('int32')", "np.dtype('int32')", "np.dtype('int32')", "np.dtype('float64')", "np.dtype('float64')", "np.dtype('float64')", "np.dtype('float64')", "np.dtype('float64')", "np.dtype('float64')", "np.dtype('float64')", "np.dtype('float64')", "np.dtype('float64')", "np.dtype('float64')", "np.dtype('float64')", "np.dtype('float64')", "np.dtype('float64')", "np.dtype('float64')", "np.dtype('float64')", "np.dtype('int32')", "np.dtype('float64')", "np.dtype('O')", "np.dtype('float64')"] 

@app.route('/getscore', methods=['GET'])
def flask_get_score(): 
    nurse_data = {} 
    for fidx in range(len(fields)): 
        field = fields[fidx] 
        nurse_data[field] = np.array(request.args.get(field), dtype=eval(field_dtypes[fidx])) 
    nurse_df = pd.DataFrame(nurse_data, index=[0]) 
    
    required_skill = request.args.get('requiredSkill') 
    required_specialization = request.args.get('requiredSpecialization') 

    print(nurse_df) 

    return Response(str(get_score(nurse_df, required_skill, required_specialization)), 200)

