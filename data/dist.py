# this is just a code to demonstrate our choice of using normal distriction for distance 

import matplotlib.pyplot as plt 
import pandas as pd 
import numpy as np 

df = pd.read_csv('cleaned_nursedf.csv', index_col=0)
plt.boxplot(df['dist'])
plt.show() 
# if we look at the visualization, it's really quite symmerical and looks gaussian 


mean = np.mean(df['dist']) 
std = np.std(df['dist']) 

print("IT SEEMS TO FOLLOW A NORMAL DISTRIBUTION OF MEAN {} AND STD {}".format(mean, std)) 


