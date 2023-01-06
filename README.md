# Telegram Subscription Bot Tracker

Telegram Subscription Streaming/Gaming platform bot to get your money administered.

## Requirements

> ### Telegram requirements

- API_ID and API_HASH from your telegram account (required for [Pyrogram](https://docs.pyrogram.org/intro/quickstart)).
- A Telegram bot API credentials (check [BotFather](https://t.me/BotFather) to get you API Creds)

> ### Environment requirements

- Tested on Windows and Linux OS (Debian and Ubuntu)
- Python 3.9 or later.

## Run (Assuming you have a Debian-based or Ubuntu distro)

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
python3 main.py
```

**_Note: store your JSON file of Firebase Admin SDK ([Setup here](https://firebase.google.com/docs/admin/setup#initialize-sdk)) inside the 'src/services/cred' folder, then you should open the 'src/services/firestore.py' file and edit <credential.json> with the name of your file_**

## Deploy on Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/mrh0wl/duestrailbot/tree/master)

### Deploy on Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/I776yL?referralCode=aQLW6q)

Send [commands](https://github.com/mrh0wl/duestrailbot/blob/master/README.md#commands) to the bot to help and other info

## Commands

| Command  | Description               |
| :------- | :------------------------ |
| /help    | Show Help Message.        |
| /creator | Show info of creator (me) |

## Note

- If you want any help you can ask [here](https://t.me/mrh0wl) or [open an issue](https://github.com/mrh0wl/duestrailbot/issues/new)
- If you want to see the bot in action search for [@duestrailbot](https://t.me/duestrailbot) in telegram

## Credits

1. [@mrh0wl](https://github.com/mrh0wl)
2. Thanks to everyone who contributed to the project.
