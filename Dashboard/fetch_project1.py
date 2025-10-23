import os
import sys
import django
import requests
import time
from datetime import datetime

# ✅ Setup Django environment
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Sankalp.settings")
django.setup()

from Dashboard.models import Project1Record, ProjectFetchLog

# 🔹 REDCap Config for Project 1
API_TOKEN = "7CD451E2003A0B8AC3B066ABAA6AAF47"
API_URL = "https://nhrp-rdp.icmr.org.in/api/"
MAX_RETRIES = 3
RETRY_DELAY = 5
BATCH_SIZE = 2000

# ----------------------------------------------------------
def get_all_record_ids():
    payload = {
        "token": API_TOKEN,
        "content": "record",
        "format": "json",
        "type": "flat",
        "fields[0]": "record_id",
        "returnFormat": "json",
    }
    for attempt in range(MAX_RETRIES):
        try:
            r = requests.post(API_URL, data=payload, timeout=(10, 600))
            r.raise_for_status()
            data = r.json()
            return list(set([rec["record_id"] for rec in data]))
        except Exception as e:
            print(f"❌ Attempt {attempt+1} failed: {e}")
            time.sleep(RETRY_DELAY)
    return []

# ----------------------------------------------------------
def fetch_and_save_project1():
    print("\n🔄 Fetching selected fields for Project 1...")

    all_record_ids = get_all_record_ids()
    if not all_record_ids:
        print("❌ No record IDs found.")
        return
    total_records = len(all_record_ids)
    print(f"📋 Total unique records to fetch: {total_records}")

    # ✅ Only fetch these fields
    FIELDS_TO_FETCH = [
        "record_id",
        "d29_baby_current_status_b1",
        "d29_baby_current_status_b2",
        "d29_baby_current_status_b3",
        "d29_call_status_b1",
        "d29_call_status_b2",
        "d29_call_status_b3",
    ]

    model_fields = {f.name for f in Project1Record._meta.get_fields() if f.name != "id"}
    saved_records = []
    num_batches = (total_records + BATCH_SIZE - 1) // BATCH_SIZE

    for batch_num in range(num_batches):
        start, end = batch_num * BATCH_SIZE, min((batch_num + 1) * BATCH_SIZE, total_records)
        batch_ids = all_record_ids[start:end]
        print(f"📦 Batch {batch_num + 1}/{num_batches} ({len(batch_ids)} records)")

        # ✅ Proper REDCap field formatting
        payload = {
            "token": API_TOKEN,
            "content": "record",
            "format": "json",
            "type": "flat",
            "rawOrLabel": "label",
            "exportDataAccessGroups": "true",
            "records": ",".join(batch_ids),
            "returnFormat": "json",
        }

        for idx, field in enumerate(FIELDS_TO_FETCH):
            payload[f"fields[{idx}]"] = field

        for attempt in range(MAX_RETRIES):
            try:
                r = requests.post(API_URL, data=payload, timeout=(10, 600))
                if r.status_code != 200:
                    print("❌ Response:", r.text[:200])
                r.raise_for_status()

                data = r.json()
                for item in data:
                    record_id = item.get("record_id")
                    if not record_id:
                        continue
                    clean_item = {k: (v if v != "" else None) for k, v in item.items() if k in model_fields}
                    clean_item["data_access_group"] = item.get("redcap_data_access_group")
                    Project1Record.objects.update_or_create(record_id=record_id, defaults=clean_item)
                    saved_records.append(record_id)

                print(f"✅ Batch {batch_num+1} fetched ({len(data)} records)")
                break

            except Exception as e:
                print(f"⚠️ Retry {attempt+1} failed: {e}")
                time.sleep(RETRY_DELAY)

    ProjectFetchLog.objects.update_or_create(
        project_name="project1",
        defaults={"last_fetch_time": datetime.now()},
    )

    print(f"✅ Done! Total records saved/updated: {len(saved_records)}")


if __name__ == "__main__":
    fetch_and_save_project1()
