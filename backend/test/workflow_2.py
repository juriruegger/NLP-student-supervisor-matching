import pandas as pd
import os
from dotenv import load_dotenv
import requests
from supabase import create_client, Client
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

load_dotenv("backend/.env.local")

url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
PURE_API_KEY = os.environ.get("PURE_API_KEY")
PURE_BASE_URL = os.environ.get("PURE_BASE_URL")

supabase: Client = create_client(url, key)

# Fetching supervisors from the database
BATCH_SIZE = 50
offset = 0
supervisors_db = []

while True:
    response = (
        supabase.table("supervisor")
        .select("*")
        .range(offset, offset + BATCH_SIZE - 1)
        .execute()
    )
    batch = response.data or []
    if not batch:
        break

    supervisors_db.extend(batch)
    offset += BATCH_SIZE

print(f"Fetched total rows: {len(supervisors_db)}")

response = (
    supabase.table("supervisor_topic")
    .select("*")
    .execute()
)
supervisors_db_topics = response.data

response = (
    supabase.table("topic")
    .select("*")
    .execute()
)
topics_db = response.data

# Fetching researchers from PURE
person_url = f"{PURE_BASE_URL}/persons"
person_headers = {
    "accept": "application/json", 
    "api-key": PURE_API_KEY,
}
person_params = {
    "size": 1000,
    "order": "lastName",
}
response = requests.get(person_url, headers=person_headers, params=person_params)
response.raise_for_status()
persons = response.json()
supervisors_pure = persons.get("items", [])

def extract_keywords(obj):
    keywords = set()
    for keyWordGroup in obj.get("keywordGroups", []):
        if not isinstance(keyWordGroup, dict):
            continue
        for keywordObj in keyWordGroup.get("keywords", []):
            if not isinstance(keywordObj, dict):
                continue
            for keyword in keywordObj.get("freeKeywords", []):
                if isinstance(keyword, str) and keyword:
                    keyword = keyword.strip()
                    keywords.add(keyword.lower())
    return keywords

def calculate_similarity(db_keywords, pure_keywords):
    if not pure_keywords:
        return 0
    db_keywords = set(db_keywords)
    pure_keywords = set(pure_keywords)
    intersection = db_keywords.intersection(pure_keywords)
    return len(intersection) / len(pure_keywords)

def assign_supervisor_topics(supervisors, supervisors_db_topics, topics_db):
    supervisor_topics = set()
    for supervisor in supervisors:
        for supervisor_topic in supervisors_db_topics:
            if supervisor_topic['uuid'] == supervisor['uuid']:
                for topic in topics_db:
                    if topic['topic_id'] == supervisor_topic['topic_id']:
                        for keywords in topic['keywords']:
                            supervisor_topics.add(keywords)
    return supervisor_topics


supervisor_pure_dict = {supervisor['uuid']: supervisor for supervisor in supervisors_pure}

intersections = 0
total_pure_keywords = 0

for supervisor in supervisors_db:
    supervisor['keywords'] = assign_supervisor_topics([supervisor], supervisors_db_topics, topics_db)
    pure_supervisor = supervisor_pure_dict.get(supervisor['uuid'])
    if pure_supervisor:
        db_keywords = set(keyword.strip().lower() for keyword in supervisor['keywords'])
        pure_keywords = extract_keywords(pure_supervisor)
        intersections += len(set(db_keywords).intersection(set(pure_keywords)))
        total_pure_keywords += len(set(pure_keywords))

percent_covered = (intersections / total_pure_keywords) * 100 if total_pure_keywords else 0

print("Percent covered:", percent_covered)


anna_db = None
for supervisor in supervisors_db:
    name = supervisor.get("name", {})
    if (
        name.get("firstName", "").strip().lower() == "anna"
        and name.get("lastName", "").strip().lower() == "rogers"
    ):
        anna_db = supervisor
        break

if anna_db:
    anna_db_keywords = assign_supervisor_topics([anna_db], supervisors_db_topics, topics_db)
    print(f"Assigned topic keywords for Anna Rogers: {sorted(anna_db_keywords)}")
else:
    print("Anna Rogers not found in DB supervisors.")