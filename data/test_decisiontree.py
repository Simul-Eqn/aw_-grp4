import pandas as pd
from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
import numpy as np
import pickle 

#import matplotlib.pyplot as plt

from model import Model 
from dataloader import load_data 


class DecisionTree(Model): 
    def __init__(self, save_path='dtree.pkl'): 
        if save_path is not None: 
            # load trained model 
            self.trained = True
			
            try: 
                with open(save_path, 'rb') as f: 
                    self.dtree = pickle.load(f) 
                return # done initializing 
            except Exception as e: 
                print("UNABLE TO LOAD MODEL FROM {}, MAKING NEW MODEL".format(save_path)) 
        
        self.dtree = DecisionTreeClassifier() 
        self.trained = False 
        

    def train(self, df=load_data(), x_cols = None, y_col = None, seed=None): 

        if seed is not None: # set seed 
            seed = 10 
        np.random.seed(seed) # set seed for sklearn 

        if self.trained: 
            print("WARNING: self.trained is already True, still trying to re-train model!") 

        if x_cols is None: 
            x_cols = Model.default_x_cols 
		
        if y_col is None: 
            y_col = Model.default_y_col 

        self.dtree = self.dtree.fit(df[x_cols], df[y_col])

        self.trained = True 

    
    def predict(self, x): 
        res = self.dtree.predict(x) 
        return res 


    def save(self, save_path:str='dtree.pkl'): 
        if not self.trained: 
            print("WARNING: self.trained is False, still saving model ")

		# save
        with open(save_path,'wb') as f:
            pickle.dump(self.dtree, f)



if __name__=='__main__': 
    import matplotlib.pyplot as plt 

    dt = DecisionTree(None) 

    dt.train() 


    from datagen import data_generator 
    gen = data_generator(return_dict=False) 

    for _ in range(10): 
        d = next(gen) 
        res = dt.predict(np.array(d).reshape(1,7)) # will give a warning as we didn't put a name but we can silence it 
        print(res) 



    tree.plot_tree(dt.dtree, feature_names=Model.default_x_cols)

    plt.show() 