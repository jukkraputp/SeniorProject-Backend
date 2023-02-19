from datetime import datetime
import makeobj
from pydantic import BaseModel
import datatypes
from enums import OrderStatus


class Payload(makeobj.Obj):

    class Auth(BaseModel):
        username: str
        password: str

    class Order(BaseModel):
        uid: str
        shopName: str
        itemList: list
        cost: float
        date: str
        isCompleted: bool
        isFinished: bool
        isPaid: bool
        IID_TOKEN: str

    class FinishOrder(BaseModel):
        uid: str
        shopName: str
        date: str
        orderId: int

    class CompleteOrder(BaseModel):
        uid: str
        date: str
        shopName: str
        orderId: str

    class UpdateStorage(BaseModel):
        item: datatypes.Item

    class UpdateProduct(BaseModel):
        uid: str
        shopName: str
        productList: list[datatypes.Product]

    class Register(BaseModel):
        username: str
        email: str
        password: str
        phoneNumber: str
        mode: str

    class GenerateToken(BaseModel):
        key: str
        mode: str
        uid: str

    class ClearToken(BaseModel):
        secret: str
        username: str

    class SaveOrder(BaseModel):
        uid: str
        shopName: str
        orderId: int

    class UpdatePayment(BaseModel):
        date: str
        shopName: str
        orderId: int

    class AddShop(BaseModel):
        shopName: str
        phoneNumber: str

    ''' class shopKeyComponent(BaseModel):
        shopName: str
        phoneNumber: str '''

    class testFCM(BaseModel):
        shopName: str
        date: str
        orderId: int
