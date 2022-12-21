from firebase_admin import firestore, db, storage
from _firebase import firebase_auth
import uuid


async def home():
    return "Hello! This is API server."


async def generateToken():
    uid = uuid.uuid4()
    return firebase_auth.create_custom_token(uid)
