from dataloader import load_data 

from sklearn.linear_model import LinearRegression 
import pickle 




class MLRM(): 
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
            
	def train(self, df=load_data(), train_cols = ['name', 'singaporean', 'race_chinese', 'race_malay', 'race_others',
       'female', 'dist', 'IPSICU_match'], test_col = 'rating'): 

		if self.trained: 
			print("WARNING: self.trained is already True, still trying to re-train model!") 

		x = df[train_cols] 
		y = df[test_col] 


		self.lm.fit(x, y) 

		self.trained = True 

	def predict(self, x): 
		return self.lm.predict(x) 

	def save(self, save_path:str='mlrm.pkl'): 
		
		if not self.trained: 
			print("WARNING: self.trained is False, still saving model ")

		# save
		with open(save_path,'wb') as f:
			pickle.dump(self.lm, f)


