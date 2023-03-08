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
        ownerUID: str
        shopName: str
        shopPhoneNumber: str
        itemList: list
        cost: float
        totalTime: float
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
        uid: str
        shopName: str
        phoneNumber: str
        mode: str

    class ClearToken(BaseModel):
        secret: str
        username: str

    class SaveOrder(BaseModel):
        uid: str
        ownerUID: str
        shopName: str
        orderId: int

    class UploadPaymentImage(BaseModel):
        ownerUID: str
        shopName: str
        date: str
        orderId: int
        paymentImageUrl: str

    class AddShop(BaseModel):
        uid: str
        shopName: str
        phoneNumber: str
        latitude: float
        longitude: float

    class DeleteShop(BaseModel):
        uid: str
        shopName: str

    class EditType(BaseModel):
        uid: str
        shopName: str
        type: str

    ''' class shopKeyComponent(BaseModel):
        shopName: str
        phoneNumber: str '''

    class testFCM(BaseModel):
        shopName: str
        date: str
        orderId: int
