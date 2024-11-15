from dataloader import load_data 
from model import Model 

from sklearn.linear_model import LinearRegression 
import pickle 

import numpy as np 



class MLRM(Model): 
	default_x_cols = ['singaporean', 'race_chinese', 'race_malay', 'race_others', 'female', 'dist', 'IPSICU_match'] 
	
	default_y_col = 'rating' 


	def __init__(self, save_path:str=None): 
		if save_path is not None: 
			# load trained model 
			self.trained = True
			
			try: 
				with open(save_path, 'rb') as f: 
					self.lm = pickle.load(f) 
				return # done initializing 
			except Exception as e: 
				print("UNABLE TO LOAD MODEL FROM {}, MAKING NEW MODEL".format(save_path)) 

		# make model (either didn't specify save_pat or couldn't load)
		self.trained = False 

		self.lm = LinearRegression() 
            
	def train(self, df=load_data(), x_cols = None, y_col = None, seed=None): 
		if seed is not None: # set seed 
			np.random.seed(10) # set seed for sklearn 

		if self.trained: 
			print("WARNING: self.trained is already True, still trying to re-train model!") 

		if x_cols is None: 
			x_cols = MLRM.default_x_cols 
		
		if y_col is None: 
			y_col = MLRM.default_y_col 

		x = df[x_cols] 
		y = df[y_col] 


		self.lm.fit(x, y) 

		self.trained = True 

	def predict(self, x): 
		res = self.lm.predict(x) 
		# make sure it's max 5, min 0 
		res = np.where(res>0, res, 0) 
		res = np.where(res<5, res, 5) 
		return res 

	def save(self, save_path:str='mlrm.pkl'): 
		
		if not self.trained: 
			print("WARNING: self.trained is False, still saving model ")

		# save
		with open(save_path,'wb') as f:
			pickle.dump(self.lm, f)



if __name__=='__main__': 
	mlrm = MLRM('mlrm.pkl') # try loading the model 
	if not mlrm.trained: 
		print("NOT TRAINED (failed to load) - will train") 
		mlrm.train() # train 
		mlrm.save('mlrm.pkl') # save 

	out = mlrm.predict(load_data().loc[[0], MLRM.default_x_cols]) 
	print("OUTPUT:", out, "(TYPE: {})".format(str(type(out)))) 
