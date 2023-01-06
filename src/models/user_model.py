# imports from default libs
from datetime import datetime
from typing import Any, List, Mapping

# imports from src
from .subscription_model import Subscription

Subscriptions = List[Subscription]


class User:
    def __init__(self,
                 chat_id: int or None,
                 language: str or None,
                 started_at: datetime or None,
                 last_message: datetime or None,
                 username: str or None = None,
                 first_name: str or None = None,
                 last_name: str or None = None,
                 subscriptions: Subscriptions = None):
        self.chat_id = chat_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.language = language
        self.started_at = started_at
        self.last_message = last_message
        self.subscriptions = subscriptions

    @property
    def empty(self):
        return User(chat_id=None, language=None, started_at=None, last_message=None)

    @property
    def isEmpty(self) -> bool:
        return self == User.empty

    @property
    def isNotEmpty(self) -> bool:
        return self != User.empty

    def toJson(self) -> Mapping[str, Any]:
        return {
            'chat_id': self.chat_id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'language': self.language,
            'started_at': self.started_at,
            'last_message': self.last_message,
        }

    @staticmethod
    def fromJson(json: Mapping[str, Any]):
        return User(
            chat_id=json['chat_id'],
            username=json['username'],
            first_name=json['first_name'],
            last_name=json['last_name'],
            language=json['language'],
            started_at=json['started_at'],
            last_message=json['last_message'],
        )
