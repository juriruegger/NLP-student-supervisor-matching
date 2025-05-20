import math
from sklearn.feature_extraction.text import CountVectorizer
from transformers import AutoTokenizer, AutoModel
import torch
import requests
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from bertopic import BERTopic
from collections import defaultdict
import joblib
from hdbscan import HDBSCAN

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# PURE setup
load_dotenv("backend/.env.local")

url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

supabase: Client = create_client(url, key)

PURE_API_KEY = os.environ.get("PURE_API_KEY")
PURE_BASE_URL = os.environ.get("PURE_BASE_URL")

# Models and tokenizers
model_id = "answerdotai/ModernBERT-base"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModel.from_pretrained(model_id)

# Utils

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

def extract_en_abstract(abstract_obj):
    if not isinstance(abstract_obj, dict):
        return ""
    return (abstract_obj.get("abstract", {}).get("en_GB", "") or "")

def valid_supervisor_topic(x):
    return isinstance(x, (int, float)) and not (math.isnan(x) or math.isinf(x))

# Get researchers from PURE API
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
researchers = persons.get("items", [])
all_researchers = researchers.copy() # all researcher will be used for topic modelling, so this should be unchanged

# Filter researchers who are allowed as supervisors.
allowed_titles = [
    "Associate Professor",
    "PhD fellow",
    "Assistant Professor",
    "Professor",
    "Postdoc",
    "Head of Section",
    "Head of PhD School",
    "Head of Studies",
    "Head of Study Programme",
    "Head of Center",
    "Deputy Head of Department",
    "Deputy Head of Center",
    "Co-head of study programme",
    "Co-head of Study Programme",
    "Co-head of PhD School",
    "Full Professor",
    "Full Professor, Head of PhD School",
    "Full Professor, Co-head of PhD School",
    "Full Professor, Head of Center",
    "Full Professor, Co-head of Center",
    "Full Professor, Deputy Head of Department",
    "Full Professor, Deputy Head of Center",
    "Full Professor, Head of Studies",
    "Full Professor, Head of Study Programme",
    "Full Professor, Co-head of Study Programme"
]

filtered_researchers = []
for researcher in researchers:
    associations = researcher.get("staffOrganizationAssociations", [])
    for association in associations:
        title = association.get("jobTitle", {}).get("term", {}).get("en_GB")
        if title and title in allowed_titles:
            filtered_researchers.append(researcher)
            break


# Get abstracts from PURE API
research_outputs = []

url = f"{PURE_BASE_URL}/research-outputs"
headers = {
    "accept": "application/json", 
    "api-key": PURE_API_KEY,
}
params = {
    "size": 1,
    "order": "authorLastName",
}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()

# Getting the total number of research outputs
count = data.get("count", 0)

