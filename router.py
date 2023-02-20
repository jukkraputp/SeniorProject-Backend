from fastapi import APIRouter, Body, Header

from routing import Routes

from payload import Payload

import json

router = APIRouter()

with open('secret.json') as json_file:
    data = json.load(json_file)
    api_key = data['api_key']

# ------------- GET -----------------------------------------------


@router.get('/')
async def root(param: str):
    return await Routes.get.Home(param)


@router.get('/check-token/')
async def checkToken(token: str):
    return await Routes.get.CheckToken(token)

# ------------- POST ----------------------------------------------


@router.post('/auth')
async def auth(payload: Payload.Auth):
    return await Routes.post.Auth(payload)


@router.post('/add')
async def addOrder(payload: Payload.Order):
    return await Routes.post.AddOrder(payload)


@router.post('/finish')
async def finishOrder(payload: Payload.FinishOrder):
    return await Routes.post.FinishOrder(payload)


@router.post('/complete')
async def completeOrder(payload: Payload.CompleteOrder):
    return await Routes.post.CompleteOrder(payload)


@router.post('/update-storage')
async def updateStorage(payload: Payload.UpdateStorage):
    return await Routes.post.UpdateStorage()


@router.post('/update-product')
async def updateProdct(payload: Payload.UpdateProduct):
    print('update-product')
    return await Routes.post.UpdateProduct(payload)


@router.post('/register')
async def register(payload: Payload.Register):
    print('register')
    return await Routes.post.Register(payload)


@router.post('/generate-token')
async def generateToken(payload: Payload.GenerateToken):
    return await Routes.post.GenerateToken(payload)


@router.post('/clear-token')
async def clearToken(payload: Payload.ClearToken):
    return await Routes.post.ClearToken(payload)


@router.post('/save-order')
async def saveOrder(payload: Payload.SaveOrder):
    return await Routes.post.SaveOrder(payload)

@router.post('/update-payment')
async def updatePayment(payload: Payload.UpdatePayment):
    return await Routes.post.UpdatePayment(payload)

@router.post('/add-shop')
async def addShop(payload: Payload.AddShop):
    return await Routes.post.AddShop(payload)

@router.post('/add-type')
async def addType(payload: Payload.EditType):
    return await Routes.post.AddType(payload)

@router.post('/delete-type')
async def deleteType(payload: Payload.EditType):
    return await Routes.post.DeleteType(payload)

''' @router.post('/create-shopkey')
async def createShopKey(payload: Payload.ShopKeyComponent, key: str = Header(default=None)):
    if key == api_key:
        return await Routes.post.CreateShopKey(payload)
    else:
        return {
            'message': False
        }


@router.post('/get-shopkey')
async def getShopKey(payload: Payload.ShopKeyComponent, key: str = Header(default=None)):
    if key == api_key:
        return await Routes.post.GetShopKey(payload)
    else:
        return {
            'message': False
        } '''


# ------------ AUTH ------------------------------------------------


def authorize(shopName: str, shopKey: str):
    return True
    if key == shopKey:
        return True
    else:
        return False
