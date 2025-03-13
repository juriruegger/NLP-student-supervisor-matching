from sklearn.feature_extraction.text import CountVectorizer
from transformers import AutoTokenizer, AutoModel
import torch
import requests
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from bertopic import BERTopic
from umap.umap_ import UMAP
from hdbscan import HDBSCAN
from collections import defaultdict

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# PURE setup
load_dotenv("backend/.env.local")

url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

supabase: Client = create_client(url, key)

API_KEY = os.environ.get("PURE_API_KEY")
BASE_URL = os.environ.get("PURE_BASE_URL")

# Models and tokenizers
model_id = "answerdotai/ModernBERT-base"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModel.from_pretrained(model_id)

# get researchers from PURE API
url = f"{BASE_URL}/persons"
headers = {
    "accept": "application/json", 
    "api-key": API_KEY,
}
params = {
    "size": 1000,
    "order": "lastName",
}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
researchers = data.get("items", [])

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


# get abstracts from PURE API
url = f"{BASE_URL}/research-outputs"
headers = {
    "accept": "application/json", 
    "api-key": API_KEY,
}
params = {
    "size": 1000,
    "order": "title",
}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
abstracts = data.get("items", [])

# Filter abstracts:
filtered_abstracts = []
for abstract in abstracts:
    if not abstract.get("abstract"):
        continue
    if not abstract.get("abstract").get("en_GB"):
        continue
    if not abstract.get("contributors"):
        continue
    if not abstract.get("title"):
        continue
    for contributor in abstract.get("contributors", []):
        if not contributor.get("person"):
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
        print(f"Abstract exceeds 8192 tokens, truncating: {len(tokens)} tokens")
    
    inputs = tokenizer(text, max_length=8192, truncation=True, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)

    # Mean pooling for the entire text
    embedding = torch.mean(outputs.last_hidden_state * inputs["attention_mask"].unsqueeze(-1), dim=1)
    return embedding.squeeze().detach()

# Apply average mean pooling across embeddings for a single researcher (testing)
def average_pooling(embeddings):
    return torch.mean(torch.stack(embeddings), dim=0)

all_keywords = set()
for researcher in researchers:
    embeddings_abstracts = []
    master_abstract = ""
    for abstract in researcher.get("abstracts", []):
        if not abstract.get("abstract"):
            continue
        if not abstract.get("abstract").get("en_GB"):
            continue
        print("title:", abstract.get("title"))
        
        
        embedding = embed(abstract.get("abstract").get("en_GB"))
        abstract["embedding"] = embedding
        embeddings_abstracts.append(embedding)
        master_abstract += abstract.get("abstract").get("en_GB") + " "

    
    embeddings_keywords = []
    for keyWordGroup in researcher.get("keywordGroups", []):
        for keywordObj in keyWordGroup.get("keywords", []):
            for keyword in keywordObj.get("freeKeywords", []):
                embedding_keyword = embed(keyword)
                embeddings_keywords.append(embedding_keyword)
                all_keywords.add(keyword)

    master_text_with_keywords = master_abstract
    for keyWordGroup in researcher.get("keywordGroups", []):
        for keywordObj in keyWordGroup.get("keywords", []):
            for keyword in keywordObj.get("freeKeywords", []):
                master_text_with_keywords += " " + keyword

    # without keywords or averaging
    master_embedding = embed(master_abstract)

    # with keywords without averaging
    master_embedding_with_keywords = embed(master_text_with_keywords)

    # wihthout keywords, averaged
    averaged_embedding = average_pooling(embeddings_abstracts).squeeze().detach().cpu()

    # with keywords, averaged
    completeEmbeddingsWithKeywords = embeddings_abstracts + embeddings_keywords
    averaged_embedding_with_keywords = average_pooling(completeEmbeddingsWithKeywords).squeeze().detach().cpu()
    
    researcher["embedding"] = master_embedding
    researcher["averaged_embedding"] = averaged_embedding
    researcher["embedding_with_keywords"] = master_embedding_with_keywords
    researcher["averaged_embedding_with_keywords"] = averaged_embedding_with_keywords

# Topic modelling
docs = []
doc_supervisors = []
for researcher in researchers:
    for abs_obj in researcher.get("abstracts", []):
        abs_text = abs_obj.get("abstract", {}).get("en_GB")
        if abs_text:
            docs.append(abs_text)
            doc_supervisors.append(researcher["uuid"])

all_keywords = {kw.lower() for kw in all_keywords}

vectorizer = CountVectorizer(
    vocabulary = list(all_keywords),
    ngram_range = (1, 3),
    lowercase = True
)

n_docs = len(docs)
n_neighbors = min(10, n_docs - 1)
min_cluster = max(2, min(10, n_docs // 2))

umap_model = UMAP(n_neighbors=n_neighbors, min_dist=0.0, metric="cosine")
hdb_model = HDBSCAN(min_cluster_size=min_cluster, min_samples=1, metric="euclidean", prediction_data=True)

topic_model = BERTopic(
    embedding_model = model,
    vectorizer_model = vectorizer,
    umap_model = umap_model,
    hdbscan_model = hdb_model,
    calculate_probabilities=True,
    nr_topics=None,
)

topics, probs = topic_model.fit_transform(docs)

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

for res in researchers:
    tid_scores = sup_topic_scores.get(res["uuid"], {})
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
            "uuid": res["uuid"],
            "topic_id": int(tid),
            "score": tid_scores[tid],
        })
        topic_ids.append(int(tid))
    res["topic_ids"] = topic_ids

unique_pairs = {}
for row in supervisor_topics:
    key = (row["uuid"], row["topic_id"])
    if key not in unique_pairs or row["score"] > unique_pairs[key]["score"]:
        unique_pairs[key] = row

supervisor_topics = list(unique_pairs.values())

if topics:
    supabase.table("topic").upsert(list(topics.values())).execute()

if supervisor_topics:
    supabase.table("supervisor_topic").upsert(supervisor_topics).execute()


supervisor_updates = []

for researcher in researchers:
    uuid = researcher.get("uuid")
    embedding = researcher.get("embedding")
    averaged_embedding = researcher.get("averaged_embedding") # averaged embedding for testing
    embedding_with_keywords = researcher.get("embedding_with_keywords")  # added embedding with keywords
    averaged_embedding_with_keywords = researcher.get("averaged_embedding_with_keywords")  # added averaged embedding with keywords
    name = researcher.get("name")

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
        "embedding": embedding,
        "averaged_embedding": averaged_embedding, # averaged embedding for testing
        "embedding_with_keywords": embedding_with_keywords, # added embedding with keywords for testing
        "averaged_embedding_with_keywords": averaged_embedding_with_keywords, # added averaged embedding with keywords for testing
        "abstracts": abstracts_list,
        "name": name,
    })


batch_size = 50 # We're upserting in batches to avoid size limitations
total_batches = (len(supervisor_updates) + batch_size - 1) // batch_size

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

print("Upsert completed")