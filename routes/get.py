import firebase_admin
from firebase_admin import firestore, db, storage, credentials
from _firebase import firebase_auth
import uuid
import datetime
import logging
import jwt
from utilities import createJWT


async def home():
    return "Hello! This is API server."


async def checkToken(token: str):
    return firebase_auth.verify_id_token(token)
