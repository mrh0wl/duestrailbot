# imports from standar lib
from enum import Enum, auto

# imports from pyrogram

# imports from src
from ..utils import I18n


class PlatformModel:
    def __init__(cls, id: int, i18n: I18n):
        names = {
            'netflix': {
                'name': 'Netflix',
                'logo': 'https://i.imgur.com/HGxIq53.png'
            },
            'gamepass': {
                'name': 'Xbox/PC Game Pass',
                'logo': 'https://i.imgur.com/To0i5VS.png'
            },
            'playplus': {
                'name': 'PlayStation Plus',
                'logo': 'https://i.imgur.com/mIdhyg7.png'
            },
            'spotify': {
                'name': 'Spotify',
                'logo': 'https://i.imgur.com/XpyhuTK.png'
            },
            'twitch': {
                'name': 'Twitch',
                'logo': 'https://i.imgur.com/Nyah7fo.png'
            },
            'primevideo': {
                'name': 'Prime Video',
                'logo': 'https://i.imgur.com/klM7KMW.png'
            }
        }
        cls.id = id
        cls.name = names[cls.id]['name']
        cls.logo = names[cls.id]['logo']
        cls.short = i18n.t(f'{cls.id}_short')
        cls.description = i18n.t(f'{cls.id}_description')


class Platforms(Enum):
    NETFLIX = auto()
    GAMEPASS = auto()
    PLAYPLUS = auto()
    SPOTIFY = auto()
    TWITCH = auto()
    PRIMEVIDEO = auto()
