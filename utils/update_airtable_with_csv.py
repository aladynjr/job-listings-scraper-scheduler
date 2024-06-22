import requests
import csv
import config
from termcolor import colored
import time

def fetch_existing_records(url, headers):
    existing_records = []
    offset = None
    limit = 1000

    sorted_url = f"{url}?sort%5B0%5D%5Bfield%5D=Created By&sort%5B0%5D%5Bdirection%5D=desc&maxRecords={limit}"

    while True:
        params = {}
        if offset:
            params['offset'] = offset

        response = requests.get(sorted_url, headers=headers, params=params)
        if response.status_code != 200:
            print(colored(f"Error fetching existing records: {response.status_code}", 'red'))
            print(colored(f"Response content: {response.content}", 'red'))
            break

        data = response.json()
        records = data.get('records', [])
        existing_records.extend(records)

        if len(existing_records) >= limit or not data.get('offset'):
            break

        offset = data.get('offset')

    print(colored(f"Total records fetched to check for duplicates: {len(existing_records)}. These records will be used to avoid adding duplicate entries.", 'cyan'))
    return existing_records

def update_airtable_with_csv(filename, table_name=config.TABLE_ID_JOBS):
    url = f'https://api.airtable.com/v0/{config.BASE_ID}/{table_name}'
    headers = {
        'Authorization': f'Bearer {config.AIRTABLE_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    existing_records = fetch_existing_records(url, headers)
    
    existing_jobs = set()
    for record in existing_records:
        job_name = record['fields'].get('Job name')
        link = record['fields'].get('Link')
        if job_name and link:
            existing_jobs.add((job_name, link))
    
    with open(f'data/{filename}', 'r', encoding='utf-8', errors='ignore') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        data = [row for row in csv_reader]
    
    records = []
    duplicate_count = 0
    for row in data:
        job_name = row.get('Job_Name')
        link = row.get('Link')
        if job_name and link and (job_name, link) not in existing_jobs:
            record = {
                'fields': {
                    'Job name': job_name,
                    'Link': link,
                    'Location': row.get('Job_Location', ''),
                    'expired date': row.get('Dead_Line', ''),
                    'Description': ''
                }
            }
            if 'Client' in row:
                record['fields']['Client'] = row['Client']
            records.append(record)
        else:
            duplicate_count += 1

    print(colored(f"Number of existing records found in Airtable: {duplicate_count}", 'yellow'))
    batch_size = 10
    total_batches = len(records) // batch_size + (1 if len(records) % batch_size > 0 else 0)
    print(colored(f"Total records to process: {len(records)}", 'cyan'))

    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        print(colored(f"Processing batch {i//batch_size + 1} of {total_batches} with {len(batch)} records", 'cyan'))
        
        response = requests.post(url, headers=headers, json={
            'records': batch,
            'typecast': True
        })
        
        print(colored(f"Batch {i//batch_size + 1} status code: {response.status_code}", 'green'))

    print(colored(f"Total records processed: {len(records)}", 'green'))
