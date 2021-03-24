import firebase_admin
from firebase_admin import firestore,auth,storage, credentials
import flask
from flask import abort,jsonify,request,redirect
import json
import requests


app = flask.Flask(__name__)

cred = credentials.Certificate("tinder-api-207c9-firebase-adminsdk-tovxm-930da536e7.json")
firebase_admin.initialize_app(cred)

store = firestore.client()

@app.route('/login',methods=['POST'])
def login():
    data = request.get_json(force= True)
    userEmail = data.get("email")
    uid=""
    message=""
    try:
        user1 = auth.get_user_by_email(userEmail)
        message='Successfully logged in !!'
        uid=user1.uid
    except:
        message='User already exists in firebase'
    
    return {"uid":uid,"message":message,"Response":200}

@app.route('/signup',methods=['POST'])
def signup():
    data = request.get_json(force= True)
    uid=""
    userEmail = data.get("email")
    userPassword = data.get("password")

    try:
        user = auth.create_user(
        email=userEmail,
        email_verified=False,
        password=userPassword)
        message='Successfully created new user'
        uid=user.uid
    except:
        message='User already exists'

    return {"uid":uid,"message":message,"Response":200}


@app.route('/updateUser',methods=['POST'])
def updateUser():
    dit = request.get_json(force= True)
    # uid=""

    uid =dit['uid']
    dit_user_details={}
    dit_user_details["name"]=dit.get("name")
    dit_user_details["number"]=dit.get("number")
    dit_user_details["image"]=dit.get("image")
    dit_user_details["desp"]=dit.get("desp")
    dit_user_details["dob"]=dit.get("dob")
    dit_user_details["gender"]=dit.get("gender")
    dit_user_details["passion"]=dit.get("passion")
    dit_user_details["job"]=dit.get("job")
    dit_user_details["location"]=dit.get("location")
    dit_user_details['email']=dit.get('email')
    dit_user_details['createdAt']= firestore.SERVER_TIMESTAMP

    store.collection("users").document(uid).set(dit_user_details)
    
    message="User data updated !!"

    return {"uid":uid,"message":message,"Response":200}

@app.route('/getFeed',methods=['POST'])
def getFeed():
    data = request.get_json(force= True)
    uid=""
    
    docs = store.collection("users").where("gender","==",data.get("gender")).stream()

    dit={}
    for i in docs:
        if i.to_dict().get('location').get('country')==data.get("country"):
            dit[i.id]= i.to_dict()
    
    return {"dit":dit,"Response":200}


@app.route('/swipeFun',methods=['POST'])
def swipeFun():
    data = request.get_json(force= True)
    uid=""
    dit={}
    dit["UID_A"]=data.get("uid_A")
    dit["UID_B"]=data.get("uid_B")
    dit["isUserA_Yes"]= data.get("isA_Yes")
    dit["isUserB_Yes"]= data.get("isB_Yes")
    dit['profileSeenByOther']= data.get("firstTime")
    dit['createdAt']=firestore.SERVER_TIMESTAMP

    store.collection('swipes').add(dit)

    return {"dit":dit,"Response":200}


@app.route('/getMatch',methods=['POST'])
def getMatch():
    data = request.get_json(force= True)
    uid=""
    docs=  store.collection('swipes').stream()
    ditSwipes={}

    for doc in docs:
        if (doc.to_dict().get('UID_A')==data.get('uid_A') or doc.to_dict().get('UID_B')==data.get('uid_B')) and (doc.to_dict().get("isUserA_Yes")==True and doc.to_dict().get("isUserB_Yes")==True ):
            ditSwipes[doc.id]=doc.to_dict()

    return {"dit":ditSwipes,"Response":200}


if __name__=='__main__':
    app.run(host='127.0.0.1', port=5001, debug= False)


