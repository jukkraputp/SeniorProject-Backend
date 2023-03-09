from enum import Enum

import makeobj
from routes import get, post

class Routes(makeobj.Obj):

    class get():
        Home = staticmethod(get.home)
        CheckToken = staticmethod(get.checkToken)

    class post():
        Auth = staticmethod(post.auth)
        AddOrder = staticmethod(post.addOrder)
        FinishOrder = staticmethod(post.finishOrder)
        CompleteOrder = staticmethod(post.completeOrder)
        UpdateStorage = staticmethod(post.updateStorage)
        UpdateProduct = staticmethod(post.updateProduct)
        Register = staticmethod(post.register)
        GenerateToken = staticmethod(post.generateToken)
        ClearToken = staticmethod(post.clearToken)
        SaveOrder = staticmethod(post.saveOrder)
        UploadPaymentImage = staticmethod(post.uploadPaymentImage)
        UpdatePaymentStatus = staticmethod(post.updatePaymentStatus)
        AddShop = staticmethod(post.addShop)
        AddType = staticmethod(post.addType)
        DeleteType = staticmethod(post.deleteType)
        DeleteShop = staticmethod(post.deleteShop)
        ''' CreateShopKey = staticmethod(post.createShopKey)
        GetShopKey = staticmethod(post.getShopKey) '''