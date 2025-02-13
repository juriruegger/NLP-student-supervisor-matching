import pandas as pd
from transformers import AutoTokenizer, AutoModel
import torch
import csv
import requests
import os
from dotenv import load_dotenv
from supabase import create_client, Client

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

# Embed each abstract
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

# Apply average mean pooling across embeddings for a single researcher
def average_pooling(embeddings):
    return torch.mean(torch.stack(embeddings), dim=0)

for researcher in researchers:
    embeddings_abstracts = []
    for abstract in researcher.get("abstracts", {}):
        if not abstract.get("abstract"):
            continue
        if not abstract.get("abstract").get("en_GB"):
            continue
        print("title:", abstract.get("title"))
        embedding = embed(abstract.get("abstract").get("en_GB"))
        abstract["embedding"] = embedding
        embeddings_abstracts.append(embedding)
    
    embeddings_keywords = []
    for keyWordGroup in researcher.get("keywordGroups", []):
        for keywordObj in keyWordGroup.get("keywords", []):
            for keyword in keywordObj.get("freeKeywords", []):
                print("keyword:", keyword)
                embedding_keyword = embed(keyword)
                embeddings_keywords.append(embedding_keyword)

    completeEmbeddings = embeddings_abstracts + embeddings_keywords
    averaged_embedding = average_pooling(completeEmbeddings).squeeze().detach().cpu().numpy()
    researcher["embedding"] = averaged_embedding

supervisor_updates = []

for researcher in researchers:
    uuid = researcher.get("uuid")
    embedding = researcher.get("embedding")
    if embedding is None:
        continue
    if hasattr(embedding, "tolist"):
        embedding = embedding.tolist()
    
    abstracts_list = []
    for abstract in researcher.get("abstracts", []):
        abstract_embedding = abstract.get("embedding").tolist()
        abstract_title = abstract.get("title").get("value")
        abstract_url = abstract.get("portalUrl")
        abstracts_list.append({
            "title": abstract_title,
            "url": abstract_url,
            "embedding": abstract_embedding,
        })
    
    supervisor_updates.append({
        "uuid": uuid,
        "embedding": embedding,
        "abstracts": abstracts_list,
    })

response = (
    supabase.table("supervisor")
    .upsert(supervisor_updates)
    .execute()
)

print("Update completed")