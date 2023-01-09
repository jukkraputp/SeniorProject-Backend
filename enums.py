from enum import Enum

import makeobj
from routes import get, post


class Routes(makeobj.Obj):

    class get(Enum):
        Home = get.home
        CheckToken = get.checkToken

    class post(Enum):
        Auth = post.auth
        AddOrder = post.addOrder
        FinishOrder = post.finishOrder
        CompleteOrder = post.completeOrder
        UpdateStorage = post.updateStorage
        UpdateProduct = post.updateProduct
        Register = post.register
        GenerateToken = post.generateToken
        ClearToken = post.clearToken
