import json
import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import seaborn as sns

# Models and tokenizers
model_id = "answerdotai/ModernBERT-base"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModel.from_pretrained(model_id)

def averaged_embeddings(supervisors, supervisors_db):
    def embed(text):
        inputs = tokenizer(text, max_length=8192, truncation=True, return_tensors="pt")
        input_length = len(inputs["input_ids"][0])
        with torch.no_grad():
            outputs = model(**inputs)

        # Mean pooling for the entire text
        embedding = torch.mean(outputs.last_hidden_state * inputs["attention_mask"].unsqueeze(-1), dim=1)
        return embedding.squeeze().detach(), input_length

    def calculate_suggestions(embedding, supervisors):
        similarities = []

        # Ensure embedding is 2D
        if len(embedding.shape) == 1:
            embedding = embedding.reshape(1, -1)

        for supervisor in supervisors:
            embedding_str = supervisor.get('averaged_embedding', []) # Getting the averaged embedding instead'

            if not embedding_str:
                continue

            embedding_list = json.loads(embedding_str)

            try:
                supervisor_embedding = np.array([float(x) for x in embedding_list]).reshape(1, -1)
            except ValueError:
                print('Error parsing supervisor embedding')
                continue

            similarity = cosine_similarity(embedding, supervisor_embedding)
            supervisor["similarity"] = similarity.item()
            similarities.append({
                'supervisor': supervisor,
                'similarity': similarity.item()
            })
        similarities.sort(key=lambda x: x['similarity'], reverse=True)

        return similarities

    length_results = []
    reciprocal_ranks = []
    for supervisor in supervisors:
        for proposal in supervisor['proposals']:
            embedding, input_length = embed(proposal)
            similarities = calculate_suggestions(embedding, supervisors_db)
            
            for rank, similarity in enumerate(similarities, 1):
                if (similarity['supervisor']['name']['firstName'] == supervisor['firstName'] and
                    similarity['supervisor']['name']['lastName'] == supervisor['lastName']):
                    reciprocal_ranks.append(1.0 / rank)
                    length_results.append((
                        rank,
                        input_length,
                    ))
                    break

    mrr = sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0

    results_sorted = sorted(length_results, key=lambda x: x[1])
    doc_lengths = [r[1] for r in results_sorted]
    ranks = [r[0] for r in results_sorted]

    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 6))
    plt.scatter(doc_lengths, ranks, alpha=0.7)
    plt.xlabel('Document Length (tokens)')
    plt.ylabel('Rank')
    plt.gca().invert_yaxis()
    plt.ylim(141, 0)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("backend/test/results/length_results.png")
    plt.close()
    
    return mrr



