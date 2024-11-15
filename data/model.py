# define a clas for the models to use 

class Model: 
    default_x_cols = ['singaporean', 'race_chinese', 'race_malay', 'race_others', 'female', 'dist', 'IPSICU_match'] 
	
    default_y_col = 'rating' 

    def __init__(self, save_path=None): 
        self.trained = (save_path is not None) 

    def train(self, df, x_cols = None, y_col = None, seed=None): 
        self.trained = True 

    def predict(self, x): 
        # returns a numpy array of them 
        pass 
    
    def save(self, save_path): 
        pass 


