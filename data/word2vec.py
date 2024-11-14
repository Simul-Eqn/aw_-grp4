

print("Importing modules... ") 
import pandas as pd 
pd.options.mode.chained_assignment = None
import numpy as np
import nltk
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('omw-1.4')
nltk.download('wordnet')
#import gensim
#from gensim.models import Word2Vec
from gensim.models import KeyedVectors 
#from sklearn.manifold import TSNE
#from sklearn.feature_extraction.text import TfidfVectorizer # if we're using word vectorization ig 
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
#from nltk.corpus import stopwords
stopwords = ['a', 'about', 'above', 'across', 'after', 'again', 'against', 'all', 'almost', 'alone', 'along', 'already', 'also', 'although', 'always', 'am', 'among', 'an', 'and', 'another', 'any', 'anybody', 'anyone', 'anything', 'anywhere', 'are', 'area', 'areas', 'around', 'as', 'ask', 'asked', 'asking', 'asks', 'at', 'away', 'b', 'back', 'backed', 'backing', 'backs', 'be', 'became', 'because', 'become', 'becomes', 'been', 'before', 'began', 'behind', 'being', 'beings', 'best', 'better', 'between', 'big', 'both', 'but', 'by', 'c', 'came', 'can', 'cannot', 'case', 'cases', 'certain', 'certainly', 'clear', 'clearly', 'come', 'could', 'd', 'did', 'differ', 'different', 'differently', 'do', 'does', 'done', 'down', 'downed', 'downing', 'downs', 'during', 'e', 'each', 'early', 'either', 'end', 'ended', 'ending', 'ends', 'enough', 'even', 'evenly', 'ever', 'every', 'everybody', 'everyone', 'everything', 'everywhere', 'f', 'face', 'faces', 'fact', 'facts', 'far', 'felt', 'few', 'find', 'finds', 'first', 'for', 'four', 'from', 'full', 'fully', 'further', 'furthered', 'furthering', 'furthers', 'g', 'gave', 'general', 'generally', 'get', 'gets', 'give', 'given', 'gives', 'go', 'going', 'good', 'goods', 'got', 'great', 'greater', 'greatest', 'group', 'grouped', 'grouping', 'groups', 'h', 'had', 'has', 'have', 'having', 'he', 'her', 'here', 'herself', 'high', 'high', 'high', 'higher', 'highest', 'him', 'himself', 'his', 'how', 'however', 'i', 'if', 'important', 'in', 'interest', 'interested', 'interesting', 'interests', 'into', 'is', 'it', 'its', 'itself', 'j', 'just', 'k', 'keep', 'keeps', 'kind', 'knew', 'know', 'known', 'knows', 'l', 'large', 'largely', 'last', 'later', 'latest', 'least', 'less', 'let', 'lets', 'like', 'likely', 'long', 'longer', 'longest', 'm', 'made', 'make', 'making', 'man', 'many', 'may', 'me', 'member', 'members', 'men', 'might', 'more', 'most', 'mostly', 'mr', 'mrs', 'much', 'must', 'my', 'myself', 'n', 'necessary', 'need', 'needed', 'needing', 'needs', 'never', 'new', 'new', 'newer', 'newest', 'next', 'no', 'nobody', 'non', 'noone', 'not', 'nothing', 'now', 'nowhere', 'number', 'numbers', 'o', 'of', 'off', 'often', 'old', 'older', 'oldest', 'on', 'once', 'one', 'only', 'open', 'opened', 'opening', 'opens', 'or', 'order', 'ordered', 'ordering', 'orders', 'other', 'others', 'our', 'out', 'over', 'p', 'part', 'parted', 'parting', 'parts', 'per', 'perhaps', 'place', 'places', 'point', 'pointed', 'pointing', 'points', 'possible', 'present', 'presented', 'presenting', 'presents', 'problem', 'problems', 'put', 'puts', 'q', 'quite', 'r', 'rather', 'really', 'right', 'right', 'room', 'rooms', 's', 'said', 'same', 'saw', 'say', 'says', 'second', 'seconds', 'see', 'seem', 'seemed', 'seeming', 'seems', 'sees', 'several', 'shall', 'she', 'should', 'show', 'showed', 'showing', 'shows', 'side', 'sides', 'since', 'small', 'smaller', 'smallest', 'so', 'some', 'somebody', 'someone', 'something', 'somewhere', 'state', 'states', 'still', 'such', 'sure', 't', 'take', 'taken', 'than', 'that', 'the', 'their', 'them', 'then', 'there', 'therefore', 'these', 'they', 'thing', 'things', 'think', 'thinks', 'this', 'those', 'though', 'thought', 'thoughts', 'three', 'through', 'thus', 'to', 'today', 'together', 'too', 'took', 'toward', 'turn', 'turned', 'turning', 'turns']
# since nltk's stopwords are a bit limiting 

