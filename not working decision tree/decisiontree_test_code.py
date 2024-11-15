import pandas as pd
import csv
from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
import matplotlib.pyplot as plt
import sys
#plt.use('Agg')
import numpy as np 

df = pd.read_csv("cleaned_nursedf2.csv")

d={'1':1,'0':0}
df['IPSICU_match']=df['IPSICU_match'].map(d)

vec_discretize_rating = np.vectorize(lambda x: int(x>2)) 

df['rating'] = vec_discretize_rating(df['rating'])
#train_cols = ['name', 'singaporean', 'race_chinese', 'race_malay', 'race_others',
#            'female', 'dist', 'ICU', 'IPSICU_match']
train_cols = ['IPSICU_match','rating']


X=df[train_cols]
y=df['recommend']


dtree = DecisionTreeClassifier()
dtree = dtree.fit(X, y)

tree.plot_tree(dtree, feature_names=train_cols)

plt.savefig(sys.stdout.buffer)
sys.stdout.flush()
