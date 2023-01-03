# imports from default libs
from datetime import datetime
from collections.abc import Mapping
from typing import Any

# imports from models
from .payment_model import Payment


class Subscription:
    id: str = None
    name: str = None
    start_at: datetime = None
    due_date: datetime = None
    months_paid: int = None
    payment: Payment = None

    def __init__(self,
                 id: str = None,
                 name: str = None,
                 start_at: datetime = None,
                 due_date: datetime = None,
                 months_paid: int = None,
                 payment: Payment = None):
        self.id = id or self.id
        self.name = name or self.name
        self.start_at = start_at or self.start_at
        self.due_date = due_date or self.due_date
        self.months_paid = months_paid or self.months_paid
        self.payment = payment or self.payment

    @property
    def isEditing(self):
        return self.editing if hasattr(self, 'editing') else False

    @property
    def isEmpty(self) -> bool:
        for attr, value in self.__dict__.items():
            if value is None and attr != 'months_paid':
                return True
        return False

    @property
    def inPartFilled(self) -> bool:
        if self.__dict__['payment'] is None:
            return None
        elif self.__dict__['start_at'] is None or self.__dict__['due_date'] is None:
            return 'start_at'
        elif self.__dict__['months_paid'] is None:
            return 'months_paid'
        return None

    def toJson(self) -> Mapping[str, Any]:
        return {
            'name': self.name,
            'start_at': self.start_at,
            'due_date': self.due_date,
            'months_paid': self.months_paid,
            'payment': self.payment.tojson() if self.payment is not None else None,
        }

    @staticmethod
    def fromJson(json: Mapping[str, Any], ):
        return Subscription(
            id=json['id'],
            name=json['name'] if 'name' in json else None,
            start_at=json['start_at'] if 'start_at' in json else None,
            due_date=json['due_date'] if 'due_date' in json else None,
            months_paid=json['months_paid'] if 'months_paid' in json else None,
            payment=Payment.fromJson(
                json=json['payment']) if 'payment' in json and json['payment'] is not None else None
        )
