import json
import pandas as pd
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.test.embedding_approaches.modernbert.modernbert_averaged_embeddings import modernbert_averaged_embeddings
from backend.test.embedding_approaches.modernbert.modernbert_averaged_embeddings_with_keywords import modernbert_averaged_embeddings_with_keywords
from backend.test.embedding_approaches.modernbert.modernbert_concatenated_embeddings import modernbert_concatenated_embeddings
from backend.test.embedding_approaches.modernbert.modernbert_concatenated_embeddings_with_keywords import modernbert_concatenated_embeddings_with_keywords
from backend.test.embedding_approaches.tfidf_baseline import tfidf_baseline
from backend.test.embedding_approaches.bert.bert_averaged import bert_averaged_embeddings
from backend.test.embedding_approaches.bert.bert_averaged_with_keywords import bert_averaged_embeddings_with_keywords
from backend.test.embedding_approaches.scibert.scibert_averaged import scibert_averaged_embeddings
from backend.test.embedding_approaches.scibert.scibert_averaged_with_keywords import scibert_averaged_embeddings_with_keywords
from backend.test.embedding_approaches.specter.specter2_averaged import specter2_averaged_embeddings
from backend.test.embedding_approaches.specter.specter2_averaged_with_keywords import specter2_averaged_embeddings_with_keywords


load_dotenv("backend/.env.local")

url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

supabase: Client = create_client(url, key)

def evaluate_proposals(proposals, supervisors_db, label):

    supervisor_proposals = {}

    supervisor_details = {}

    for _, row in proposals.iterrows():
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

    tests = [
        modernbert_concatenated_embeddings, 
        modernbert_averaged_embeddings, 
        modernbert_concatenated_embeddings_with_keywords, 
        modernbert_averaged_embeddings_with_keywords, 
        tfidf_baseline
    ]

    model_tests = [
        modernbert_concatenated_embeddings,
        modernbert_concatenated_embeddings_with_keywords,
        modernbert_averaged_embeddings,
        modernbert_averaged_embeddings_with_keywords,
        bert_averaged_embeddings,
        bert_averaged_embeddings_with_keywords,
        scibert_averaged_embeddings,
        scibert_averaged_embeddings_with_keywords,
        specter2_averaged_embeddings,
        specter2_averaged_embeddings_with_keywords,
        tfidf_baseline
    ]
    mrr_approach_results = {}

    print("Running approach tests...")
    for test in tests:
        print("Running test:", test.__name__)
        mrr = test(supervisors, supervisors_db)
        print("MRR:", mrr)
        mrr_approach_results[test.__name__.replace('_', ' ').title()] = mrr

    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 6))
    sns.barplot(x=list(mrr_approach_results.keys()), y=list(mrr_approach_results.values()))
    plt.ylabel("Mean Reciprocal Rank (MRR)")
    plt.ylim(0, 1)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"backend/test/results/embedding_approaches/mrr_results({label}).png")

    mrr_model_results = {}

    print("\nRunning model tests...")
    for test in model_tests:
        print("Running test:", test.__name__)
        mrr = test(supervisors, supervisors_db)
        print("MRR:", mrr)
        mrr_model_results[test.__name__.replace('_', ' ').title()] = mrr

    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 6))
    sns.barplot(x=list(mrr_model_results.keys()), y=list(mrr_model_results.values()))
    plt.ylabel("Mean Reciprocal Rank (MRR)")
    plt.ylim(0, 1)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"backend/test/results/models/mrr_results({label}).png")

proposals = pd.read_csv("backend/test/proposals/proposals.csv")
gpt_proposals = pd.read_csv("backend/test/proposals/gpt_proposals.csv")

BATCH_SIZE = 25
offset = 0
supervisors_db = []

while True:
    response = (
        supabase.table("supervisor")
        .select(
            "name", 
            "abstracts",
            "embedding", 
            "averaged_embedding", 
            "embedding_with_keywords", 
            "averaged_embedding_with_keywords", 
            "bert_averaged_embedding", 
            "bert_averaged_embedding_with_keywords",
            "scibert_averaged_embedding",
            "scibert_averaged_embedding_with_keywords",
            "specter2_averaged_embedding",
            "specter2_averaged_embedding_with_keywords",
        )
        .range(offset, offset + BATCH_SIZE - 1)
        .execute()
    )
    batch = response.data or []
    if not batch:
        break

    supervisors_db.extend(batch)
    offset += BATCH_SIZE

print(f"Fetched total rows: {len(supervisors_db)}")

print("__" * 50)
print("\nEvaluating supervisor proposals...")
evaluate_proposals(proposals, supervisors_db, "supervisor_proposals")
print("__" * 50)
print("\nEvaluating GPT proposals...")
evaluate_proposals(gpt_proposals, supervisors_db, "gpt_proposals")