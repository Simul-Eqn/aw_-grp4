default_model_path = './torchmodels/saved2_torchmodel_epoch500.pt'

import torch
from torch_model import TorchModel 

import word2vec 
from dataloader import experience_possibilities, experience_names, get_job_df, constituencies, constituency_to_dist 

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
                #print("EXPERIENCE HAVE: {}".format(k)) 
                #print("REQUIRED SKILL: {}".format(required_skill))
                if required_skill[-3:] == k[-3:]: # enough for our purposes for coparison 
                    experience_score += 1 
     
    experience_score = experience_score*1.3 
 
 
    specialization_score = 0 
    for k, v in nurse.items(): 
        if k.startswith('special_'): 
            if required_specialization in k: 
                #print("SPECIALIZATION REQUIRED:", required_specialization) 
                #print("SCORE:", v)
                specialization_score += v 
    specialization_score = specialization_score*1.5 - 0.5 
 
 
    return (experience_score*3/5 + specialization_score + model_score) 


def info_to_nursedf(name:str, singaporean:bool, race:str, female:bool, experience:str, 
                 speciality:str, constituency:str, preferred_ICU:bool, assigned_ICU:bool, to_dict:bool=True): 

    # cleaned 
    data = {} 

    # name 
    data['name'] = name.strip() 

    # citizenship 
    data['singaporean'] = int(singaporean) 

    # race 
    # let's use one-hot encoding 
    data['race_chinese'] = int(race=='Chinese') 
    data['race_malay'] = int(race=='Malay') 
    data['race_others'] = 1 - data['race_chinese'] - data['race_malay'] 

    # gender - let 1 be female, 0 be male 
    data['female'] = int(female) 

    # experience... 
    # assume all possible values of experience are in experience_possibilities 
    # we should one-hot encode this 
    for epidx in range(len(experience_possibilities)): 
        data['experience_{}'.format(experience_names[epidx])] = int(experience==experience_possibilities[epidx]) 

    # specialization........ 
    job_df = get_job_df() 

    for nidx in range(len(job_df['name'])): 
        data['special_{}'.format(job_df.loc[nidx, 'name'])] = word2vec.filter_and_get_similarity(speciality, job_df.loc[nidx, 'name']) 
    # NOTE: if we do MLRM or smtg, based on the job to be matched with, we'll only use one of these. 


    # singapore constituency 
    # approximate distance to Farrer Park Hospital, with ChatGPT (not completely reliable but we did a quick check and it makes some sense)
    #constituencies = _get_constituencies() 
    data['dist'] = constituency_to_dist(constituency) # distance to Farrer Park Hospital 



    # this fields shld probably be dealt with outside the model 
    # available work days raw_df['Available work days'].value_counts() 
    # ughhh let's just check for mon/tues/wed/thurs/fri/sat/sun 
    # TODO 


    # this field, when considered by model, shld just be a bool of whether or not it will still fulfil 
    # frequency of work raw_df['Frequency of work'].value_counts() 
    # let's read it in as a number, how many times a week 
    # TODO 


    # this field, when considered by model, shld just be a bool of whether work timing prefernece is met 
    # available work timing preference 
    # it's just prefer morning shift or evening shift (830pm-730am) or no preference i think 
    # TODO 


    # preference for Inpatient Ward / ICU 
    # IPS/ICU 
    # let's make it a bool, true if ICU 
    data_ICU = preferred_ICU 

    # assigned department 
    # either IPS or an ICU...
    data_assigned_ICU = assigned_ICU 


    # IN THE MODEL, IT SHLD JUST BE A BOOL OF WHETHER IT IS CORRECT ASSIGNED DEPARTMENT OR NOT 
    data['IPSICU_match'] = int(preferred_ICU == assigned_ICU) 

    if to_dict: 
        return data 

    return pd.DataFrame(data) 





load_model(default_model_path) 


# flask 
from flask import Flask, request, Response, redirect, url_for, render_template 

app = Flask(__name__)


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

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST': 
        name = request.form['name'] 
        singaporean = (request.form['citizenship']=='Singaporean') 
        race = request.form['race'] 
        female = (request.form['gender']=='Female') 
        experience = request.form['experience'] 
        specialty = request.form['specialty'] 
        constituency = request.form['constituency'] 
        preferred_ICU = (request.form["preferred_ICU"]=='ICU') 
        assigned_ICU = (request.form["assigned_ICU"]=='ICU') 
        nurse_dict = info_to_nursedf(name, singaporean, race, female, experience, specialty, 
                                   constituency, preferred_ICU, assigned_ICU, True)
        
        required_skill = request.form['required_skill'] 
        required_specialization = request.form['required_specialization'] 
        nurse_dict['requiredSkill'] = required_skill 
        nurse_dict['requiredSpecialization'] = required_specialization 
        
        return redirect(url_for('flask_get_score', **nurse_dict)) 
    return render_template('form.html')

if __name__=='__main__': 
    app.run(host='0.0.0.0', port=5000, debug=True)
