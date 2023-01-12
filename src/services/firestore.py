# imports from default libs
from typing import Union, List

# imports from firebase
import firebase_admin
from firebase_admin import firestore
from google.cloud.firestore import Client
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from google.cloud.firestore_v1.document import DocumentReference
from google.cloud.firestore_v1.collection import CollectionReference

# imports from pyrogram
from pyrogram.types import Message

# imports from src
from ..models import User, Subscription, Plan, Payment

import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'src/services/cred/duestrailbot-firebase-adminsdk-v9lol-1e9fde616d.json'

# Application Default credentials are automatically created.
app = firebase_admin.initialize_app()
db = firestore.client()

Subscriptions = List[Subscription]
Payments = Union[Payment, List[Payment]]


class UserDB:
    def __init__(self,
                 message: Message = None,
                 id: int = None,
                 subscription: Subscription = None
                 ) -> None:
        self.id = message.from_user.id or id
        self.message = message
        self.firestore: Client = db.collection(u'users')
        self.doc: DocumentSnapshot = self.firestore.document(
            str(self.id)).get()
        self.ref: DocumentReference = self.doc.reference
        self.subcol: CollectionReference = self.ref.collection(
            u'subscriptions')

        json = self.doc.to_dict()
        chat_id = (message.chat.id
                   if hasattr(message, 'chat')
                   else json['chat_id']
                   if self.doc.exists
                   else message.from_user.id)

        user = User(
            chat_id=chat_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            language=message.from_user.language_code,
            started_at=firestore.SERVER_TIMESTAMP,
            last_message=firestore.SERVER_TIMESTAMP,
        )

        if not self.doc.exists:
            self.ref.set(user.toJson())

        for k, v in user.toJson().items():
            if v and v != self.doc.to_dict()[k] and k != 'started_at':
                self.ref.update({k: v})

    def getUser(self):
        if self.doc.exists:
            return User.fromJson(self.doc.to_dict())

    def subscription(self, subscription: Subscription) -> Subscription:
        doc: DocumentSnapshot = self.subcol.document(subscription.id).get()
        ref: DocumentReference = doc.reference
        if not doc.exists:
            subscription.name = db.collection(u'platforms').document(
                subscription.id).get().to_dict()['name']
            ref.set(subscription.toJson())
            json = ref.get().to_dict()
            json['id'] = subscription.id
            return Subscription.fromJson(json)
        for k, v in subscription.toJson().items():
            if v is not None:
                ref.update({k: v})
        json = ref.get().to_dict()
        json['id'] = subscription.id
        return Subscription.fromJson(json)

    def removeSubscription(self, subscription: str) -> None:
        self.subcol.document(subscription.lower()).delete()

    def listSubscriptions(self) -> Subscriptions:
        result = []
        subscriptions: list = list(self.subcol.get())
        for subscription in subscriptions:
            subscription: DocumentSnapshot
            json = subscription.to_dict()
            json['id'] = subscription.id
            result.append(Subscription.fromJson(json))

        return result


class PaymentDB:
    def __new__(self, platform: str, plan: str) -> Payments:
        self.firestore = db.collection(u'platforms')
        self.doc: DocumentSnapshot = self.firestore.document(
            platform.lower()).get()
        if self.doc.exists:
            json = self.doc.to_dict()
            json = {k: json[k] for k in json if k != 'plans'}
            plans = self.doc.to_dict()['plans']
            if plan is not None:
                return list([Payment(discounts=json['discounts'], extra_fees=json['extra_fees'], total_pay=[] if k == plan else 0, plan=Plan.fromJson({k: v})) for k, v in plans.items() if k == plan])[0]
            return [Payment(discounts=json['discounts'], extra_fees=json['extra_fees'], total_pay=[], plan=Plan.fromJson({k: v})) for k, v in plans.items()]
