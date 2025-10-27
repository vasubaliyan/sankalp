import os
import sys
import django
import requests
import time
from datetime import datetime
from django.db import transaction
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# ✅ Setup Django environment
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Sankalp.settings")
django.setup()

from Dashboard.models import Project2Record, ProjectFetchLog

# 🔹 REDCap Config for Project 2
API_TOKEN = "5D139489F36A6883E108BA772FBA991A"
API_URL = "https://nhrp-rdp.icmr.org.in/api/"
MAX_RETRIES = 3
RETRY_DELAY = 5
BATCH_SIZE = 1000  # Optimal batch size


# ----------------------------------------------------------
def broadcast_dashboard_update(message="Data updated"):
    """Send live update message to all connected dashboards via WebSocket"""
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "dashboard_updates",
            {"type": "send_dashboard_update", "message": message},
        )
        print("📡 Dashboard update broadcast sent.")
    except Exception as e:
        print(f"⚠️ Failed to broadcast dashboard update: {e}")


# ----------------------------------------------------------
def get_all_record_ids():
    """Fetch all unique record IDs from REDCap"""
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
            r = requests.post(API_URL, data=payload, timeout=(30, 600))
            r.raise_for_status()
            data = r.json()
            return list(set([rec["record_id"] for rec in data]))
        except Exception as e:
            print(f"❌ Attempt {attempt + 1} failed: {e}")
            time.sleep(RETRY_DELAY)
    return []


# ----------------------------------------------------------
def fetch_and_save_project2():
    print("\n🔄 Fetching selected fields for Project 2...")

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
        "d29_baby_death_date_b1",
        "d29_baby_death_date_b2",
        "d29_baby_death_date_b3",
        "d29_baby_death_place_b1",
        "d29_baby_death_place_b2",
        "d29_baby_death_place_b3",
        # death cause fields
        "q17_cause_of_death_d29_b1___1", "q17_cause_of_death_d29_b1___2",
        "q17_cause_of_death_d29_b1___3", "q17_cause_of_death_d29_b1___4",
        "q17_cause_of_death_d29_b1___5", "q17_cause_of_death_d29_b1___6",
        "q17_cause_of_death_d29_b1___7", "q17_cause_of_death_d29_b1___8",
        "q17_cause_of_death_d29_b1___9", "q17_cause_of_death_d29_b1___10",
        "q17_cause_of_death_d29_b2___1", "q17_cause_of_death_d29_b2___2",
        "q17_cause_of_death_d29_b2___3", "q17_cause_of_death_d29_b2___4",
        "q17_cause_of_death_d29_b2___5", "q17_cause_of_death_d29_b2___6",
        "q17_cause_of_death_d29_b2___7", "q17_cause_of_death_d29_b2___8",
        "q17_cause_of_death_d29_b2___9", "q17_cause_of_death_d29_b2___10",
        "q17_cause_of_death_d29_b3___1", "q17_cause_of_death_d29_b3___2",
        "q17_cause_of_death_d29_b3___3", "q17_cause_of_death_d29_b3___4",
        "q17_cause_of_death_d29_b3___5", "q17_cause_of_death_d29_b3___6",
        "q17_cause_of_death_d29_b3___7", "q17_cause_of_death_d29_b3___8",
        "q17_cause_of_death_d29_b3___9", "q17_cause_of_death_d29_b3___10",
        # extra fields
        "estimated_date_of_delivery",
        "gestation_age",
        "q40_if_available_estimated_ga_through_ultrasound_before_20_weeks_in_weeks",
    ]

    model_fields = {f.name for f in Project2Record._meta.get_fields() if f.name != "id"}
    num_batches = (total_records + BATCH_SIZE - 1) // BATCH_SIZE
    total_saved = 0

    for batch_num in range(num_batches):
        start, end = batch_num * BATCH_SIZE, min((batch_num + 1) * BATCH_SIZE, total_records)
        batch_ids = all_record_ids[start:end]
        print(f"\n📦 Batch {batch_num + 1}/{num_batches} → {len(batch_ids)} records")

        payload = {
            "token": API_TOKEN,
            "content": "record",
            "format": "json",
            "type": "flat",
            "rawOrLabel": "label",
            "exportDataAccessGroups": "true",
            "returnFormat": "json",
        }

        # Correct REDCap array format
        for idx, record_id in enumerate(batch_ids):
            payload[f"records[{idx}]"] = record_id
        for idx, field in enumerate(FIELDS_TO_FETCH):
            payload[f"fields[{idx}]"] = field

        for attempt in range(MAX_RETRIES):
            try:
                api_start = time.time()
                r = requests.post(API_URL, data=payload, timeout=(30, 600))

                # Debugging info for non-200 response
                if r.status_code != 200:
                    print(f"❌ REDCap error response ({r.status_code}): {r.text}")

                r.raise_for_status()
                data = r.json()
                print(f"⏱️ API Fetch time: {time.time() - api_start:.2f}s, Records: {len(data)}")

                if not data:
                    print("⚠️ Empty batch, skipping...")
                    break

                record_ids = [item.get("record_id") for item in data if item.get("record_id")]
                existing_ids = set(
                    Project2Record.objects.filter(record_id__in=record_ids)
                    .values_list("record_id", flat=True)
                )

                new_objs, update_data = [], []

                for item in data:
                    record_id = item.get("record_id")
                    if not record_id:
                        continue

                    clean_item = {
                        k: (v if v != "" else None)
                        for k, v in item.items()
                        if k in model_fields
                    }
                    clean_item["data_access_group"] = item.get("redcap_data_access_group")

                    if record_id in existing_ids:
                        update_data.append((record_id, clean_item))
                    else:
                        new_objs.append(Project2Record(**clean_item))

                db_start = time.time()
                with transaction.atomic():
                    if new_objs:
                        Project2Record.objects.bulk_create(new_objs, ignore_conflicts=True)
                    for record_id, fields_to_update in update_data:
                        Project2Record.objects.filter(record_id=record_id).update(**fields_to_update)

                batch_saved = len(new_objs) + len(update_data)
                total_saved += batch_saved
                print(f"💾 DB Save time: {time.time() - db_start:.2f}s → Saved {batch_saved} records")

                time.sleep(1.5)
                break

            except Exception as e:
                print(f"⚠️ Retry {attempt + 1} failed: {e}")
                wait = RETRY_DELAY * (2 ** attempt)
                print(f"⏳ Waiting {wait}s before retry...")
                time.sleep(wait)

    ProjectFetchLog.objects.update_or_create(
        project_name="project2",
        defaults={"last_fetch_time": datetime.now()},
    )

    broadcast_dashboard_update("Project2 data updated")
    print(f"\n✅ Done! Total records saved/updated: {total_saved}")


# ----------------------------------------------------------
if __name__ == "__main__":
    fetch_and_save_project2()
