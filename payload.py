from datetime import datetime
import makeobj
from pydantic import BaseModel
import datatypes


class Payload(makeobj.Obj):

    class Auth(BaseModel):
        username: str
        password: str

    class Order(BaseModel):
        shopKey: str
        orderId: str
        date: datetime
        totalAmount: float
        foods: dict

    class FinishOrder(BaseModel):
        shopKey: str
        orderId: str

    class CompleteOrder(BaseModel):
        shopKey: str
        orderId: str

    class UpdateStorage(BaseModel):
        item: datatypes.Item

    class UpdateProduct(BaseModel):
        shop_key: str
        type: str
        id: str
        product: datatypes.Product

    class Register(BaseModel):
        username: str
        password: str

    class GenerateToken(BaseModel):
        key: str
        mode: str
        uid: str

    class ClearToken(BaseModel):
        secret: str
        username: str
