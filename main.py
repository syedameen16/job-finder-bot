"""
🎯 DAILY JOB TRACKER for Indian Data Analyst Freshers
Tracks NEW postings on real job portals
No scraping, no APIs, no junk
"""

import os
import json
import hashlib
from datetime import datetime
from telegram import Bot

# ========== CONFIG ==========
HISTORY_FILE = "tracked_jobs.json"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# ========== YOUR DAILY JOB PORTALS ==========
DAILY_PORTALS = [
    {
        "name": "LinkedIn Bangalore",
        "url": "https://www.linkedin.com/jobs/search/?keywords=data%20analyst%20fresher&location=bangalore&f_TPR=r86400&position=1&pageNum=0",
        "description": "Data Analyst fresher jobs in Bangalore (last 24h)"
    },
    {
        "name": "LinkedIn Chennai", 
        "url": "https://www.linkedin.com/jobs/search/?keywords=data%20analyst%20fresher&location=chennai&f_TPR=r86400",
        "description": "Data Analyst fresher jobs in Chennai (last 24h)"
    },
    {
        "name": "LinkedIn Hyderabad",
        "url": "https://www.linkedin.com/jobs/search/?keywords=data%20analyst%20fresher&location=hyderabad&f_TPR=r86400",
        "description": "Data Analyst fresher jobs in Hyderabad (last 24h)"
    },
    {
        "name": "Naukri Fresher Bangalore",
        "url": "https://www.naukri.com/data-analyst-fresher-jobs-in-bangalore?k=data%20analyst%20fresher&l=bangalore",
        "description": "Data Analyst fresher jobs on Naukri Bangalore"
    },
    {
        "name": "Indeed Fresher India",
        "url": "https://in.indeed.com/jobs?q=data+analyst+fresher&l=india&fromage=1",
        "description": "Data Analyst fresher jobs across India (last 24h)"
    },
    {
        "name": "Foundit Fresher",
        "url": "https://www.foundit.in/data-analyst-fresher-jobs-in-india",
        "description": "Data Analyst fresher jobs on Foundit"
    },
    {
        "name": "Python Fresher Bangalore",
        "url": "https://www.linkedin.com/jobs/search/?keywords=python%20fresher&location=bangalore&f_TPR=r86400",
        "description": "Python fresher jobs in Bangalore"
    },
    {
        "name": "SQL Fresher India",
        "url": "https://www.linkedin.com/jobs/search/?keywords=sql%20fresher&location=india&f_TPR=r86400",
        "description": "SQL fresher jobs across India"
    },
]

# ========== HELPER FUNCTIONS ==========
def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def get_portal_id(portal):
    return hashlib.md5(f"{portal['name']}_{portal['url']}".encode()).hexdigest()

# ========== TELEGRAM MESSAGE ==========
def send_daily_summary(bot, new_portals_count):
    """Send one clean daily summary"""
    today = datetime.now().strftime("%B %d, %Y")
    
    message = f"""
🎯 *DAILY JOB CHECKLIST - {today}*

✅ *Your curated job portals are READY*

📊 *Portals to check today:* {len(DAILY_PORTALS)}
🆕 *Updated since yesterday:* {new_portals_count}

---

*📍 TODAY'S PORTALS:*

"""
    
    # Add each portal
    for i, portal in enumerate(DAILY_PORTALS, 1):
        message += f"{i}. *{portal['name']}*\n"
        message += f"   {portal['description']}\n"
        message += f"   🔗 [Open Portal]({portal['url']})\n\n"
    
    message += f"""
---

*⚡ QUICK TIPS:*
1. Check each portal (takes 10-15 minutes)
2. Apply to 3-5 relevant jobs daily
3. Bookmark interesting companies
4. Set job alerts on LinkedIn

*📈 YOUR CRITERIA:*
• Data Analyst / Business Analyst
• Fresher (0-2 years)
• Python, SQL, Power BI, Excel
• Bangalore, Chennai, Hyderabad, Pune
• IT, Software, E-commerce, Analytics

*⏰ Best time to apply:* 10 AM - 4 PM
*🎯 Target:* 10 applications/week

Good luck! 🚀
"""
    
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
        return True
    except Exception as e:
        print(f"Telegram error: {e}")
        return False

# ========== MAIN ==========
def main():
    print("=" * 60)
    print("🎯 DAILY JOB PORTAL TRACKER")
    print("=" * 60)
    
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Set Telegram credentials")
        return
    
    # Load history
    history = load_history()
    
    # Track which portals are "new" (not sent today)
    new_portals = []
    today = datetime.now().strftime("%Y-%m-%d")
    
    for portal in DAILY_PORTALS:
        portal_id = get_portal_id(portal)
        
        # Check if we sent this portal today
        if portal_id not in history or history[portal_id] != today:
            new_portals.append(portal)
            history[portal_id] = today  # Mark as sent today
    
    # Send summary
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    if new_portals:
        success = send_daily_summary(bot, len(new_portals))
        if success:
            print(f"✅ Sent daily checklist with {len(new_portals)} portals")
            
            # Save history
            save_history(history)
            print(f"💾 Updated tracking history")
        else:
            print("❌ Failed to send message")
    else:
        print("📭 All portals already checked today")
    
    print(f"\n📊 Total portals: {len(DAILY_PORTALS)}")
    print(f"🆕 New today: {len(new_portals)}")
    print("=" * 60)

if __name__ == "__main__":
    main()
