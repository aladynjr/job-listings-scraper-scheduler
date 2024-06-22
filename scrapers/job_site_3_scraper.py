import datetime
from selenium import webdriver as wd
from selenium.webdriver.common.by import By
import pandas as pd
from selenium.webdriver.chrome.options import Options
import os
import re
from termcolor import colored

def get_current_path():
    path = os.path.dirname(os.path.abspath(__file__))
    print(colored(f"Current path: {path}", 'blue'))
    return path

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = wd.Chrome(options=options)
    #print(colored("Chrome driver initialized", 'green'))
    return driver

def new_links(job_data):
    new_jobs = []
    path = os.path.join(get_current_path(), "..", "data")
    csv_file_path = os.path.join(path, "site_3_scraped_data.csv")
    if os.path.exists(csv_file_path):
        df_old = pd.read_csv(csv_file_path)
        print(colored(f"Loaded {len(df_old)} links from existing CSV", 'blue'))
        df_old = df_old["Link"].tolist()
    else:
        df_old = []
        print(colored("No existing CSV found. All links are new.", 'yellow'))
    
    for job in job_data:
        if job['Link'] not in df_old:
            new_jobs.append(job)
    print(colored(f"Found {len(new_jobs)} new job links", 'yellow'))
    return new_jobs

def parse_location(text):
    if "Location:" in text:
        location = text.split("Location:")[1].split("\n")[0].strip()
    else:
        location = 'remote'
    print(colored(f"Location parsed: {location}", 'blue'))
    return location

def scrape_site_3_data():
    print("\n##################################################")
    print(colored(f"######## Starting scrape for site 3 at {datetime.datetime.now()} ########", "green"))
    print("##################################################\n")
    driver = get_driver()
    url = 'https://www.nikita.se/ramavtal/'
    print(colored(f"Opening URL: {url}", 'blue'))
    driver.get(url)
    driver.implicitly_wait(2)

    filler = '#' * 8
    print(colored(f"{filler} running site 3 time : {datetime.datetime.today()} {filler}", 'magenta'))

    try:
        get_all_links = driver.find_elements(By.XPATH, '//*[@id="ramavtal-target"]/ul/li/a')
        links_to_jobs = [i.get_attribute("href") for i in get_all_links]
        print(colored(f"Fetched {len(links_to_jobs)} links", 'blue'))
    except Exception as e:
        print(colored(f"Error fetching links: {e}", 'red'))
        driver.quit()
        return []

    try:
        get_job_name = driver.find_elements(By.XPATH, '//*[@id="ramavtal-target"]/ul/li/a/span[2]')
        job_name_list = [i.text for i in get_job_name]
        #print(colored(f"Fetched {len(job_name_list)} job names", 'blue'))
    except Exception as e:
        print(colored(f"Error fetching job names: {e}", 'red'))
        job_name_list = ["Unknown"] * len(links_to_jobs)

    all_job_data = []
    for link, job_name in zip(links_to_jobs, job_name_list):
        job_data = {
            "Job_Name": job_name,
            "Link": link,
            "Job_Location": "",
            "Description": "",
            "Dead_Line": ""  # We'll set a default later if not found
        }
        all_job_data.append(job_data)

    new_jobs = new_links(all_job_data)

    for job in new_jobs:
        print(colored(f"Opening link: {job['Link']}", 'blue'))
        driver.get(job['Link'])
        driver.implicitly_wait(2)
        try:
            find_paragraph = driver.find_element(By.XPATH, '/html/body/div[1]/div/section/div[2]/div[1]')
        except:
            try:
                find_paragraph = driver.find_element(By.XPATH, '/html/body/div[2]/div/section/div[2]/div[1]')
            except Exception as e:
                print(colored(f"Error fetching paragraph for link {job['Link']}: {e}", 'red'))
                find_paragraph = None
        if find_paragraph:
            job['Description'] = find_paragraph.text
            job['Job_Location'] = parse_location(job['Description'])
            #print(colored(f"Fetched paragraph and parsed location for link: {job['Link']}", 'blue'))

    driver.quit()
    #print(colored("Chrome driver quit", 'green'))
    return new_jobs