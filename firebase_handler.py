# the admin can create accounts 
import firebase_admin
from firebase_admin import credentials, db
from firebase_admin import auth 

# clients like pyrebase can login to them 
import pyrebase 


# use key to authenticate / connect to firebase with admin SDK 
cred = credentials.Certificate("./firebase_key.json")
firebase_admin.initialize_app(cred)

# connect to pyrebase 
with open('./apikey.txt', 'r') as apikey_file: 
    apikey = apikey_file.readline().strip() 

config = {
  "apiKey": apikey, 
  "authDomain": "fir-demo-70178.firebaseapp.com",
  "storageBucket": "fir-demo-70178.firebasestorage.app",
  #projectId: "fir-demo-70178",
  #messagingSenderId: "101649240617",
  #appId: "1:101649240617:web:82b125f00c34116b2cc238",
  #measurementId: "G-7V42SYHQ4W",
  "databaseURL": "https://databaseName.firebaseio.com", # dummy value as we aren't using realtime database so we don't need 
  "serviceAccount": "./firebase_key.json", 
}

firebase = pyrebase.initialize_app(config)
pyrebase_auth = firebase.auth() 



# auth functions (using firebase to do login/logout) 
def signup_email_password(email, password):
    # returns Exception OR UserRecord 
    # if Exception: error message for signup 
    # if UserRecord: successful signup 
    try:
        user = auth.create_user(email=email, password=password) 
        return user 
    except Exception as e:
        return e 


def login_email_password(email, password):
   # returns Exception OR User 
    # if Exception: error message for login 
    # if User: successful login 
    try:
        user = pyrebase_auth.sign_in_with_email_and_password(email, password)
        return user 
    except Exception as e:
        return e 




# TODO allow login with google 


