from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime
import time
import re
import pandas as pd
from selenium.webdriver.chrome.options import Options
import os
from termcolor import colored

HASH_STR = "#" * 20

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = wd.Chrome(options=options)
    #print(colored("Chrome driver initialized", 'green'))
    return driver

def login(driver, mail, password):
    driver.maximize_window()
    print(colored(f'Attempting to login at {datetime.now()}', 'magenta'))
    
    try:
        # Reject cookies if the button is present
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"Reject")]'))).click()
        except TimeoutException:
            print(colored("No 'Reject' button found. Continuing with login.", 'yellow'))

        # First email input
        first_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Email address']")))
        first_input.send_keys(mail)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[@id="login-next-button"]'))).click()

        # Second email input
        second_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@type='email']")))
        second_input.send_keys(mail)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//input[@id="idSIButton9"]'))).click()

        time.sleep(2)  # Wait for password input to load

        # Password input
        input_password = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@name="passwd"]')))
        input_password.send_keys(password)
        
        time.sleep(5)  # Wait before final sign-in click

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="idSIButton9"]'))).click()

        # Handle "Stay signed in" prompt if it appears
        try:
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="acceptButton"]'))).click()
        except TimeoutException:
            print(colored("No 'Stay signed in' prompt found. Continuing.", 'yellow'))

        # Handle "End tour" button if it appears
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="End tour"]'))).click()
        except TimeoutException:
            print(colored("No 'End tour' button found. Continuing.", 'yellow'))

        print(colored("Login process completed successfully", 'green'))

    except TimeoutException as e:
        print(colored(f"Timeout during login process: {str(e)}", 'red'))
        print(colored("The page structure might have changed or the site is responding slowly.", 'red'))
    except Exception as e:
        print(colored(f"An unexpected error occurred during login: {str(e)}", 'red'))




def get_new_links(driver):
    assignment_url = "https://portal.afry.com/en/AvailableAssignments?AssignmentFilter.SearchAssignment=&AssignmentFilter.NumberOfHits=100&AssignmentFilter.RemoteWorkOnly=false&AssignmentFilter.EnglishOnlyInfo=false"
    time.sleep(1)
    driver.get(assignment_url)
    time.sleep(3)
    get_all_links = driver.find_elements(By.XPATH, '//*[@id="legacy-main"]/div[1]/div[2]/div/div/div/table/tbody/tr/td[1]/a')
    links = [i.get_attribute("href") for i in get_all_links]
    print(colored(f"Fetched {len(links)} new links", 'blue'))
    return links

def get_job_data(driver, link):
    driver.get(link)
    driver.implicitly_wait(2)
    time.sleep(1)
    
    job_name = driver.find_element(By.XPATH, '//h1[@class="assignmentdetails__heading"]').text
    text = driver.find_element(By.XPATH, "//*[@id='assignmentInfo']/div/div[2]").text
    
    location_pattern = r"Location\n(.*?)\n"
    date_pattern = r"Last Day to Apply\n(.*?)\n"
    
    location_match = re.search(location_pattern, text)
    date_match = re.search(date_pattern, text)
    
    location = location_match.group(1).split('\\')[-1].strip() if location_match else "remote"
    deadline = date_match.group(1) if date_match else ""
    
    job_data = {
        "Job_Name": job_name,
        "Link": link,
        "Job_Location": location,
        "Dead_Line": deadline,
        "Description": ""
    }
    
    return job_data

def new_links(old_links, links):
    new_jobs = [new for new in links if new not in old_links]
    print(colored(f"Found {len(new_jobs)} new job links", 'yellow'))
    return new_jobs

def scrape_site_4_data():
    print("\n##################################################")
    print(colored(f"######## Starting scrape for site 4 at {datetime.now()} ########", "green"))
    print("##################################################\n")
    mail = "info@veritaz.se"
    password = "Pokemon1337"

    driver = get_driver()
    url = "https://portal.afry.com/login?ReturnUrl=%2F"
    driver.get(url)
    login(driver, mail, password)
    
    print("Reading old data")
    path = os.path.join(get_current_path(), "..", "data")
    csv_file_path = f"{path}/site_4_scraped_data.csv"
    if not os.path.exists(csv_file_path):
        print("No existing CSV found. All links are new.", 'yellow')
        old_links = []
    else:
        df = pd.read_csv(csv_file_path)
        old_links = df['Link'].tolist()
        print(f"Got {len(old_links)} old links", 'blue')
    
    links = get_new_links(driver)
    print(f"Got {len(links)} new links", 'blue')
    new_job_links = new_links(old_links, links)
    new_jobs_data = []
    for link in new_job_links:
        job_data = get_job_data(driver, link)
        new_jobs_data.append(job_data)
        print(f"Processed job: {job_data['Job_Name']}", 'blue')
    
    driver.quit()
    #print("Chrome driver quit", 'green')
    return new_jobs_data

def get_current_path():
    path = os.path.dirname(os.path.abspath(__file__))
    print(colored(f"Current path: {path}", 'blue'))
    return path

