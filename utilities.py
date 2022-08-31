from firebase_admin import firestore

def getShopKey(shopName: str):
    fs: firestore.firestore.Client = firestore.client()
    data = fs.collection('ShopList').document(shopName).get()._data
    key = data['key']
    return key