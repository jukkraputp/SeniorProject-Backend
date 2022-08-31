from dataclasses import dataclass
from datetime import datetime
from typing import List
import makeobj
from pydantic import BaseModel


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
