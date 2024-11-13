from bs4 import BeautifulSoup 
import requests 
import pandas as pd 

# categorical variable: constituency 
# get constituencies 
def _get_constituencies(): 
    url = 'https://en.wikipedia.org/wiki/Constituencies_of_Singapore'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', {'class': 'wikitable'})

    # get table headers and rows 
    headers = [header.text.strip() for header in table.fine_all('th')]
    # Extract table rows
    rows = []
    for row in table.find_all('tr')[1:]:  # Skipping the header row
        cells = [cell.text.strip() for cell in row.find_all(['td', 'th'])]
        rows.append(cells) 

    # df 
    df = pd.DataFrame(rows, columns=headers)
    
    return [c.lower() for c in df['Constituency'].values.tolist()  ]

def _postalcode_to_constituency(postalcode): # utility function? 
    # https://www.parliament.gov.sg/mps/find-mps-in-my-constituency 
    return 


class Dataloader(): 

    constituencies = _get_constituencies() 

    @classmethod 
    def get_constituency_idx(cls, constituency:str): 
        return Dataloader.constituencies.index(constituency.lower().strip()) 
    
    @classmethod 
    def get_constituency_from_idx(cls, idx:int): 
        return Dataloader.constituencies[idx] 
    





