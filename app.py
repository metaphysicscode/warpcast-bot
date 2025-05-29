
import os
import time
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

USERS = os.getenv("WARPCAST_USERS", "").split(",")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

last_seen = {}

def get_latest_cast(username):
    try:
        url = f"https://warpcast.com/{username.strip()}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        scripts = soup.find_all("script", {"type": "application/json"})
        for script in scripts:
            if 'props' in script.text and 'cast' in script.text:
                raw = script.string
                if raw and '"text":"' in raw:
                    start = raw.find('"text":"') + 8
                    end = raw.find('"', start)
                    text = raw[start:end]
                    return text
        return None
    except Exception as e:
        print(f"[{username}] Error: {e}")
        return None

def send_to_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        params = {"chat_id": TELEGRAM_CHAT_ID, "text": msg}
        requests.get(url, params=params)
    except Exception as e:
        print(f"Telegram Error: {e}")

if __name__ == "__main__":
    while True:
        for user in USERS:
            cast = get_latest_cast(user)
            if cast:
                if user not in last_seen or last_seen[user] != cast:
                    message = f"[{user}] {cast}"
                    print(message)
                    send_to_telegram(message)
                    last_seen[user] = cast
        time.sleep(5)
