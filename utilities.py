from firebase_admin import firestore, messaging
import jwt
import math
import random
import json
from cryptography.fernet import Fernet
import uuid

with open('secret.json') as json_file:
    data = json.load(json_file)
    salt = data['salt']
    jwt_key = data['jwt_key']


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
    }, key=jwt_key)
    return encoded_jwt


def generateOTP():

    # Declare a digits variable
    # which stores all digits
    digits = "0123456789"
    OTP = ""

   # length of password can be changed
   # by changing value in range
    for i in range(4):
        OTP += digits[math.floor(random.random() * 10)]

    return OTP


def encodeShopName(shopName: str):
    encoded = list(shopName.encode('utf-8'))
    return encoded.__str__().replace('[', '__listformat1__').replace(']', '__listformat2__').replace(', ', '__listformat3__')


def decodeShopName(encodedShopName: str):
    bytesDataStr = encodedShopName.replace(
        '__listformat1__', '[').replace('__listformat2__', ']').replace('__listformat3__', ', ').strip('][').split(', ')
    bytesDataInt = list(map(int, bytesDataStr))
    bytesData = bytes(bytesDataInt)
    return bytes.decode(bytesData)


def sendMessagesToTopics(notification: dict, data: dict, topic: str):
    noti = messaging.Notification(
        title=notification['title'], body=notification['body'])
    message = messaging.Message(
        notification=noti, data=data, topic=topic)
    response = messaging.send(message=message)
    return response


''' def genShopKey(shopName: str):
    uid: str = str(uuid.uuid5(namespace=uuid.uuid4(), name=shopName))
    shopKey, fernet_key = encrypt(uid)
    with open('secret.json') as json_file:
        data = json.load(json_file)
        data[f'{shopName}-fernet_key'] = str(fernet_key)
        json_object = json.dumps(data)
        with open('secret.json', 'w') as outfile:
            outfile.write(json_object)
    return shopKey


def encrypt(message: str):
    key = Fernet.generate_key()
    fernet = Fernet(key)
    encMessage = fernet.encrypt(message.encode())
    return encMessage, key


def decrypt(encMessage: str, fernet: Fernet):
    message = fernet.decrypt(encMessage).decode()
    return message '''
