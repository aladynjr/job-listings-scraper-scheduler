import datetime
from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from termcolor import colored

def get_driver():
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = wd.Chrome(options=options)
    return driver

def parse_date(date_str):
    input_date = datetime.datetime.strptime(date_str, "%b %d, %Y")
    return input_date.strftime("%Y-%m-%d")

def scrape_site_5_data():
    print("\n##################################################")
    print(colored(f"######## Starting scrape for site 5 at {datetime.datetime.now()} ########", "green"))
    print("##################################################\n")

    driver = get_driver()
    url = "https://cinode.market/requests"
    print(colored(f"Opening URL: {url}", 'blue'))
    driver.get(url)
    driver.maximize_window()

    try:
        cookies_reject = driver.find_element(By.XPATH, '//button[contains(text(),"Reject")]').click()
    except:
        pass

    print(colored("Getting job names and links", 'blue'))
    get_name = driver.find_elements(By.XPATH, '/html/body/app-root/app-page-layout/app-requests-list-page/app-content/app-list/app-list-row/app-list-column[1]/a')
    get_company = driver.find_elements(By.XPATH, "/html/body/app-root/app-page-layout/app-requests-list-page/app-content/app-list/app-list-row/app-list-column[2]/p")
    get_deadline = driver.find_elements(By.XPATH, '/html/body/app-root/app-page-layout/app-requests-list-page/app-content/app-list/app-list-row/app-list-column[4]/p')

    all_job_data = []
    for name, company, deadline in zip(get_name, get_company, get_deadline):
        job_data = {
            "Job_Name": name.text,
            "Link": name.get_attribute("href"),
            "Company": company.text,
            "Dead_Line": parse_date(deadline.text),
            "Job_Location": "",
            "Description": ""
        }
        if job_data["Company"] in ["Nexer Group", 
                           #"Forefront Consulting Group AB", 
                           #"Softronic", 
                           #"CAG Group"
                          ]:
            all_job_data.append(job_data)

    print(colored(f"Fetched {len(all_job_data)} relevant job listings", 'blue'))

    for job in all_job_data:
        print(colored(f"Opening link: {job['Link']}", 'blue'))
        driver.get(job['Link'])
        driver.implicitly_wait(5)
        try:
            location_element = driver.find_element(By.XPATH, '/html/body/app-root/app-page-layout/app-request-page/app-content/div[2]/aside/app-request-details/div/section[2]/div[4]/p[2]')
            job['Job_Location'] = "remote" if location_element.text == "No location set" else location_element.text.split(",")[0]
        except Exception as e:
            print(colored(f"Error fetching location for link {job['Link']}: {e}", 'red'))
            job['Job_Location'] = "Unknown"

    driver.quit()
    print(colored("Chrome driver quit", 'green'))
    return all_job_data

