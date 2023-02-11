from enum import Enum


class OrderStatus(Enum):
    WaitingForPayment = 'Waiting for payment'
    WaitingForPaymentConfirmation = 'Waiting for payment confirmation'
    Cooking = 'Cooking'
    Ready = 'Ready'
    Complete = 'Complete'
