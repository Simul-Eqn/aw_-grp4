import pandas as pd
import csv
from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
import matplotlib.pyplot as plt
import sys
import numpy as np

df = pd.read_csv("cleaned_nursedf2.csv")

d={'1':1,'0':0}

df['IPSICU_match']=df['IPSICU_match'].map(d)

df['singaporean']=df['singaporean'].map(d)

df['female']=df['female'].map(d)

vec_discretize_rating = np.vectorize(lambda x: int(x>2))
df['rating'] = vec_discretize_rating(df['rating'])

discretize_distance=np.vectorize(lambda x:int(x<8)) #max dist 14, take less than medium
df['dist'] = discretize_distance(df['dist'])

#train_cols = ['name', 'singaporean', 'race_chinese', 'race_malay', 'race_others',
#            'female', 'dist', 'ICU', 'IPSICU_match']
train_cols = ['singaporean','female','IPSICU_match','rating','dist']

X=df[train_cols]
y=df['recommend']


dtree = DecisionTreeClassifier()
dtree = dtree.fit(X, y)

tree.plot_tree(dtree, feature_names=train_cols)

plt.savefig(sys.stdout.buffer)
sys.stdout.flush()
