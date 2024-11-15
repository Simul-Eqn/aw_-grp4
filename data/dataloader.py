from bs4 import BeautifulSoup 
import requests 
import pandas as pd 
import numpy as np 

#import word2vec 

from fuzzywuzzy import process, fuzz # matching constituency 

from pathlib import Path 

file_dir = Path('.') 


# categorical variable: constituency 
# get constituencies 
def _get_constituencies(): 
    url = 'https://en.wikipedia.org/wiki/Constituencies_of_Singapore'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', {'class': 'wikitable'})

    # get table headers and rows 
    headers = [header.text.strip() for header in table.find_all('th')]
    # Extract table rows
    rows = []
    for row in table.find_all('tr')[1:]:  # Skipping the header row
        cells = [cell.text.strip() for cell in row.find_all(['td', 'th'])]
        rows.append(cells) 

    # df 
    df = pd.DataFrame(rows, columns=headers)

    # since "Wards" has multiple rows per constituency, there's some odd formatting so we have to do this 
    return [c.lower() for c in df[~df['Wards'].isna()]['Constituency'].values.tolist()] 

constituencies = _get_constituencies() 
constituency_approximate_distances = [6, 10, 4.5, 20, 13.5, 7, 1.5, 19, 9.5, 17, 7.5, 19, 17.5, 11, 14, 3.5, 11]


def constituency_to_dist(in_con): 
    con = process.extract(in_con, constituencies, scorer=fuzz.partial_ratio) 
    # con will be [(name, score), (name, score), ...] 
    # score will be in descending order - first one is highest 
    #idx = np.argmax(con) 
    #print("MATCHING '{}' WITH '{}'".format(in_con, constituencies[idx])) 
    return constituency_approximate_distances[constituencies.index(con[0][0])] 


# TODO, but NOT NECESSARY TO IMPLEMENT THOUGH 
def _postalcode_to_constituency(postalcode): # utility function? 
    # https://www.parliament.gov.sg/mps/find-mps-in-my-constituency 
    raise NotImplementedError("_postalcode_to_constituency has not yet been implemented") 



def get_job_df(): 
    # let's load job data to see the possible jobs 
    job_data = {'name':[], 'salary':[], 'experience':[], 'responsibilities':[]} 
    with open(str(file_dir / 'job_data.txt'), 'r') as fin: 
        def fingen(): 
            lines = fin.readlines() 
            for line in lines: 
                yield line 
            return 
        
        fingenn = fingen() 
        def finreadline():
            #nonlocal fingenn 
            return next(fingenn) 
        

        try: 
            while True: 
                name = finreadline().strip() 
                finreadline() # no need for location since it's all Farrer Park Hospital 
                salary = finreadline()[8:].strip() 
                experience = finreadline()[31:].strip() 
                finreadline() # key responsibilities 
                responsibilities = [finreadline()[2:].strip() for _ in range(3)] # since all have 3 responsibilities 
                
                if name == 'Orthoptist': 
                    job_data['name'].append("Eye") # it's a horrible replacement but it's in the vectorizer's vocabulary 
                else: 
                    job_data['name'].append(name) 
                job_data['salary'].append(salary) 
                job_data['experience'].append(experience) 
                job_data['responsibilities'].append(responsibilities) 
        except Exception as e: 
            print(e) 


    job_df = pd.DataFrame(job_data) 

    return job_df



vec_int = np.vectorize(lambda x: int(x)) 

experience_possibilities = ['Nursing Home / Community Treatment facility',
 'Emergency Clinic',
 'Intensive care unit',
 'Neonatal ICU / Nursery',
 'Day ward'] 
experience_names = ['nurshingHome', 'emergencyClinic', 'ICU', 'nursery', 'dayWard'] 

