import requests
import json
import os
from datetime import datetime
from bs4 import BeautifulSoup
from telegram import Bot
from telegram.error import TelegramError
import asyncio
import hashlib

# Import config
try:
    from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, LOCATIONS
    from resume_keywords import RESUME_KEYWORDS
except ImportError:
    # For local testing
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    LOCATIONS = ['Bangalore', 'Bengaluru', 'Hyderabad', 'Pune', 'Chennai', 'Remote', 'India']

class GitHubJobAlert:
    def __init__(self):
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN) if TELEGRAM_BOT_TOKEN else None
        self.history_file = 'jobs_history.json'
        self.seen_jobs = self.load_history()
        
    def load_history(self):
        """Load previously seen jobs"""
        try:
            with open(self.history_file, 'r') as f:
                return set(json.load(f))
        except FileNotFoundError:
            return set()
    
    def save_history(self):
        """Save seen jobs"""
        with open(self.history_file, 'w') as f:
            json.dump(list(self.seen_jobs), f)
    
    def generate_job_id(self, job):
        """Create unique ID for job"""
        job_str = f"{job.get('title', '')}{job.get('company', '')}{job.get('platform', '')}"
        return hashlib.md5(job_str.encode()).hexdigest()
    
    def check_location(self, location):
        """Check if location matches our criteria"""
        if not location:
            return False
        location_lower = location.lower()
        return any(loc.lower() in location_lower for loc in LOCATIONS)
    
    def search_github_jobs(self):
        """Search GitHub Jobs API"""
        jobs = []
        try:
            url = "https://jobs.github.com/positions.json"
            params = {
                'description': 'data analyst',
                'location': 'india'
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for job in data:
                    if self.check_location(job.get('location', '')):
                        jobs.append({
                            'title': job.get('title', ''),
                            'company': job.get('company', ''),
                            'location': job.get('location', ''),
                            'link': job.get('url', ''),
                            'platform': 'GitHub Jobs',
                            'type': job.get('type', ''),
                            'description': job.get('description', '')[:200] + '...'
                        })
        except Exception as e:
            print(f"Error searching GitHub Jobs: {e}")
        return jobs
    
    def search_naukri_simple(self):
        """Simple Naukri search"""
        jobs = []
        try:
            # Note: Naukri has anti-scraping. This is a simplified version.
            # For production, consider using their API with proper authentication.
            search_queries = [
                'data+analyst+bangalore',
                'power+bi+developer+hyderabad',
                'sql+analyst+pune',
                'python+data+analyst+chennai'
            ]
            
            for query in search_queries:
                url = f"https://www.naukri.com/{query}-jobs"
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Note: Naukri's HTML structure changes frequently
                    # This is a basic example
                    job_cards = soup.find_all('article', class_='jobTuple')
                    
                    for card in job_cards[:5]:  # Limit to 5 per query
                        try:
                            title_elem = card.find('a', class_='title')
                            company_elem = card.find('a', class_='subTitle')
                            location_elem = card.find('li', class_='location')
                            
                            if title_elem:
                                job = {
                                    'title': title_elem.text.strip(),
                                    'company': company_elem.text.strip() if company_elem else 'Not specified',
                                    'location': location_elem.text.strip() if location_elem else 'India',
                                    'link': title_elem.get('href', ''),
                                    'platform': 'Naukri',
                                    'description': 'Data analyst position'
                                }
                                
                                if self.check_location(job['location']):
                                    jobs.append(job)
                        except:
                            continue
                
                # Be polite - delay between requests
                import time
                time.sleep(2)
                
        except Exception as e:
            print(f"Error searching Naukri: {e}")
        
        return jobs
    
    def search_linkedin_simple(self):
        """Simple LinkedIn search using public endpoint"""
        jobs = []
        try:
            # Using LinkedIn's public job search (simplified)
            queries = [
                'data-analyst-jobs-bangalore',
                'power-bi-developer-jobs-hyderabad',
                'sql-analyst-jobs-pune',
                'python-data-analyst-jobs-chennai'
            ]
            
            for query in queries:
                url = f"https://www.linkedin.com/jobs/search/?keywords={query}"
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract job data from script tag (LinkedIn stores data in JSON-LD)
                    script_tags = soup.find_all('script', type='application/ld+json')
                    
                    for script in script_tags:
                        try:
                            data = json.loads(script.string)
                            if isinstance(data, list):
                                for item in data:
                                    if item.get('@type') == 'JobPosting':
                                        job = {
                                            'title': item.get('title', ''),
                                            'company': item.get('hiringOrganization', {}).get('name', ''),
                                            'location': item.get('jobLocation', {}).get('address', {}).get('addressLocality', 'India'),
                                            'link': item.get('url', ''),
                                            'platform': 'LinkedIn',
                                            'description': item.get('description', '')[:200] + '...'
                                        }
                                        
                                        if self.check_location(job['location']):
                                            jobs.append(job)
                        except:
                            continue
                
                import time
                time.sleep(3)  # Longer delay for LinkedIn
                
        except Exception as e:
            print(f"Error searching LinkedIn: {e}")
        
        return jobs
    
    def check_keywords_match(self, job_title, job_description):
        """Check if job matches your resume keywords"""
        text = f"{job_title} {job_description}".lower()
        
        # Your specific keywords from resume
        your_keywords = [
            'python', 'sql', 'power bi', 'excel', 'pandas', 
            'data analysis', 'dashboard', 'visualization',
            'mysql', 'jupyter', 'analytics', 'etl'
        ]
        
        match_count = sum(1 for keyword in your_keywords if keyword in text)
        return match_count >= 3
    
    def format_message(self, job):
        """Format job alert for Telegram"""
        return f"""
🚀 **New Job Alert!**

**Position:** {job['title']}
**Company:** {job['company']}
**Location:** {job['location']}
**Platform:** {job['platform']}

[Apply Here]({job['link']})

⏰ Found at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()
    
    async def send_telegram_alert(self, job):
        """Send alert to Telegram"""
        if not self.bot:
            print("Telegram bot not configured")
            return False
            
        try:
            message = self.format_message(job)
            await self.bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=message,
                parse_mode='Markdown',
                disable_web_page_preview=False
            )
            print(f"✓ Alert sent: {job['title']}")
            return True
        except TelegramError as e:
            print(f"✗ Telegram error: {e}")
            return False
    
    async def run_search(self):
        """Main search function"""
        print("🔍 Starting job search...")
        print(f"📍 Locations: {', '.join(LOCATIONS)}")
        
        all_jobs = []
        
        # Search different platforms
        print("Searching GitHub Jobs...")
        all_jobs.extend(self.search_github_jobs())
        
        print("Searching Naukri...")
        all_jobs.extend(self.search_naukri_simple())
        
        print("Searching LinkedIn...")
        all_jobs.extend(self.search_linkedin_simple())
        
        print(f"\n📊 Found {len(all_jobs)} total jobs")
        
        # Filter and send alerts
        new_jobs = []
        for job in all_jobs:
            job_id = self.generate_job_id(job)
            
            # Skip if already seen
            if job_id in self.seen_jobs:
                continue
            
            # Check if job matches keywords
            if self.check_keywords_match(job['title'], job.get('description', '')):
                # Send alert
                success = await self.send_telegram_alert(job)
                if success:
                    self.seen_jobs.add(job_id)
                    new_jobs.append(job)
                    print(f"  → New: {job['title']} at {job['company']}")
            
            # Small delay between sends
            await asyncio.sleep(0.5)
        
        # Save history
        self.save_history()
        
        print(f"\n✅ Search complete: {len(new_jobs)} new alerts sent")
        return new_jobs

async def main():
    """Main function for GitHub Actions"""
    alert_bot = GitHubJobAlert()
    
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Warning: Telegram credentials not set")
        print("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables")
        print("Jobs will be found but not sent to Telegram")
    
    new_jobs = await alert_bot.run_search()
    
    # For GitHub Actions output
    if new_jobs:
        print(f"::set-output name=new_jobs::{len(new_jobs)}")
    else:
        print("::set-output name=new_jobs::0")

if __name__ == "__main__":
    asyncio.run(main())
