from fastapi import FastAPI
from router import router
import _firebase

app = FastAPI()

app.include_router(router)
