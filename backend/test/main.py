import pandas as pd
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from sklearn.metrics.pairwise import cosine_similarity
from concat_embeddings import concat_embeddings
from averaged_embeddings import averaged_embeddings
from concat_embeddings_with_keywords import concat_embeddings_with_keywords
from averaged_embeddings_with_keywords import averaged_embeddings_with_keywords
from tfidf_baseline import tfidf_baseline
import matplotlib.pyplot as plt
import seaborn as sns

proposals = pd.read_csv("backend/proposals.csv")

load_dotenv("backend/.env.local")

url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

supabase: Client = create_client(url, key)

supervisor_proposals = {}

supervisor_details = {}

for index, row in proposals.iterrows():
    first_name = row['firstName']
    last_name = row['lastName']
    full_name = f"{first_name} {last_name}"
    text = row['proposal']
    
    if full_name not in supervisor_proposals:
        supervisor_proposals[full_name] = []
    
    supervisor_proposals[full_name].append(text)
    
    if full_name not in supervisor_details:
        supervisor_details[full_name] = {
            'firstName': first_name,
            'lastName': last_name
        }

supervisors = []
for full_name, texts in supervisor_proposals.items():
    supervisors.append({
        'full_name': full_name,
        'firstName': supervisor_details[full_name]['firstName'],
        'lastName': supervisor_details[full_name]['lastName'],
        'proposals': texts,
    })

response = (
    supabase.table("supervisor")
    .select("*")
    .execute()
)

supervisors_db = response.data

response = (
    supabase.table("topic")
    .select("*")
    .execute()
)

topics_db = response.data

response = (
    supabase.table("supervisor_topic")
    .select("*")
    .execute()
)

supervisor_topic_relation_db = response.data

tests = [
    concat_embeddings, 
    averaged_embeddings, 
    concat_embeddings_with_keywords, 
    averaged_embeddings_with_keywords, 
    tfidf_baseline
]
mrr_results = {}

for test in tests:
    print("Running test:", test.__name__)
    mrr = test(supervisors, supervisors_db)
    print("MRR:", mrr)
    mrr_results[test.__name__.replace('_', ' ').capitalize()] = mrr


sns.set_theme(style="whitegrid")
plt.figure(figsize=(10, 6))
sns.barplot(x=list(mrr_results.keys()), y=list(mrr_results.values()))
plt.xlabel("Embedding Method")
plt.ylabel("Mean Reciprocal Rank (MRR)")
plt.ylim(0, 1)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("backend/test/mrr_results.png")


