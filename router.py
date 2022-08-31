from fastapi import APIRouter, Body

from enums import Routes

from datatypes import Payload
from utilities import getShopKey

router = APIRouter()

# ------------- GET -----------------------------------------------


@router.get('/')
async def root():
    return await Routes.get.Home()

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


# ------------ AUTH ------------------------------------------------


def authorize(shopName: str, shopKey: str):
    key = getShopKey(shopName)
    return True
    if key == shopKey:
        return True
    else:
        return False
