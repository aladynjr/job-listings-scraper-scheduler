import datetime
from selenium import webdriver as wd
from selenium.webdriver.common.by import By
import re
import pandas as pd
from selenium.webdriver.chrome.options import Options
import os
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


def new_links(links, job_data):
    new_jobs = []
    path = os.path.join(get_current_path(), "..", "data")
    csv_file_path = os.path.join(path, "site_2_scraped_data.csv")
    if os.path.exists(csv_file_path):
        df_old = pd.read_csv(csv_file_path)
        print(colored(f"Loaded {len(df_old)} links from existing CSV", 'blue'))
        df_old = df_old["Link"].tolist()
    else:
        df_old = []
        print(colored("No existing CSV found. All links are new.", 'yellow'))
    
    for link, job in zip(links, job_data):
        if link not in df_old:
            new_jobs.append(job)
    print(colored(f"Found {len(new_jobs)} new job links", 'yellow'))
    return new_jobs



def parse_location(text):
    if "remote" in text.lower():
        return "remote"
    match = re.search(r'(Location|Ort\.?|Placement|Placering|Plats):?\s*(.*)', text)
    if match:
        location_text = match.group(2)
        cities = re.findall(r'\b[A-Za-zÀ-ÖØ-öø-ÿ]+(?: [A-Za-zÀ-ÖØ-öø-ÿ]+)?\b', location_text)
        return cities[0] if cities else "unknown"
    return "remote"

def scrape_site_2_data():
    print("\n##################################################")
    print(colored(f"######## Starting scrape for site 2 at {datetime.datetime.now()} ########", "magenta"))
    print("##################################################\n")
    driver = get_driver()
    url1 = "https://www.nikita.se/lediga-uppdrag/"
    print(colored(f"Opening URL: {url1}", 'blue'))
    driver.get(url1)
    driver.implicitly_wait(2)
    filler = '#' * 8
    print(colored(f"{filler} running site 2 time : {datetime.datetime.today()} {filler}", 'magenta'))

    try:
        get_all_links = driver.find_elements(By.XPATH, '//*[@id="open-positions-target"]/ul/li/a')
        links = [i.get_attribute("href") for i in get_all_links]
        print(colored(f"Fetched {len(links)} links", 'blue'))
    except Exception as e:
        print(colored(f"Error fetching links: {e}", 'red'))
        driver.quit()
        return []

    try:
        get_job_name = driver.find_elements(By.XPATH, '//*[@id="open-positions-target"]/ul/li/a/span[2]')
        job_names = [i.text for i in get_job_name]
        #print(colored(f"Fetched {len(job_names)} job names", 'blue'))
    except Exception as e:
        print(colored(f"Error fetching job names: {e}", 'red'))
        job_names = ["Unknown"] * len(links)

    all_job_data = []
    for link, job_name in zip(links, job_names):
        job_data = {
            "Job_Name": job_name,
            "Link": link,
            "Job_Location": "",
            "Description": "",
            "Dead_Line": ""  # We'll set a default later if not found
        }
        all_job_data.append(job_data)

    new_jobs = new_links(links, all_job_data)

    for job in new_jobs:
        print(colored(f"Opening link: {job['Link']}", 'blue'))
        driver.get(job['Link'])
        driver.implicitly_wait(2)
        try:
            find_paragraph = driver.find_element(By.XPATH, '/html/body/div[2]/div/section/div[2]/div[1]')
        except:
            try:
                find_paragraph = driver.find_element(By.XPATH, '/html/body/div[1]/div/section/div[2]/div[1]')
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

