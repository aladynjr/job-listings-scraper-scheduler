import datetime
from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import os
from termcolor import colored

URL = "https://upgraded.se/lediga-uppdrag/"

def get_current_path():
    path = os.path.dirname(os.path.abspath(__file__))
    return path

def filter_new_jobs_from_csv(links):
    unmatched = []
    path = os.path.join(get_current_path(), "..", "data")
    csv_file_path = os.path.join(path, "site_1_scraped_data.csv")

    if os.path.exists(csv_file_path):
        df_old = pd.read_csv(csv_file_path)
        print(colored(f"Loaded {len(df_old)} links from existing CSV", 'blue'))
        df_old = df_old["Link"].tolist()
    else:
        df_old = []
        print(colored("No existing CSV found. All links are new.", 'yellow'))
    
    for job in links:
        if job['Link'] not in df_old:
            unmatched.append(job)
    print(colored(f"Found {len(unmatched)} new job links", 'green'))
    return unmatched

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--log-level=3')
    driver = wd.Chrome(options=options)
    return driver

def get_job_data(driver):
    driver.get(URL)
    print(colored(f"Opening URL: {URL}", 'cyan'))
    driver.implicitly_wait(5)
    try:
        driver.find_element(By.XPATH, '//*[@id="popmake-4241"]/button').click()
    except:
        pass

    tbody = driver.find_element(By.XPATH, '//*[@id="container-async"]/div[2]/table/tbody')
    trs = tbody.find_elements(By.TAG_NAME, "tr")

    data = []
    for tr in trs:
        row = [item for item in tr.find_elements(By.TAG_NAME, "td")]
        if len(row) == 0:
            continue
        row_data = {
            "Job_Name": row[0].text,
            "Link": row[0].find_element(By.TAG_NAME, "a").get_attribute("href"),
            "Job_Location": row[1].text,
            "Dead_Line": row[-1].text,
            "Description": row[-1].text,
        }
        data.append(row_data)
    print(colored(f"Fetched {len(data)} job listings", 'cyan'))
    return data

def scrape_site_1_data():
    print("\n##################################################")
    print(colored(f"######## Starting scrape for site 1 at {datetime.datetime.now()} ########", "magenta"))
    print("##################################################\n")
    driver = get_driver()
    all_job_data = get_job_data(driver)
    new_job_data = filter_new_jobs_from_csv(all_job_data)

    driver.quit()
    return new_job_data
