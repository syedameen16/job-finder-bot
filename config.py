import os

# Get secrets from environment (GitHub Secrets)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# Job Platforms
PLATFORMS = {
    'linkedin': 'https://www.linkedin.com/jobs/search/',
    'naukri': 'https://www.naukri.com/jobapi/v3/search',
    'indeed': 'https://www.indeed.com/jobs',
    'wellfound': 'https://angel.co/jobs',
    'instahyre': 'https://www.instahyre.com/'
}

# Search Parameters
LOCATIONS = ['Bangalore', 'Bengaluru', 'Hyderabad', 'Pune', 'Chennai', 'Remote', 'India']
JOB_TITLES = ['Data Analyst', 'Business Analyst', 'Data Engineer', 'Analytics', 'Power BI', 'SQL Analyst']