# Fetching the actual research outputs
while len(research_outputs) < count:
    params = {
        "size": 1000,
        "offset": len(research_outputs),
        "order": "authorLastName",
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    research_outputs.extend(data.get("items", []))

# Filter abstracts:
filtered_abstracts = []
for abstract in research_outputs:
    text = extract_en_abstract(abstract)
    if not text:
        continue
    if not abstract.get("contributors"):
        continue
    if not abstract.get("title"):
        continue
    valid_contributer = False
    for contributor in abstract.get("contributors", []):
        if not contributor.get("person"):
            continue
        if contributor["person"].get("uuid") in [researcher["uuid"] for researcher in filtered_researchers]:
            valid_contributer = True
            break
    if not valid_contributer:
        continue
    filtered_abstracts.append(abstract)

# Associate abstracts with researchers
researchers_with_abstracts = []
for researcher in filtered_researchers:
    has_any_abstract = False
    researcher_abstracts = []
    for abstract in filtered_abstracts:
        for contributor in abstract.get("contributors", []):
            if not contributor.get("person"):
                continue
            if contributor["person"].get("uuid") == researcher["uuid"]:
                researcher_abstracts.append(abstract)
                has_any_abstract = True
                break
    if not has_any_abstract:
        continue

    researcher["abstracts"] = researcher_abstracts
    researchers_with_abstracts.append(researcher)

researchers = researchers_with_abstracts

# Embed abstract
def embed(text):
    tokens = tokenizer(text, add_special_tokens=False)["input_ids"]
    print(f"Length (in tokens): {len(tokens)}")
    if len(tokens) > 8192:
        print(f"Abstract exceeds 8192 tokens, removing {len(tokens)-8192} tokens")
    
    inputs = tokenizer(text, max_length=8192, truncation=True, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)

    # Mean pooling for the entire text
    embedding = torch.mean(outputs.last_hidden_state * inputs["attention_mask"].unsqueeze(-1), dim=1)
    return embedding.squeeze().detach()

# Apply average mean pooling across embeddings for a single researcher (testing)
def average_pooling(embeddings):
    return torch.mean(torch.stack(embeddings), dim=0)

processed_abstracts = 0
for researcher in researchers:
    embeddings_abstracts = []
    master_abstract = ""
    for abstract in researcher.get("abstracts", []):
        if not isinstance(abstract, dict):
            continue
        text = extract_en_abstract(abstract)
        if not text or text == "":
            continue
        processed_abstracts += 1
        embedding = embed(text)
        abstract["embedding"] = embedding
        embeddings_abstracts.append(embedding)
        master_abstract += text + " "

    keywords_list = extract_keywords(researcher)
    keywords = " ".join(keywords_list)

    embeddings_keywords = embed(keywords.strip())

    master_text_with_keywords = master_abstract + " " + " ".join(extract_keywords(researcher))

    # without keywords or averaging
    master_embedding = embed(master_abstract)

    # with keywords without averaging
    master_embedding_with_keywords = embed(master_text_with_keywords)

    # without keywords, averaged
    averaged_embedding = average_pooling(embeddings_abstracts).squeeze().detach().cpu()

    # with keywords, averaged
    averaged_embedding_with_keywords = average_pooling(embeddings_abstracts + [embeddings_keywords]).squeeze().detach().cpu()
    
    researcher["embedding"] = master_embedding
    researcher["averaged_embedding"] = averaged_embedding
    researcher["embedding_with_keywords"] = master_embedding_with_keywords
    researcher["averaged_embedding_with_keywords"] = averaged_embedding_with_keywords

# Topic modelling
# Getting possible keywords from all researchers and research outputs
all_keywords = set()
for researcher in all_researchers:
    if not isinstance(researcher, dict):
        continue
    all_keywords.update(extract_keywords(researcher))

print("Number of unique keywords in researchers:", len(all_keywords))

""" for output in research_outputs:
    if not isinstance(output, dict):
        continue
    all_keywords.update(extract_keywords(output))

print("Number of unique keywords:", len(all_keywords)) """

docs = []
doc_supervisors = []
for researcher in researchers:
    for abs_obj in researcher.get("abstracts", []):
        text = extract_en_abstract(abs_obj)
        if text:
            docs.append(text)
            doc_supervisors.append(researcher["uuid"])


vectorizer = CountVectorizer(
    vocabulary = list(all_keywords),
    ngram_range = (1, 3),
    lowercase = True
)

joblib.dump(vectorizer, "vectorizer.joblib")

topic_model = BERTopic(
    embedding_model=model,
    vectorizer_model=vectorizer,
    calculate_probabilities=True,
)

topics, probs = topic_model.fit_transform(docs)

topic_model.visualize_topics()
topic_model.visualize_barchart()

sup_topic_scores = defaultdict(lambda: defaultdict(float))

for idx, sup_uuid in enumerate(doc_supervisors):
    label = topics[idx]
    if label == -1:
        continue
    score = probs[idx][label] if probs is not None else 1.0
    sup_topic_scores[sup_uuid][label] += float(score) 

topics = {}
supervisor_topics = []

existing_labels = set()

for researcher in researchers:
    tid_scores = sup_topic_scores.get(researcher["uuid"], {})
    top_tids = sorted(tid_scores, key=tid_scores.get, reverse=True)[:5]
    topic_ids = []
    
    for tid in top_tids:
        # get top n keywords for the topic
        n_keywords = 10
        keywords = [w.title() for w, _ in topic_model.get_topic(tid)[:n_keywords]]
        label = keywords[0].title()

        for i in range(n_keywords):
            if keywords[i].title() not in existing_labels:
                label = keywords[i].title()
                break

        existing_labels.add(label)

        topics[tid] = {               
            "topic_id": tid,
            "label": label,
            "keywords": keywords,
        }

        supervisor_topics.append({
            "uuid": researcher["uuid"],
            "topic_id": int(tid),
            "score": tid_scores[tid],
        })
        topic_ids.append(int(tid))
    researcher["topic_ids"] = topic_ids

unique_pairs = {}
for row in supervisor_topics:
    key = (row["uuid"], row["topic_id"])
    if key not in unique_pairs or row["score"] > unique_pairs[key]["score"]:
        unique_pairs[key] = row

supervisor_topics = list(unique_pairs.values())

# Some topics can be duplicated, so we ensure they are unique
def deduplicate_topics(topics):
    seen = set()
    unique = []
    for topic in topics.values():
        label = topic["label"]
        keywords_tuple = tuple(topic["keywords"])
        key = (label, keywords_tuple)
        if key not in seen:
            seen.add(key)
            unique.append(topic)
    return unique

supervisor_updates = []

for researcher in researchers:
    uuid = researcher.get("uuid")
    embedding = researcher.get("embedding") # embedding
    averaged_embedding = researcher.get("averaged_embedding") # averaged embedding
    embedding_with_keywords = researcher.get("embedding_with_keywords")  # added embedding with keywords
    averaged_embedding_with_keywords = researcher.get("averaged_embedding_with_keywords")  # added averaged embedding with keywords
    name = researcher.get("name")
    emails = researcher.get("emails", [])
    email = emails[0].get("value") if emails and isinstance(emails[0], dict) else None

    if embedding is None:
        continue
    if hasattr(embedding, "tolist"):
        embedding = embedding.tolist()
    if hasattr(averaged_embedding, "tolist"):
        averaged_embedding = averaged_embedding.tolist()
    if hasattr(embedding_with_keywords, "tolist"):
        embedding_with_keywords = embedding_with_keywords.tolist()
    if hasattr(averaged_embedding_with_keywords, "tolist"):
        averaged_embedding_with_keywords = averaged_embedding_with_keywords.tolist()

    abstracts_list = []
    for abstract in researcher.get("abstracts", []):
        if not isinstance(abstract, dict):
            continue
        abstract_embedding = abstract.get("embedding").tolist()
        abstract_title = abstract.get("title").get("value")
        abstract_url = abstract.get("portalUrl")
        abstract_text = abstract.get("abstract").get("en_GB")
        abstracts_list.append({
            "title": abstract_title,
            "url": abstract_url,
            "embedding": abstract_embedding,
            "text": abstract_text,
        })
    
    supervisor_updates.append({
        "uuid": uuid,
        "embedding": embedding, # concattenated embedding
        "averaged_embedding": averaged_embedding, # averaged embedding
        "embedding_with_keywords": embedding_with_keywords, # concattenated embedding with keywords
        "averaged_embedding_with_keywords": averaged_embedding_with_keywords, # averaged embedding with keywords
        "abstracts": abstracts_list,
        "name": name,
        "email": email,
    })

batch_size = 10 # We're upserting in batches to avoid size limitations

for i in range(0, len(supervisor_updates), batch_size):
    batch = supervisor_updates[i:i+batch_size]
    batch_num = (i // batch_size) + 1
    
    try:
        response = (
            supabase.table("supervisor")
            .upsert(batch)
            .execute()
        )
    except Exception as e:
        print(f"Error in batch {batch_num}: {str(e)}")

if topics:
    unique_topics = deduplicate_topics(topics)
    supabase.table("topic").upsert(unique_topics).execute()

for topic in supervisor_topics:
    if not valid_supervisor_topic(topic["topic_id"]):
        print("Invalid topic_id:", topic)
    if not valid_supervisor_topic(topic["score"]):
        print("Invalid score:", topic)

valid_stopic = [
    topic for topic in supervisor_topics
    if valid_supervisor_topic(topic["topic_id"]) and valid_supervisor_topic(topic["score"])
]

if valid_stopic:
    supabase.table("supervisor_topic").upsert(valid_stopic).execute()

print("Upsert completed")
