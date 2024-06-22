import time
import schedule
from tasks.update_expired_jobs_status import update_expired_jobs_status
from tasks.scrape_all_sites_task import scrape_all_sites_task, test_everything

from termcolor import colored
import pandas as pd
import datetime
import os
import traceback
from dotenv import load_dotenv
os.system('color')

load_dotenv()

ENV = os.getenv('ENV', 'development')

def main():
    current_time = datetime.datetime.now()
    print(colored(f"######## STARTING, Current Time and Date: {current_time} ########", 'cyan'))
    
    if ENV == 'development':
        test_everything()
        return
    
    try:
        # Schedule scrapers
        for hour in range(7, 18):
            schedule.every().monday.at(f"{hour:02d}:00").do(scrape_all_sites_task)
            schedule.every().tuesday.at(f"{hour:02d}:00").do(scrape_all_sites_task)
            schedule.every().wednesday.at(f"{hour:02d}:00").do(scrape_all_sites_task)
            schedule.every().thursday.at(f"{hour:02d}:00").do(scrape_all_sites_task)
            schedule.every().friday.at(f"{hour:02d}:00").do(scrape_all_sites_task)
            schedule.every().saturday.at(f"{hour:02d}:00").do(scrape_all_sites_task)
            schedule.every().sunday.at(f"{hour:02d}:00").do(scrape_all_sites_task)
                
        # Schedule update expired jobs status
        schedule.every().day.at("08:20").do(update_expired_jobs_status)
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                print(colored(f"Error in the scheduled task loop: {e}", 'red'))
                print(traceback.format_exc())
                time.sleep(10)  # Wait before retrying

    except Exception as e:
        print(colored(f"Fatal error in main loop: {e}", 'red'))
        print(traceback.format_exc())

if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print(colored(f"Restarting main loop due to error: {e}", 'red'))
            print(traceback.format_exc())
            time.sleep(10)  # Wait before restarting
