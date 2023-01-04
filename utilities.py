from firebase_admin import firestore
import jwt
import math, random

def getShopKey(shopName: str):
    fs: firestore.firestore.Client = firestore.client()
    data = fs.collection('ShopList').document(shopName).get()._data
    key = data['key']
    return key


def createJWT(alg: str, iss: str, sub: str, aud: str,
              iat: str, exp: str, uid: str):
    encoded_jwt = jwt.encode({
        "alg": alg,
        "iss": iss,
        "sub": sub,
        "aud": aud,
        "iat": iat,
        "exp": exp,
        "uid": uid
    })
    return encoded_jwt

def generateOTP() :
     
    # Declare a digits variable 
    # which stores all digits
    digits = "0123456789"
    OTP = ""
 
   # length of password can be changed
   # by changing value in range
    for i in range(4) :
        OTP += digits[math.floor(random.random() * 10)]
 
    return OTP
