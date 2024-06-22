import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the environment (defaulting to 'development' if not set)
ENV = os.getenv('ENV', 'development')

if ENV == 'production':
    AIRTABLE_API_KEY = os.getenv('PROD_AIRTABLE_API_KEY')
    BASE_ID = os.getenv('PROD_BASE_ID')
    TABLE_ID_CANDIDATES = os.getenv('PROD_TABLE_ID_CANDIDATES')
    TABLE_ID_JOBS = os.getenv('PROD_TABLE_ID_JOBS')
else:
    AIRTABLE_API_KEY = os.getenv('DEV_AIRTABLE_API_KEY')
    BASE_ID = os.getenv('DEV_BASE_ID')
    TABLE_ID_CANDIDATES = os.getenv('DEV_TABLE_ID_CANDIDATES')
    TABLE_ID_JOBS = os.getenv('DEV_TABLE_ID_JOBS')
