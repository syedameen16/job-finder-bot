import requests
import time
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    requests.post(url, data=data)

def check_jobs():
    # TEMP demo — replace with real scraping later
    jobs = [
        "Data Analyst | SQL Excel | Bangalore",
        "MIS Executive | Reporting | Chennai"
    ]
    for job in jobs:
        send_telegram(job)
        
        
if __name__ == "__main__":
    check_jobs()

# while True:
#     check_jobs()
#     time.sleep(3600)
    # Check every hour
    


    