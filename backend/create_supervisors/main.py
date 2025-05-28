import sys
from tqdm import tqdm
import os
from dotenv import load_dotenv
from supabase import create_client, Client

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.create_supervisors.create_model_embeddings import get_bert_embeddings, get_modernbert_embeddings, get_scibert_embeddings, get_specter2_embeddings
from backend.create_supervisors.topic_modeling import topic_modelling
from backend.create_supervisors.get_supervisors import get_supervisors
from backend.create_supervisors.utils import extract_email, extract_keywords
from backend.create_supervisors.db_update_supervisors_topics import db_update_supervisors_topics

os.environ["TOKENIZERS_PARALLELISM"] = "false"

"""
The main script to create and update supervisors in the database.
This script fetches supervisors from the PURE API, processes their data to extract keywords and abstracts, 
creates topics using topic modeling, generates embeddings for each supervisor using various models,
and updates the database with their embeddings and topics.
"""

# PURE setup
load_dotenv("backend/.env.local")

url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

supabase: Client = create_client(url, key)

researchers, all_researchers = get_supervisors()

unique_topics, supervisor_topics = topic_modelling(researchers, all_researchers)

supervisor_updates = []

uuids = []
for researcher in researchers:
    uuid = researcher.get("uuid")
    uuids.append(uuid)
    email = extract_email(researcher)

    abstracts_list = []
    for abstract in researcher.get("abstracts", []):
        if not isinstance(abstract, dict):
            continue
        abstract_text = abstract.get("abstract").get("en_GB")
        abstract_uuid = abstract.get("uuid")
        abstracts_list.append({
            "text": abstract_text,
            "uuid": abstract_uuid
        })

    supervisor_updates.append({
        "uuid": uuid,
        "keywords": list(extract_keywords(researcher)),
        "abstracts": abstracts_list,
        "email": email,
    })

models = {
    "specter2": get_specter2_embeddings,
    "modernbert": get_modernbert_embeddings,
    "bert": get_bert_embeddings,
    "scibert": get_scibert_embeddings,
}

for model_name, model_function in tqdm(models.items(), desc="Adding embeddings"):
    supervisor_updates = model_function(supervisor_updates)

for supervisor in supervisor_updates:
    supervisor.pop("keywords", None)
    for abstract in supervisor.get("abstracts", []):
        abstract.pop("text", None)

db_update_supervisors_topics(supabase, supervisor_updates, unique_topics, supervisor_topics)

print("Update completed")