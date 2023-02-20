from datetime import datetime
from firebase_admin import db, firestore
from _firebase import storage_bucket, firebase_auth
from payload import Payload
import uuid
import logging
from fastapi import HTTPException
from utilities import generateOTP, sendMessagesToTopics
import json
from dateutil import parser


async def auth(payload: Payload.Auth):
    print(payload)
    return True


async def addOrder(payload: Payload.Order):
    date: datetime = parser.parse(payload.date)
    today = f'{date.year}/{date.month}/{date.day}'
    idRef = db.reference(f'OrderId/{payload.uid}-{payload.shopName}/{today}')
    idData = idRef.get()
    if idData is not None:
        print(f'idData: {idData}, type: {type(idData)}')
        idDic = dict(idData)
        orderId: int = int(idDic['orderId'])
        idRef.set({
            'orderId': orderId + 1
        })
    else:
        orderId = 1
        idRef.set({
            'orderId': 2
        })
    ref = db.reference(
        f'Order/{payload.uid}-{payload.shopName}/{today}/order{orderId}')
    dic = payload.dict()
    dic.pop('shopName')
    dic['isFinished'] = False
    if not ref.get():
        ref.set(dic)
        saveOrderRes = await saveOrder(Payload.SaveOrder(uid=payload.uid, shopName=payload.shopName, orderId=orderId))
        if saveOrderRes['message']:
            return {
                'message': True,
                'orderId': orderId,
                'orderTopic': f'{payload.uid}_{payload.shopName}_{today.replace("/","_")}_{orderId}'
            }
    else:
        return {
            'message': False
        }


async def finishOrder(payload: Payload.FinishOrder):
    fs: firestore.firestore.Client = firestore.client()
    try:
        ref = db.reference(
            f'Order/{payload.uid}-{payload.shopName}/{payload.date}/order{payload.orderId}')
        ref.update({
            'isFinished': True
        })
        docs = fs.collection('Orders').where('shopUID', '==', payload.uid).where('date', '==', payload.date).where(
            'orderId', '==', payload.orderId).where('shopName', '==', payload.shopName).get()
        for doc in docs:
            if doc.exists:
                fs.collection('Orders').document(doc.id).update({
                    'isFinished': True
                })
        await sendMessagesToTopics(
            notification={
                'title': 'Your meals have been ready',
                'body': "Let's go grab your food!"
            },
            data={
                'message': 'finishOrder',
                'data': json.dumps({
                    'orderId': payload.orderId,
                    'shopName': payload.shopName
                })
            }, topic=f'{payload.uid}_{payload.shopName}_{payload.date.replace("/", "_")}_{payload.orderId}')
        return {
            'message': True
        }
    except Exception as e:
        return {
            'message': e
        }


async def completeOrder(payload: Payload.CompleteOrder):
    ref = db.reference(
        f'Order/{payload.uid}-{payload.shopName}/{payload.date}/order{payload.orderId}')
    data = dict(ref.get())
    data.pop('isFinished')
    data['date'] = datetime.fromisoformat(data['date'])
    data['orderId'] = int(payload.orderId)
    print(data)

    fs: firestore.firestore.Client = firestore.client()
    try:
        fs.collection(u'History').document(f'{payload.uid}-{payload.shopName}').collection(
            payload.date).add(data)
        ref.delete()
        docs = fs.collection('Orders').where('shopUID', '==', payload.uid).where('date', '==', payload.date).where(
            'orderId', '==', payload.orderId).where('shopName', '==', payload.shopName).get()
        for doc in docs:
            if doc.exists:
                fs.collection('Orders').document(doc.id).update({
                    'isCompleted': True
                })
        await sendMessagesToTopics(
            notification={
                'title': 'Your meals have been ready',
                'body': "Let's go grab your food!"
            }, data={
                'message': 'completeOrder',
            }, topic=f'{payload.uid}_{payload.shopName}_{payload.date.replace("/","_")}_{payload.orderId}')
        return {
            'message': True
        }
    except Exception as e:
        raise e


async def updateStorage():
    storage_bucket.location = '/shop1/Food1'
    return storage_bucket.location_type


