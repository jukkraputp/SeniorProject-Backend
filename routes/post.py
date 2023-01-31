from datetime import datetime
from firebase_admin import db, firestore
from _firebase import storage_bucket, firebase_auth
from payload import Payload
import uuid
import logging
from fastapi import HTTPException
from utilities import generateOTP
import json


async def auth(payload: Payload.Auth):
    print(payload)
    return True


async def addOrder(payload: Payload.Order):
    print(payload)
    ref = db.reference(
        f'Order/{payload.shopKey}').child(f'order{payload.orderId}')
    dic = payload.dict()
    dic.pop('shopKey')
    dic['date'] = payload.date.isoformat()
    dic['isFinished'] = False
    if not ref.get():
        ref.set(dic)
        res = {
            'message': 'Success'
        }
    else:
        res = {
            'message': 'Error'
        }
    return res


async def finishOrder(payload: Payload.FinishOrder):
    ref = db.reference(f'Order/{payload.shopKey}/order{payload.orderId}')
    ref.update({
        'isFinished': True
    })
    return {
        'message': 'Success'
    }


async def completeOrder(payload: Payload.CompleteOrder):
    ref = db.reference(f'Order/{payload.shopKey}/order{payload.orderId}')
    data = dict(ref.get())
    data.pop('isFinished')
    data['date'] = datetime.fromisoformat(data['date'])
    print(data)

    fs: firestore.firestore.Client = firestore.client()
    try:
        fs.collection(u'History').document(payload.shopKey).collection(
            f"{data['date'].year}{data['date'].month}{data['date'].day}").document(f'order{payload.orderId}').set(data)
        ref.delete()
        return {
            'message': 'Success'
        }
    except Exception as e:
        raise e


async def updateStorage():
    storage_bucket.location = '/shop1/Food1'
    return storage_bucket.location_type


async def updateProduct(payload: Payload.UpdateProduct):
    print(payload)
    fs: firestore.firestore.Client = firestore.client()
    try:
        if payload.product.delete:
            fs.collection(u'Menu').document(
                payload.shop_key).collection(payload.type).document(payload.id).delete()
        else:
            fs.collection(u'Menu').document(
                payload.shop_key).collection(payload.type).document(payload.id).set({
                    "name": payload.product.name,
                    "price": payload.product.price
                })

    except Exception as e:
        print(e)
        return e
    return True


async def register(payload: Payload.Register):
    fs: firestore.firestore.Client = firestore.client()
    try:
        user: firebase_auth.UserRecord = firebase_auth.create_user(
            email=f'{payload.username}@gmail.com', password=payload.password)
        try:
            fs.collection(u'Manager').document(f'{user.uid}').create({
                'name': payload.username,
            })
            return True
        except Exception as e:
            print('register2::', e)
            return False
    except Exception as e:
        print('register1::', e)
        return False


async def generateToken(payload: Payload.GenerateToken):
    # print(payload)
    uid = uuid.uuid4().__str__()
    # print(uid)
    fs: firestore.firestore.Client = firestore.client()
    token = firebase_auth.create_custom_token(uid).decode('utf-8')
    # print(f'token: {token}')
    otp = generateOTP()
    # print('try')
    try:
        # print('setting otp')
        fs.collection('OTP').document(otp).set({
            'token': token
        })
        # print('otp has been set')
        # print('setting token')
        fs.collection('TokenList').document(token).set({
            "key": payload.key,
            "mode": payload.mode
        })
        # print('token has been set')
        doc = fs.collection('Manager').document(payload.uid).get()
        if doc.exists:
            data = doc._data
            data[payload.mode] = otp
            fs.collection('Manager').document(payload.uid).set(data)
        return {
            'OTP': otp
        }
    except Exception as e:
        logging.error(f'error {e}')
        raise HTTPException(
            status_code=404, detail='error has occur in setting token process')


async def clearToken(payload: Payload.ClearToken):
    fs: firestore.firestore.Client = firestore.client()

    if payload.secret == 'my_secret_1234':

        docs = fs.collection('OTP').list_documents()
        for doc in docs:
            print(f"Deleting doc {doc.id} => {doc.get().to_dict()}")
            doc.delete()

        docs = fs.collection('TokenList').list_documents()
        for doc in docs:
            print(f"Deleting doc {doc.id} => {doc.get().to_dict()}")
            doc.delete()

        docs = fs.collection('Manager').where(
            'name', '==', payload.username).get()
        for doc in docs:
            dic: dict = doc._data
            if dic.__contains__('Reception'):
                dic.pop('Reception')
            if dic.__contains__('Chef'):
                dic.pop('Chef')
            fs.collection('Manager').document(doc.id).set(dic)

        return {
            'message': True
        }

    return {
        'message': 'secret not match.'
    }
