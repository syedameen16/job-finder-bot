import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": msg
    }
    r = requests.post(url, data=data)
    print(r.text)  # this will show error in GitHub logs if any

def check_jobs():
    jobs = [
        "Data Analyst | SQL Excel | Bangalore",
        "MIS Executive | Reporting | Chennai"
    ]
    for job in jobs:
        send_telegram(job)

if __name__ == "__main__":
    check_jobs()
