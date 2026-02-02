import os

# Get secrets from environment
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# Your exact criteria from job alerts
JOB_CRITERIA = {
    'keywords': [
        'Data Analyst', 'Python', 'SQL', 'Pandas', 'NumPy', 
        'Power BI', 'Excel', 'Data Visualization', 'EDA', 
        'Data Cleaning', 'Dashboard', 'Reporting', 
        'Business Intelligence', 'KPI', 'Statistics', 
        'Analytics Intern', 'Junior Data Analyst'
    ],
    'experience': '0',  # 0 years
    'salary_min': 400000,  # 4 LPA
    'locations': [
        'Bangalore', 'Chennai', 'Hyderabad', 'Pune', 
        'Mumbai', 'Remote', 'India'
    ],
    'industries': [
        'Internet', 'Ecommerce', 'IT-Software', 
        'Software Services', 'KPO', 'Research', 'Analytics'
    ],
    'categories': [
        'Analytics & Business Intelligence',
        'IT Software - DBA, Datawarehousing',
        'IT Software - Systems, EDP, MIS'
    ],
    'roles': ['Data Analyst', 'Business Analyst']
}

# Target companies
TARGET_COMPANIES = [
    'Amazon', 'Microsoft', 'Google', 'Accenture',
    'TCS', 'Infosys', 'Wipro', 'Cognizant',
    'Capgemini', 'Deloitte', 'EY', 'KPMG', 'PwC'
]

# Platform-specific configurations
PLATFORMS = {
    'linkedin': {
        'url': 'https://www.linkedin.com/jobs/search/',
        'params_template': {
            'keywords': 'data analyst python',
            'location': 'India',
            'f_E': '1,2',  # Entry level
            'f_JT': 'F',  # Full-time
            'f_WT': '1,2,3',  # On-site, Remote, Hybrid
            'start': 0
        }
    },
    'naukri': {
        'url': 'https://www.naukri.com/jobapi/v3/search',
        'params_template': {
            'noOfResults': 20,
            'urlType': 'search_by_keyloc',
            'searchType': 'adv',
            'keyword': 'data analyst',
            'location': 'bangalore',
            'experience': '0',
            'salary': '400000',
            'jobAge': '1',
            'pageNo': 0
        }
    },
    'indeed': {
        'url': 'https://www.indeed.com/jobs',
        'params_template': {
            'q': 'data analyst',
            'l': 'bangalore',
            'jt': 'fulltime',
            'explvl': 'entry_level',
            'fromage': '1'
        }
    }
}

# Email for notifications (yours)
NOTIFICATION_EMAIL = 'ameenahmed16th@gmail.com'
