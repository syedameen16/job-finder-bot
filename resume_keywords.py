# Resume Keywords for Syed Ameen Ahmed - Based on your job alert preferences
RESUME_KEYWORDS = {
    'primary': [
        'Data Analyst',
        'Python',
        'SQL',
        'Pandas',
        'NumPy',
        'Power BI',
        'Excel',
        'Data Visualization',
        'EDA',
        'Data Cleaning',
        'Dashboard',
        'Reporting',
        'Business Intelligence',
        'KPI',
        'Statistics',
        'Analytics Intern',
        'Junior Data Analyst'
    ],
    'secondary': [
        'MySQL',
        'Jupyter',
        'ETL',
        'Exploratory Data Analysis',
        'Analytics',
        'Machine Learning',
        'Matplotlib',
        'Seaborn',
        'DAX',
        'Data Warehousing',
        'MIS',
        'Business Analyst',
        'Data Engineer'
    ],
    'experience_keywords': [
        '0 years',
        'fresher',
        'entry level',
        'junior',
        'intern',
        'trainee'
    ]
}

# Your exact location preferences
PREFERRED_LOCATIONS = [
    'Bangalore',
    'Bengaluru',
    'Chennai',
    'Hyderabad',
    'Pune',
    'Mumbai',
    'Remote',
    'India'
]

# Target companies from your list
TARGET_COMPANIES = [
    'Amazon',
    'Microsoft',
    'Google',
    'Accenture',
    'TCS',
    'Infosys',
    'Wipro',
    'Cognizant',
    'Capgemini',
    'Deloitte',
    'EY',
    'KPMG',
    'PwC'
]

# Your industry preferences
PREFERRED_INDUSTRIES = [
    'Internet',
    'Ecommerce',
    'IT-Software',
    'Software Services',
    'KPO',
    'Research',
    'Analytics'
]

# Job categories from your alert
JOB_CATEGORIES = [
    'Analytics & Business Intelligence',
    'IT Software - DBA, Datawarehousing',
    'IT Software - Systems, EDP, MIS',
    'Data Analyst',
    'Business Analyst'
]

# Salary expectation (4 LPA)
EXPECTED_SALARY_MIN = 400000  # 4 LPA in rupees

# Generate search queries based on your criteria
def generate_search_queries():
    """Generate search queries for job platforms"""
    base_keywords = ['Data Analyst', 'Python', 'SQL', 'Power BI']
    experience_levels = ['fresher', 'entry level', 'junior', '0 years experience']
    
    queries = []
    
    # Create location-based queries
    for location in PREFERRED_LOCATIONS[:6]:  # Exclude 'India' and 'Remote' for location-specific
        for keyword in base_keywords:
            for exp in experience_levels:
                queries.append(f"{keyword} {exp} {location}")
    
    # Add remote-specific queries
    for keyword in base_keywords:
        for exp in experience_levels:
            queries.append(f"{keyword} {exp} remote")
    
    # Add company-specific queries
    for company in TARGET_COMPANIES:
        queries.append(f"{company} data analyst fresher")
    
    return queries

# Generate LinkedIn search filters
def generate_linkedin_filters():
    """Generate LinkedIn search filter parameters"""
    filters = {
        'keywords': 'Data Analyst OR Python Analyst OR SQL Analyst OR Power BI Developer',
        'location': 'India',
        'f_E': '1',  # Entry level (1: Internship, 2: Entry level)
        'f_JT': 'F',  # Job Type: Full-time
        'f_WT': '2',  # Work type: Remote (1: On-site, 2: Remote, 3: Hybrid)
        'f_C': ','.join([  # Company filters (if LinkedIn supports)
            '1441',  # Amazon
            '1035',  # Microsoft
            '1052',  # Google
            '3648',  # Accenture
            '1313',  # TCS
            '3125',  # Infosys
            '5860'   # Wipro
        ])
    }
    return filters

# Naukri specific search parameters
def generate_naukri_params():
    """Generate Naukri.com search parameters"""
    return {
        'jobAge': '1',  # Last 1 day
        'salary': '400000',  # 4 LPA
        'experience': '0',  # 0 years
        'loc': 'bangalore,chennai,hyderabad,pune,mumbai',
        'ind': 'internet,ecommerce,it-software,software-services,kpo,research,analytics'
    }
