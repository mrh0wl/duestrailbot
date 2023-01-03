# Telegram Voice-Chat Bot [PyTGCalls] [![Mentioned in Awesome Telegram Calls](https://awesome.re/mentioned-badge-flat.svg)](https://github.com/tgcalls/awesome-tgcalls)

Telegram Subscription Streaming/Gaming platform bot to get your money administered.

## Requirements

> ### Telegram requirements

- API_ID and API_HASH from you telegram account (required for [pyrogram](https://docs.pyrogram.org/intro/quickstart)).
- A Telegram bot API credentials (check [BotFather](https://t.me/BotFather) to get you API Creds)

> ### Environment requirements

- Tested on Windows and Linux OS (debian and ubuntu)
- Python 3.9 or later.

## Run (Assuming you have a debian-based or ubuntu distro)

**Clone and the repository to your machine:**

```sh
git clone https://github.com/mrh0wl/duestrailbot
```

```sh
cd duestrailbot
```

**Install requirements.txt using pip:**

```sh
pip3 install -U -r requirements.txt
```

```sh
$ python3 main.py
```

**_Note: store your JSON file of Firebase Admin SDK ([Setup here](https://firebase.google.com/docs/admin/setup#initialize-sdk)) inside src/services/cred folder, then you should open src/services/firestore.py and edit <credential.json> with the name of your file_**

## Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/mrh0wl/duestrailbot/tree/master)

Send [commands](https://github.com/mrh0wl/duestrailbot/blob/master/README.md#commands) to bot to help and other info

## Commands

| Command  | Description               |
| :------- | :------------------------ |
| /help    | Show Help Message.        |
| /creator | Show info of creator (me) |

## Note

- If you want any help you can ask [here](https://t.me/mrh0wl) or [open an issue](https://github.com/mrh0wl/duestrailbot/issues/new)

## Credits

1. [@mrh0wl](https://github.com/mrh0wl)
2. Thanks to everyone who contributed to the project.
