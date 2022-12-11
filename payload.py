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

    class updateStorage(BaseModel):
        imgBytes: str

    class updateProduct(BaseModel):
        shop_key: str
        type: str
        id: str
        product: datatypes.Product