async def updateProduct(payload: Payload.UpdateProduct):
    fs: firestore.firestore.Client = firestore.client()
    try:
        for product in payload.productList:
            if product.delete:
                fs.collection(u'Menu').document(
                    f'{payload.uid}-{payload.shopName}').collection(product.type).document(product.id).delete()
            else:
                fs.collection(u'Menu').document(
                    f'{payload.uid}-{payload.shopName}').collection(product.type).document(product.id).set({
                        "name": product.name,
                        "price": product.price,
                        "time": product.time
                    })

    except Exception as e:
        print(e)
        return e
    return True


async def register(payload: Payload.Register):
    if payload.mode != 'Manager' and payload.mode != 'Customer':
        return {
            'status': False,
            'message': f'mode: {payload.mode} is not available.'
        }
    fs: firestore.firestore.Client = firestore.client()
    try:
        user: firebase_auth.UserRecord = firebase_auth.create_user(
            email=payload.email, password=payload.password, phone_number=payload.phoneNumber, display_name=payload.username)
        try:
            fs.collection(payload.mode).document(f'{user.uid}').create({
                'username': payload.username,
                'password': payload.password,
                'email': payload.email
            })

            return {
                'status': True,
                'message': 'Registration has been success.'
            }
        except Exception as e:
            print('register2::', e)
            return {
                'status': False,
                'message': e.__str__()
            }

    except Exception as e:
        print('register1::', e)
        return {
            'status': False,
            'message': e.__str__()
        }


async def generateToken(payload: Payload.GenerateToken):
    # print(payload)
    uid = uuid.uuid4().__str__()
    # print(uid)
    fs: firestore.firestore.Client = firestore.client()
    token = firebase_auth.create_custom_token(uid).decode('utf-8')
    # print(f'token: {token}')

    # print('try')
    try:
        while(True):
            otp = generateOTP()
            data = fs.collection('OTP').document(otp).get()
            if not data.exists:
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
            'username', '==', payload.username).get()
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


async def saveOrder(payload: Payload.SaveOrder):
    fs: firestore.firestore.Client = firestore.client()

    fs.collection('Orders').add({
        'uid': payload.uid,
        'shopName': payload.shopName,
        'orderId': payload.orderId,
        'date': f'{datetime.now().year}/{datetime.now().month}/{datetime.now().day}',
        'isCompleted': False,
        'isFinished': False,
        'isPaid': False
    })

    return {
        'message': True
    }


async def updatePayment(payload: Payload.UpdatePayment):
    fs: firestore.firestore.Client = firestore.client()
    try:
        docs = fs.collection('Orders').where('date', '==', payload.date).where(
            'orderId', '==', payload.orderId).where('shopName', '==', payload.shopName).get()
        for doc in docs:
            if doc.exists:
                fs.collection('Orders').document(doc.id).update({
                    'isPaid': True
                })
        return {
            'message': True
        }
    except Exception as e:
        return {
            'message': e
        }


async def addShop(payload: Payload.AddShop):
    fs: firestore.firestore.Client = firestore.client()
    countryCode = '+66'

    try:
        fs.collection('ShopList').add({
            'shopName': payload.shopName,
            'phoneNumber': payload.phoneNumber.replace(countryCode, '0'),
            'rating': 0,
            'rater': 0,
            'ownerUID': payload.uid
        })
        fs.collection('Manager').document(payload.uid).update({
            u'shopList': firestore.firestore.ArrayUnion([payload.shopName])
        })
        return {
            'status': True
        }
    except Exception as e:
        return {
            'status': False,
            'message': e.__str__()
        }


''' async def createshopName(payload: Payload.shopNameComponent):
    fs: firestore.firestore.Client = firestore.client()

    shopName = genshopName(payload.shopName)
    docRef = fs.collection('shopName').document(
        f'{payload.shopName}-{payload.phoneNumber}')
    try:
        if not docRef.get().exists:
            docRef.set({
                'shopName': shopName,
            })
        else:
            return {
                'message': 'this shop already has a key'
            }
        return {
            'message': True
        }
    except Exception as e:
        return {
            'message': e
        }


async def getshopName(payload: Payload.shopNameComponent):
    fs: firestore.firestore.Client = firestore.client()

    data = fs.collection('shopName').document(
        f'{payload.shopName}-{payload.phoneNumber}').get()
    dic = data.to_dict()
    if dic is not None:
        key = dic['shopName']
        with open('secret.json') as json_file:
            secret_data = json.load(json_file)
            fernet_key = bytes(secret_data[f'{payload.shopName}-fernet_key'], 'utf-8')
            return decrypt(encMessage=key, fernet=Fernet(fernet_key))
    else:
        return '' '''
