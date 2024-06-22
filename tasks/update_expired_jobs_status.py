import requests
import datetime
import csv
from termcolor import colored
import config
import os

filter_condition = "Status = ''"
encoded_filter_condition = filter_condition.replace(" ", "%20")

headers = {'Authorization': f'Bearer {config.AIRTABLE_API_KEY}'}

url = f'https://api.airtable.com/v0/{config.BASE_ID}/{config.TABLE_ID_JOBS}?filterByFormula={encoded_filter_condition}'
def update_expired_jobs_status(update_airtable=True):
    print("\n##################################################")
    print(colored(f"######## Starting update_expired_jobs_status function at {datetime.datetime.now()} ########", "magenta"))
    print("##################################################\n")
    all_records = []

    def retrieve_records(url):
        response = requests.get(url, headers=headers)
        data = response.json()
        records = data.get('records', [])
        all_records.extend(records)
        print(colored(f'Retrieved {len(records)} records, total: {len(all_records)}', 'green'))
        offset = data.get('offset')
        if offset:
            next_url = url + f'?offset={offset}'
            retrieve_records(next_url)

    print(colored("Starting to retrieve records...", 'cyan'))
    retrieve_records(url)
    print(colored(f'Total records retrieved: {len(all_records)}', 'green'))

    updated_records = []
    report = []

    today = datetime.date.today()
    expired_count = 0
    non_expired_count = 0

    for record in all_records:
        record_id = record['id']
        fields = record['fields']
        expired_date = fields.get('expired date')
        status = fields.get('status')
        job_name = fields.get('Job name', 'Unknown Job')

        if status and expired_date:
            expired_date = datetime.datetime.strptime(expired_date, '%Y-%m-%d').date()
            if expired_date <= today and 'Expired' not in status:
                expired_count += 1
                updated_fields = {'status': ['Expired']}
                updated_records.append({'id': record_id, 'fields': updated_fields})
                report.append({'Record ID': record_id, 'Job Name': job_name})
                print(colored(f"Found expired job: {job_name} (ID: {record_id})", 'yellow'))
            else:
                non_expired_count += 1

    print(colored(f"Total jobs processed: {len(all_records)}", 'cyan'))
    print(colored(f"Expired jobs found: {expired_count}", 'yellow'))

    if update_airtable and updated_records:
        print(colored(f"\nUpdating {len(updated_records)} expired jobs in Airtable...", 'cyan'))
        batch_size = 10
        record_batches = [updated_records[i:i + batch_size] for i in range(0, len(updated_records), batch_size)]
        for i, batch in enumerate(record_batches, 1):
            batch_records = {'records': batch}
            update_url = f'https://api.airtable.com/v0/{config.BASE_ID}/{config.TABLE_ID_JOBS}'
            response = requests.patch(update_url, json=batch_records, headers=headers)
            if response.status_code == 200:
                print(colored(f'Batch {i}: Updated {len(batch)} records successfully', 'green'))
            else:
                print(colored(f'Batch {i}: Error updating records', 'red'))
                print(colored(f'Status code: {response.status_code}', 'red'))
                print(colored(f'Response content: {response.content}', 'red'))


    print(colored('\nNo expired jobs found to update', 'yellow'))