#First AI: Naive Bayes Classifer --------------------------------------------------------------

print("LOADING FIRST AI - Naive Bayes Classifier")

#loading stuff

#initialize lemmatizer
print("Initializing lemmatizer and related functions... ") 
lemmatizer = WordNetLemmatizer()

#define filter text function using lemmatizer 
def filtertext(text): 
    new_tokens = [] 
    for token in word_tokenize(text): 
        new_tokens.append(lemmatizer.lemmatize(token))
    
    #assign to globally set stopwords to a local set
    stop_words = set(stopwords.words('english')+[''])
    
    #filter the stopwords and non-alphanumeric characters from the token
    filtered_tokens = [''.join(ch for ch in token if ch in letters) for token in new_tokens if not ''.join(ch for ch in token if ch in letters).lower() in stop_words]

    return filtered_tokens 


#for the lists later: no. of blanks is number of topics because yes. Each topic is assigned a certain "id". 
letters = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

#read in location data
print("Loading locations... ") 
fl = open("LocationData.csv", 'r') #will be formatted such that odd lines are location names and evens are tags 
rawLocs = fl.readlines()
fl.close()

#Load locations and corresponding tags 
locTags = {}
values = [] 
for x in range(len(rawLocs)):
    if rawLocs[x].strip() == "": continue 
    temp = rawLocs[x].split(',')
    temp2 = [] 
    for i in range(1, len(temp)):
        temp2 += filtertext(temp[i].strip()) 
    locTags[temp[0]] = temp2
    values += temp2 

#compile list of tags 
#values = locTags.values()
taglookup = []
for i in values:
    taglookup.append(i) 
taglookup = list(set(taglookup))
#print("Taglookup:", taglookup) 

#Load pre-trained Word2Vec model
print("Loading vectorizer... (This is usually the longest step)") 
vectorizer = KeyedVectors.load_word2vec_format('./data/GoogleNews-vectors-negative300.bin', binary=True)




#print(locTags)
print("Loading complete!") 

#define function to get word similarities 
def word_similarities(target_word, words): 
    words = [word for word in taglookup] 
    distances = vectorizer.distances(target_word, words) #ordered based on orders of vocabulary it seems
    return distances #(distances-np.min(distances))/(np.max(distances)-np.min(distances))



def get_similarity(words1, words2): 
    max_score = 0.0 
    for inword in words1:
        #print("checkpoint 1")
        try:
            max_score = max(max_score, max(word_similarities(inword, words2)))
        except Exception as ex:
            print(ex)
    return max_score 
# this is cosine similarity, so it's 0.0 to 1.0 


def get_most_similar(words, wordsslist): 
    # words is the phrase you're checking 
    # wordsslist is the list of phrases to check t o

    t = filtertext(words) 

    scores = [] 

    for wss in wordsslist: 
        scores.append((get_similarity(t, filtertext(wss)), wss)) 
    
    return max(scores) # (score, words)

    