def load_data(save_path='cleaned_nursedf.csv'): 
    if save_path is not None: 
        # just load from it save path! 
        try: 
            return pd.read_csv(save_path) 
        except Exception as e: 
            print("ERROR CALLING load_data('{}'): {}".format(save_path, str(e))) 
            print("RE-LOADING DATA") 

    raw_df = pd.read_csv(str(file_dir / 'nursedataset.csv'), header=[1,2]) 
    
    # clean the column names to make more sense 
    raw_df.columns = pd.Series([a[0].split('-')[0] if 'Unnamed' in a[1] else a[1] for a in raw_df.columns.values]) 
    
    raw_df = raw_df.drop(0, axis=0).reset_index().drop('index', axis=1) # ignore the first row of mandatory / non-mandatory fields 

    # remove duplicate names 
    prev = '' 
    idxs = [] 
    for nidx in range(len(raw_df['Name \n (as per NRIC) '])): 
        name = raw_df.loc[nidx, 'Name \n (as per NRIC) ']
        if name == prev: continue 
        prev = name 
        idxs.append(nidx) 
    raw_df = raw_df.loc[idxs].reset_index().drop('index', axis=1) 


    global word2vec 
    if 'word2vec' not in globals(): 
        import word2vec as word2vec 


    # cleaned 
    data = {} 

    # name 
    data['name'] = raw_df['Name \n (as per NRIC) '] 

    # citizenship 
    data['singaporean'] = vec_int(raw_df['Singaporean/ Singapore PR']=='Singaporean')  

    # race 
    # let's use one-hot encoding 
    data['race_chinese'] = vec_int(raw_df['Race']=='Chinese') 
    data['race_malay'] = vec_int(raw_df['Race']=='Malay') 
    data['race_others'] = vec_int( (raw_df['Race']!='Chinese') & (raw_df['Race']=='malay') ) 

    # gender - let 1 be female, 0 be male 
    data['female'] = vec_int(raw_df['Gender']=='Female') 

    # experience... 
    # assume all possible values of experience are in experience_possibilities 
    # we should one-hot encode this 
    for epidx in range(len(experience_possibilities)): 
        data['experience_{}'.format(experience_names[epidx])] = vec_int(raw_df['Experience']==experience_possibilities[epidx]) 

    # specialization........ 
    job_df = get_job_df() 
    to_similarities = {} 
    for spec in raw_df['Specialisation'].unique(): 
        to_similarities[spec] = [word2vec.filter_and_get_similarity(spec, name) for name in job_df['name']]

    sims = np.array([ to_similarities[spec] for spec in raw_df['Specialisation'] ]) 

    for nidx in range(len(job_df['name'])): 
        data['special_{}'.format(job_df.loc[nidx, 'name'])] = sims[:, nidx] 
    # NOTE: if we do MLRM or smtg, based on the job to be matched with, we'll only use one of these. 


    # singapore constituency 
    # approximate distance to Farrer Park Hospital, with ChatGPT (not completely reliable but we did a quick check and it makes some sense)
    #constituencies = _get_constituencies() 
    dists = [] 
    for con in raw_df['Postal Code ']: 
        dists.append(constituency_to_dist(con)) 
    data['dist'] = dists # distance to Farrer Park Hospital 



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
    data_ICU = vec_int(raw_df['Inpatient Ward(IPS)/ Intensive Care (ICU)']=='ICU') 

    # assigned department 
    # either IPS or an ICU...
    data_assigned_ICU = vec_int(raw_df['Assigned Department'].str.contains('ICU')) 


    # IN THE MODEL, IT SHLD JUST BE A BOOL OF WHETHER IT IS CORRECT ASSIGNED DEPARTMENT OR NOT 
    data['IPSICU_match'] = vec_int(data_ICU == data_assigned_ICU) 


    # assigned supervisor... probably not. 

    # supervisor's rating 
    vec_float = np.vectorize(lambda x:float(x))
    data['rating'] = vec_float(raw_df['Supervisor\'s rating on Locum Perfomance\n Poor, Below Average, Average, Above Average, Excellent\n (1 ']) 

    # supervisor's comments - this is not like an int/float 
    data['comments'] = raw_df['Comments on \n Locum Perfomance'] 

    # recommend to rehire 
    data['recommend'] = vec_int(raw_df['Recommend to Rehire\n (Yes/No)'].str.lower().str.contains('yes')) 

    return pd.DataFrame(data) 
# useful fields are going to be like 
# ['name', 'singaporean', 'race_chinese', 'race_malay', 'race_others', 'female', 'experience_0', 'experience_1', 'experience_2', 'special_', 'IPSICU_match', 'rating', 'comments', 'recommend'] 


class Dataloader(): 

    constituencies = _get_constituencies() 

    @classmethod 
    def get_constituency_idx(cls, constituency:str): 
        return Dataloader.constituencies.index(constituency.lower().strip()) 
    
    @classmethod 
    def get_constituency_from_idx(cls, idx:int): 
        return Dataloader.constituencies[idx] 
    
    def __init__(self): 
        self.data = load_data() 
    
    # TODO match data loading format for sklearn or tf/pytorch, whichever we are using 


if __name__ == '__main__': 
    df = load_data(save_path=None)
    df.to_csv('cleaned_nursedf.csv')



