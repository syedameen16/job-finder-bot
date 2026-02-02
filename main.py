import requests
import json
import os
from datetime import datetime
from bs4 import BeautifulSoup
from telegram import Bot
from telegram.error import TelegramError
import asyncio
import hashlib
import re

from config import JOB_CRITERIA, TARGET_COMPANIES, NOTIFICATION_EMAIL
from resume_keywords import (
    RESUME_KEYWORDS, PREFERRED_LOCATIONS, PREFERRED_INDUSTRIES,
    generate_search_queries, generate_naukri_params
)

class EnhancedJobAlert:
    def __init__(self):
        self.bot = Bot(token=os.environ.get('TELEGRAM_BOT_TOKEN')) if os.environ.get('TELEGRAM_BOT_TOKEN') else None
        self.history_file = 'jobs_history.json'
        self.seen_jobs = self.load_history()
        self.email = NOTIFICATION_EMAIL
        
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
    
    def check_criteria_match(self, job):
        """Check if job matches all your criteria"""
        title = job.get('title', '').lower()
        description = job.get('description', '').lower()
        company = job.get('company', '').lower()
        location = job.get('location', '').lower()
        
        # 1. Check for target companies (priority)
        for target_company in TARGET_COMPANIES:
            if target_company.lower() in company:
                return True, "Target Company"
        
        # 2. Check location
        location_match = False
        for loc in PREFERRED_LOCATIONS:
            if loc.lower() in location:
                location_match = True
                break
        
        if not location_match:
            return False, "Location mismatch"
        
        # 3. Check for experience level (0 years/fresher)
        exp_keywords = ['fresher', 'entry level', 'junior', '0 year', '0-1 year', 'intern']
        exp_match = any(exp in title.lower() or exp in description.lower() for exp in exp_keywords)
        
        if not exp_match:
            # Check for senior roles to exclude
            senior_keywords = ['senior', 'lead', 'manager', '2+', '3+', '4+', '5+']
            if any(senior in title.lower() for senior in senior_keywords):
                return False, "Senior role"
        
        # 4. Check primary keywords
        primary_match_count = 0
        for keyword in RESUME_KEYWORDS['primary']:
            if keyword.lower() in title.lower() or keyword.lower() in description.lower():
                primary_match_count += 1
        
        # 5. Check secondary keywords
        secondary_match_count = 0
        for keyword in RESUME_KEYWORDS['secondary']:
            if keyword.lower() in description.lower():
                secondary_match_count += 1
        
        # Decision logic
        if primary_match_count >= 2:
            return True, f"Primary keywords: {primary_match_count}"
        elif primary_match_count >= 1 and secondary_match_count >= 2:
            return True, f"Mixed keywords: {primary_match_count}+{secondary_match_count}"
        else:
            return False, f"Insufficient keyword match: {primary_match_count} primary, {secondary_match_count} secondary"
    
    def search_naukri_enhanced(self):
        """Enhanced Naukri search with your criteria"""
        jobs = []
        try:
            base_params = generate_naukri_params()
            queries = ['data analyst', 'python analyst', 'sql analyst', 'power bi developer']
            
            for query in queries:
                params = base_params.copy()
                params['keyword'] = query
                
                # Search for each location
                for location in ['bangalore', 'chennai', 'hyderabad', 'pune', 'mumbai']:
                    params['location'] = location
                    
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'appid': '109',
                        'systemid': '109'
                    }
                    
                    response = requests.get(
                        'https://www.naukri.com/jobapi/v3/search',
                        params=params,
                        headers=headers,
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        job_details = data.get('jobDetails', [])
                        
                        for job_data in job_details:
                            # Check salary
                            salary = job_data.get('salary', '')
                            min_salary = self.extract_salary_min(salary)
                            
                            if min_salary and min_salary < 400000:
                                continue  # Skip if less than 4 LPA
                            
                            # Check experience
                            experience = job_data.get('experience', '')
                            if '1' in experience or '2' in experience or '3' in experience:
                                continue  # Skip if requires 1+ years
                            
                            job = {
                                'title': job_data.get('title', ''),
                                'company': job_data.get('companyName', ''),
                                'location': job_data.get('placeholders', [{}])[1].get('label', ''),
                                'link': job_data.get('jdURL', ''),
                                'platform': 'Naukri',
                                'salary': salary,
                                'experience': experience,
                                'description': job_data.get('jobDescription', '')[:300] + '...',
                                'posted_date': job_data.get('createdDate', '')
                            }
                            
                            jobs.append(job)
                    
                    # Delay to avoid rate limiting
                    await asyncio.sleep(2)
                    
        except Exception as e:
            print(f"Error searching Naukri: {e}")
        
        return jobs
    
    def extract_salary_min(self, salary_text):
        """Extract minimum salary from text"""
        if not salary_text:
            return None
        
        # Patterns like "4-6 LPA", "4 LPA", "₹4,00,000 - ₹6,00,000"
        patterns = [
            r'(\d+)\s*-\s*\d+\s*LPA',  # 4-6 LPA
            r'(\d+)\s*LPA',  # 4 LPA
            r'₹\s*([\d,]+)\s*-\s*₹',  # ₹4,00,000 - ₹6,00,000
        ]
        
        for pattern in patterns:
            match = re.search(pattern, salary_text, re.IGNORECASE)
            if match:
                try:
                    salary = match.group(1).replace(',', '')
                    return int(salary)
                except:
                    continue
        
        return None
    
    def search_linkedin_with_filters(self):
        """LinkedIn search with your filters"""
        jobs = []
        try:
            queries = generate_search_queries()
            
            for query in queries[:10]:  # Limit to first 10 queries
                url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
                params = {
                    'keywords': query,
                    'location': 'India',
                    'f_E': '1,2',  # Entry level and internship
                    'f_WT': '2',  # Remote
                    'start': 0
                }
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(url, params=params, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    job_cards = soup.find_all('div', class_='base-card')
                    
                    for card in job_cards:
                        try:
                            title_elem = card.find('h3', class_='base-search-card__title')
                            company_elem = card.find('h4', class_='base-search-card__subtitle')
                            location_elem = card.find('span', class_='job-search-card__location')
                            link_elem = card.find('a', class_='base-card__full-link')
                            
                            if all([title_elem, company_elem, link_elem]):
                                job = {
                                    'title': title_elem.text.strip(),
                                    'company': company_elem.text.strip(),
                                    'location': location_elem.text.strip() if location_elem else 'India',
                                    'link': link_elem.get('href'),
                                    'platform': 'LinkedIn',
                                    'description': 'LinkedIn job posting'
                                }
                                
                                # Check if it's from target company
                                company_lower = job['company'].lower()
                                if any(target.lower() in company_lower for target in TARGET_COMPANIES):
                                    jobs.append(job)
                                else:
                                    # Check other criteria
                                    matches, reason = self.check_criteria_match(job)
                                    if matches:
                                        jobs.append(job)
                                        
                        except Exception as e:
                            continue
                
                # Respectful delay
                await asyncio.sleep(3)
                
        except Exception as e:
            print(f"Error searching LinkedIn: {e}")
        
        return jobs
    
    def format_enhanced_message(self, job, match_reason=""):
        """Format job alert with more details"""
        emoji_map = {
            'LinkedIn': '💼',
            'Naukri': '📊',
            'Indeed': '🔍',
            'GitHub Jobs': '🐙'
        }
        
        platform_emoji = emoji_map.get(job['platform'], '📨')
        
        message = f"""
{platform_emoji} *NEW JOB ALERT!*

*Position:* {job['title']}
*Company:* {job['company']}
*Location:* {job['location']}
*Platform:* {job['platform']}

"""
        
        # Add salary if available
        if job.get('salary'):
            message += f"*Salary:* {job['salary']}\n"
        
        # Add experience if available
        if job.get('experience'):
            message += f"*Experience:* {job['experience']}\n"
        
        # Add match reason
        if match_reason:
            message += f"*Match:* {match_reason}\n"
        
        message += f"""
[🔗 Apply Here]({job['link']})

⏰ *Posted:* {datetime.now().strftime('%Y-%m-%d %H:%M IST')}
📧 *Your email:* {self.email}
"""
        
        return message.strip()
    
    async def send_enhanced_alert(self, job, match_reason=""):
        """Send enhanced alert to Telegram"""
        if not self.bot:
            print("Telegram bot not configured")
            return False
            
        try:
            message = self.format_enhanced_message(job, match_reason)
            
            # Send with better formatting
            await self.bot.send_message(
                chat_id=os.environ.get('TELEGRAM_CHAT_ID'),
                text=message,
                parse_mode='Markdown',
                disable_web_page_preview=False,
                disable_notification=False
            )
            
            print(f"✅ Alert sent: {job['title']} at {job['company']}")
            return True
            
        except TelegramError as e:
            print(f"❌ Telegram error: {e}")
            return False
    
    async def run_enhanced_search(self):
        """Main search function with your criteria"""
        print("=" * 60)
        print("🔍 ENHANCED JOB ALERT BOT - SYED AMEEN AHMED")
        print("=" * 60)
        print(f"📧 Notification email: {self.email}")
        print(f"📍 Locations: {', '.join(PREFERRED_LOCATIONS)}")
        print(f"🏢 Target companies: {len(TARGET_COMPANIES)} companies")
        print(f"💼 Experience: 0 years (Fresher)")
        print(f"💰 Expected salary: 4 LPA+")
        print("=" * 60)
        
        all_jobs = []
        
        print("\n1. Searching Naukri with your criteria...")
        naukri_jobs = await self.search_naukri_enhanced()
        print(f"   Found {len(naukri_jobs)} jobs on Naukri")
        all_jobs.extend(naukri_jobs)
        
        print("\n2. Searching LinkedIn with filters...")
        linkedin_jobs = await self.search_linkedin_with_filters()
        print(f"   Found {len(linkedin_jobs)} jobs on LinkedIn")
        all_jobs.extend(linkedin_jobs)
        
        print(f"\n📊 Total jobs found: {len(all_jobs)}")
        
        # Filter and send alerts
        new_jobs = []
        for job in all_jobs:
            job_id = self.generate_job_id(job)
            
            # Skip if already seen
            if job_id in self.seen_jobs:
                continue
            
            # Check criteria match
            matches, reason = self.check_criteria_match(job)
            
            if matches:
                # Send alert
                success = await self.send_enhanced_alert(job, reason)
                if success:
                    self.seen_jobs.add(job_id)
                    new_jobs.append(job)
                    print(f"   ✅ New match: {job['title'][:40]}... ({reason})")
            
            # Small delay between sends
            await asyncio.sleep(1)
        
        # Save history
        self.save_history()
        
        print("\n" + "=" * 60)
        print(f"🎯 SEARCH COMPLETE")
        print(f"   New alerts sent: {len(new_jobs)}")
        print(f"   Total jobs in history: {len(self.seen_jobs)}")
        print("=" * 60)
        
        # Return summary for GitHub Actions
        return {
            'total_found': len(all_jobs),
            'new_alerts': len(new_jobs),
            'jobs': new_jobs[:5]  # First 5 new jobs
        }

async def main():
    """Main function"""
    # Check for credentials
    if not os.environ.get('TELEGRAM_BOT_TOKEN'):
        print("⚠️ WARNING: TELEGRAM_BOT_TOKEN not set")
        print("Set it in GitHub Secrets or environment variables")
    
    if not os.environ.get('TELEGRAM_CHAT_ID'):
        print("⚠️ WARNING: TELEGRAM_CHAT_ID not set")
    
    # Initialize bot
    alert_bot = EnhancedJobAlert()
    
    # Run search
    results = await alert_bot.run_enhanced_search()
    
    # Output for GitHub Actions
    print(f"::set-output name=new_jobs::{results['new_alerts']}")
    print(f"::set-output name=total_found::{results['total_found']}")
    
    # Save results to file for GitHub Pages if needed
    with open('search_results.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
