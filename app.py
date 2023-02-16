from fastapi import FastAPI
from router import router
import _firebase
from utilities import sendMessagesToTopics
from payload import Payload
import json

app = FastAPI()

app.include_router(router)


@app.post('/test-fcm')
async def testFCM(payload: Payload.testFCM):
    res = sendMessagesToTopics(
        notification={
            'title': 'Your meals have been ready',
            'body': "Let's go grab your food"
        },
        data={
            'message': 'finishOrder',
            'data': json.dumps({
                'orderId': payload.orderId,
                'shopName': payload.shopName
            })
        }, topic=f'{payload.shopName}_{payload.date}_{payload.orderId}')
    return res
