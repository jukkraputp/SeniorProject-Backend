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
import pytz


async def auth(payload: Payload.Auth):
    print(payload)
    return True


async def addOrder(payload: Payload.Order):
    date: datetime = parser.parse(payload.date).astimezone(pytz.utc)
    today = f'{date.year}/{date.month}/{date.day}'
    idRef = db.reference(
        f'OrderId/{payload.ownerUID}-{payload.shopName}/{today}')
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
        f'Order/{payload.ownerUID}-{payload.shopName}/{today}/order{orderId}')
    dic = payload.dict()
    dic.pop('shopName')
    dic['isFinished'] = False
    dic['paymentImage'] = None
    if not ref.get():
        ref.set(dic)
        saveOrderRes = await saveOrder(Payload.SaveOrder(uid=payload.uid, ownerUID=payload.ownerUID, shopName=payload.shopName, orderId=orderId))
        if saveOrderRes['status']:
            return {
                'status': True,
                'message': "an order has been added",
                'orderId': orderId,
                'orderTopic': f'{payload.ownerUID}_{payload.shopName.replace(" ", "_")}_{today.replace("/","_")}_{orderId}'
            }
    else:
        return {
            'status': False,
            'message': "error has occurred"
        }


async def finishOrder(payload: Payload.FinishOrder):
    fs: firestore.firestore.Client = firestore.client()
    try:
        ref = db.reference(
            f'Order/{payload.uid}-{payload.shopName}/{payload.date}/order{payload.orderId}')
        ref.update({
            'isFinished': True
        })
        docs = fs.collection('Orders').where('ownerUID', '==', payload.uid).where('date', '==', payload.date).where(
            'orderId', '==', payload.orderId).where('shopName', '==', payload.shopName).get()
        for doc in docs:
            if doc.exists:
                fs.collection('Orders').document(doc.id).update({
                    'isFinished': True
                })
        sendMessagesToTopics(
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
            }, topic=f'{payload.uid}_{payload.shopName.replace(" ", "_")}_{payload.date.replace("/", "_")}_{payload.orderId}')
    except Exception as e:
        return {
            'status': False,
            'message': e.__str__()
        }
    return {
        'status': True
    }


async def completeOrder(payload: Payload.CompleteOrder):
    path = f'Order/{payload.uid}-{payload.shopName}/{payload.date}/order{payload.orderId}'
    ref = db.reference(path=path)
    orderData = ref.get()
    if orderData is None:
        return {
            'status': False,
            'message': 'order not found'
        }
    data = dict(orderData)
    data.pop('isFinished')
    print(data['date'])
    data['date'] = datetime.fromisoformat(
        data['date']).astimezone(pytz.utc)
    data['orderId'] = int(payload.orderId)
    data['isCompleted'] = True
    print(data)

    fs: firestore.firestore.Client = firestore.client()
    try:
        fs.collection(u'History').document(f'{payload.uid}-{payload.shopName}').update({
            'dates': firestore.firestore.ArrayUnion([payload.date])
        })
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
        sendMessagesToTopics(
            notification={
                'title': 'Your meals have been ready',
                'body': "Let's go grab your food!"
            }, data={
                'message': 'completeOrder',
            }, topic=f'{payload.uid}_{payload.shopName.replace(" ","_")}_{payload.date.replace("/","_")}_{payload.orderId}')
        return {
            'status': True
        }
    except Exception as e:
        return {
            'status': False,
            'message': e.__str__()
        }


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
                        "id": product.id,
                        "name": product.name,
                        "price": product.price,
                        "time": product.time,
                        "image": product.imageUrl,
                        "available": product.available
                    })
    except Exception as e:
        print(e)
        return {
            'status': True,
            'message': e.__str__()
        }
    return {
        'status': True
    }


async def updateAvailableType(uid: str, shopName: str, type: str):
    fs: firestore.firestore.Client = firestore.client()
    docs = fs.collection(u'Menu').document(
        f'{uid}-{shopName}').collection(type).get()
    for element in docs:
        doc: firestore.firestore.DocumentSnapshot = element
        if not doc.exists:
            await deleteType(Payload.EditType(uid=uid, shopName=shopName, type=type))


async def addType(payload: Payload.EditType):
    fs: firestore.firestore.Client = firestore.client()
    fs.collection(u'Menu').document(
        f'{payload.uid}-{payload.shopName}').update({
            'types': firestore.firestore.ArrayUnion([payload.type])
        })


