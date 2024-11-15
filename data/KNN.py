from sklearn.manifold import TSNE
from model import Model
import numpy as np
import matplotlib.pyplot as plt
from adjustText import adjust_text
from annoy import AnnoyIndex 

class KNN(Model):
    def __init__(self, df, save_path = None, features = 7, distance = "manhattan", num_trees = 5, k=5): 
        self.trained = (save_path is not None)
        self.df = df
        self.features = features
        self.distance = distance
        self.num_trees = 5
        self.model = AnnoyIndex(self.features, self.distance)
        self.k = k 

        if save_path is not None: 
			# load trained model 
            self.trained = True
            try: 
                self.model.load(save_path)
                return # done initializing 
            except Exception as e: 
                print("UNABLE TO LOAD MODEL FROM {}, MAKING NEW MODEL".format(save_path))
        self.trained = False


    # def train(self, df=load_data(), x_cols = None, y_col = None, seed=None): 

    def train(self, df=None, x_cols = None, y_col = None, seed=None): 
        if df is None: 
            df = self.df 
        selected_nurse_data = df[Model.default_x_cols] # select data used for training
        vectors = [] # will be used for visualization
        for i in range(len(selected_nurse_data)):
            self.model.add_item(i, selected_nurse_data.iloc[i].values) # add each data point
            vectors.append(selected_nurse_data.iloc[i].values)
        self.model.build(self.num_trees)
        return vectors
        

    def predict(self, x, k=None, df=None):
        if df is None:
            df = self.df
        if k is None: 
            k = self.k 
        
        nearest_k = self.model.get_nns_by_vector(x, k) # getting k nearest neighbors
        
        # getting ratings of all k nearest neighbors
        ratings = []
        for i in nearest_k:
            ratings.append(df.iloc[i][Model.default_y_col])
        return np.mean(ratings) # return mean rating of k nearest neighbors


    def visualize(self, vectors, df=None):
        if df is None:
            df = self.df
        
        # getting different colors for different ratings
        col_dict = {
            2: 'tab:blue',
            3: 'tab:green',
            4: 'tab:red',
            5: 'tab:orange'
        } 

        # make sure TSNE is trained on numpy array
        if not isinstance(vectors, np.ndarray):
            vectors_array = np.array(vectors)
        tsne = TSNE(n_components=2, random_state=42, perplexity=5)
        tsne_results = tsne.fit_transform(vectors_array)

        # initializing figure
        fig = plt.figure(figsize=(10,8))

        # adding index as the label of each data point
        texts = []
        for i in range(len(df)):
            plt.scatter(tsne_results[i,0], tsne_results[i,1], s=50, c=col_dict[int(df.loc[i, Model.default_y_col])])
            texts.append(plt.text(tsne_results[i,0], tsne_results[i,1], str(i), fontsize=7))

        adjust_text(texts) # make sure the texts do not overlap

        # settings for figure
        plt.title("t-SNE plot of vectors from Annoy Index")
        plt.xlabel("t-SNE Component 1")
        plt.ylabel("t-SNE Component 2")

        plt.show() # display the figure
    
    def save(self, save_path:str='test.ann'):
        if not self.trained:
            print("WARNING: Model is not trained")
        self.save(save_path)