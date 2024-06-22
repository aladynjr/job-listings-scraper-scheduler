from scrapers.job_site_1_scraper import scrape_site_1_data
from scrapers.job_site_2_scraper import scrape_site_2_data
from scrapers.job_site_3_scraper import scrape_site_3_data
from scrapers.job_site_4_scraper import scrape_site_4_data
from scrapers.job_site_5_scraper import scrape_site_5_data  
from utils.update_airtable_with_csv import update_airtable_with_csv
from termcolor import colored
import pandas as pd
import datetime
import os
from tasks.update_expired_jobs_status import update_expired_jobs_status

MAIN_PATH = os.path.dirname(os.path.abspath(__file__))+'/../'

def process_data(jobs_data, site, update_airtable=True):
    if not jobs_data:
        print(colored(f"NO JOBS DATA TO PROCESS FOR SITE {site}. EXITING FUNCTION.", 'yellow'))
        return

    today = datetime.date.today()
    print(colored(f"Processing data for site {site} with {len(jobs_data)} new jobs", 'cyan'))
    
    job_names = []
    new_jobs_links = []
    locations = []
    deadlines = []
    descriptions = []

    for job in jobs_data:
        job_names.append(job['Job_Name'])
        new_jobs_links.append(job['Link'])
        locations.append(job['Job_Location'])
        
        try:
            deadline = datetime.datetime.strptime(job['Dead_Line'], '%Y-%m-%d').date()
        except ValueError:
            deadline = today + datetime.timedelta(days=14)
            print(colored(f"Invalid deadline format for job {job['Job_Name']}, setting default to 14 days from today: {deadline}", 'yellow'))
        deadlines.append(deadline)
        
        descriptions.append(job.get('Description', ''))

    df = pd.DataFrame({
        "Job_Name": job_names,
        "Link": new_jobs_links,
        "Job_Location": locations, 
        "Dead_Line": deadlines,
        "status": '',
        "Description": descriptions
    })

    csv_file_path = f"{MAIN_PATH}/data/site_{site}_scraped_data.csv"
    
    if not os.path.exists(csv_file_path):
        print(colored(f"Creating a new CSV file for site {site} with headers", 'cyan'))
        df.to_csv(csv_file_path, mode='w', index=False)
    else:
        print(colored(f"Appending data to existing CSV file for site {site}", 'cyan'))
        df.to_csv(csv_file_path, mode='a', index=False, header=False)

    print(colored(f"Saving data to {MAIN_PATH}/data/site_{site}_new_jobs.csv", 'cyan'))
    df.to_csv(f"{MAIN_PATH}/data/site_{site}_new_jobs.csv", mode='w', index=False)

    if update_airtable:
        print(colored(f"Updating Airtable with data from site_{site}_new_jobs.csv", 'cyan'))
        update_airtable_with_csv(filename=f"site_{site}_new_jobs.csv")

    print(colored(f"Data processing for site {site} completed", 'green'))

def scrape_all_sites_task(update_airtable=True):
    site1_new_jobs = scrape_site_1_data() 
    process_data(site1_new_jobs, site=1, update_airtable=update_airtable)

    site2_new_jobs = scrape_site_2_data()
    process_data(site2_new_jobs, site=2, update_airtable=update_airtable)

    site3_new_jobs = scrape_site_3_data()
    process_data(site3_new_jobs, site=3, update_airtable=update_airtable)

    site4_new_jobs = scrape_site_4_data()
    process_data(site4_new_jobs, site=4, update_airtable=update_airtable)

    site5_new_jobs = scrape_site_5_data()  
    process_data(site5_new_jobs, site=5, update_airtable=update_airtable) 

def test_everything():
    print(colored("######## Testing all functions ########", "magenta"))

    update_expired_jobs_status(update_airtable=True)

    site1_new_jobs = scrape_site_1_data()
    process_data(site1_new_jobs, site=1, update_airtable=True)

    site2_new_jobs = scrape_site_2_data()
    process_data(site2_new_jobs, site=2, update_airtable=True)

    site5_new_jobs = scrape_site_5_data()  
    process_data(site5_new_jobs, site=5, update_airtable=False)  

    site3_new_jobs = scrape_site_3_data()
    process_data(site3_new_jobs, site=3, update_airtable=True)

    site5_new_jobs = scrape_site_4_data()
    process_data(site5_new_jobs, site=4, update_airtable=True)    

    return 
