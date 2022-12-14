from datetime import datetime
from firebase_admin import db, firestore
from _firebase import storage_bucket

from payload import Payload


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


''' async def register(payload: Payload.Register):
    fs: firestore.firestore.Client = firestore.client()
    try:
        fs.collection(u'Register')
    return True '''
