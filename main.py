import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

print("BOT_TOKEN:", BOT_TOKEN)
print("CHAT_ID:", CHAT_ID)

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
data = {"chat_id": CHAT_ID, "text": "Test from GitHub"}

r = requests.post(url, data=data)

print("Status Code:", r.status_code)
print("Response:", r.text)