async def deleteType(payload: Payload.EditType):
    fs: firestore.firestore.Client = firestore.client()
    fs.collection(u'Menu').document(
        f'{payload.uid}-{payload.shopName}').update({
            'types': firestore.firestore.ArrayRemove([payload.type])
        })


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
                'email': payload.email,
                'shopList': []
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
                    "uid": payload.uid,
                    "shopName": payload.shopName,
                    "phoneNumber": payload.phoneNumber,
                    "mode": payload.mode
                })
                docs = fs.collection('TokenList').where('shopName', '==', payload.shopName).where('mode', '==', payload.mode).where('Document ID', '!=', token).get()
                for doc in docs:
                    if doc.exists:
                        fs.collection('TokenList').document(doc.id).delete()
                # print('token has been set')
                doc = fs.collection('Manager').document(payload.uid).get()
                if doc.exists:
                    manager_data = doc._data
                    obj: dict[str, str]
                    for obj in manager_data['shopList']:
                        if obj['shopName'] == payload.shopName:
                            obj[payload.mode] = otp
                            break
                    fs.collection('Manager').document(
                        payload.uid).set(manager_data)
                
                return {
                    'status': True,
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
            'status': True
        }

    return {
        'status': False,
        'message': 'secret not match.'
    }


async def saveOrder(payload: Payload.SaveOrder):
    fs: firestore.firestore.Client = firestore.client()
    fs.collection('Orders').add({
        'uid': payload.uid,
        'ownerUID': payload.ownerUID,
        'shopName': payload.shopName,
        'orderId': payload.orderId,
        'date': f'{datetime.utcnow().year}/{datetime.utcnow().month}/{datetime.utcnow().day}',
        'isCompleted': False,
        'isFinished': False,
        'isPaid': False
    })

    return {
        'status': True
    }


async def uploadPaymentImage(payload: Payload.UploadPaymentImage):
    fs: firestore.firestore.Client = firestore.client()
    try:
        path = f'Order/{payload.ownerUID}-{payload.shopName}/{payload.date}/order{payload.orderId}'
        orderRef = db.reference(path)
        orderData = dict(orderRef.get())
        print(path, orderData)
        orderData['paymentImage'] = payload.paymentImageUrl
        orderRef.set(orderData)
        docs = fs.collection('Orders').where('shopName', '==', payload.shopName).where(
            'ownerUID', '==', payload.ownerUID).where('orderId', '==', payload.orderId).where('date', '==', payload.date).get()
        for doc in docs:
            if doc.exists:
                data = doc.to_dict()
                if data != None:
                    data['paymentImage'] = payload.paymentImageUrl
                    fs.collection('Orders').document(doc.id).set(data)
    except Exception as e:
        return {
            'status': False,
            'message': e.__str__()
        }
    return {
        'status': True
    }


async def addShop(payload: Payload.AddShop):
    fs: firestore.firestore.Client = firestore.client()
    countryCode = '+66'

    try:
        doc = fs.collection('Manager').document(payload.uid).get()
        if doc.exists:
            data = doc.to_dict()
            if data == None:
                data = {'shopList': []}
            shopList = data['shopList']
            for shopName in shopList:
                if payload.shopName == shopName:
                    raise Exception('This shop name is already exist.')
        fs.collection('Manager').document(payload.uid).update({
            u'shopList': firestore.firestore.ArrayUnion([{'shopName': payload.shopName}])
        })
        fs.collection('ShopList').add({
            'shopName': payload.shopName,
            'phoneNumber': payload.phoneNumber.replace(countryCode, '0'),
            'rating': float(0),
            'rater': 0,
            'ownerUID': payload.uid,
            'position': firestore.firestore.GeoPoint(latitude=payload.latitude, longitude=payload.longitude)
        })
        fs.collection('Menu').document(f'{payload.uid}-{payload.shopName}').set({
            'types': []
        })
        fs.collection('History').document(f'{payload.uid}-{payload.shopName}').set({
            'dates': []
        })

    except Exception as e:
        return {
            'status': False,
            'message': e.__str__()
        }
    return {
        'status': True
    }


async def deleteShop(payload: Payload.DeleteShop):
    fs: firestore.firestore.Client = firestore.client()

    docs = fs.collection('ShopList').where(
        'shopName', '==', payload.shopName).where('ownerUID', '==', payload.uid).get()
    for doc in docs:
        if doc.exists:
            doc.reference.delete()

    fs.collection('Menu').document(
        f'{payload.uid}-{payload.shopName}').delete()

    fs.collection('Manager').document(payload.uid).update({
        'shopList': firestore.firestore.ArrayRemove([{'shopName': payload.shopName}])
    })
    pass


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
