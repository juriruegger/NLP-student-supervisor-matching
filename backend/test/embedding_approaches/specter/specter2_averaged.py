import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import torch
from transformers import AutoTokenizer
from adapters import AutoAdapterModel
import matplotlib.pyplot as plt
import seaborn as sns

specter_tokenizer = AutoTokenizer.from_pretrained('allenai/specter2_base')
specter_model = AutoAdapterModel.from_pretrained('allenai/specter2_base')

specter_model.load_adapter("allenai/specter2", source="hf", load_as="specter2", set_active=True)

def specter2_averaged_embeddings(supervisors, supervisors_db):
    """
    Evaluates supervisor proposals using SPECTER 2 averaged embeddings with.
    
    Parameters:
        supervisors: List of supervisors with their proposals to evaluate
        supervisors_db: List of supervisor records from database

    Returns:
        The MRR score for the SPECTER 2 embedding approach.
    """
    def embed(text):
        inputs = specter_tokenizer(
            text,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )

        with torch.no_grad():
            outputs = specter_model(**inputs)

        mask = inputs["attention_mask"].unsqueeze(-1)
        token_embeddings = outputs.last_hidden_state
        summed = (token_embeddings * mask).sum(dim=1)
        counts = mask.sum(dim=1)
        mean_pooled = summed / counts 
        return mean_pooled.squeeze().detach() 

    def calculate_suggestions(embedding, supervisors):
        similarities = []

        # Ensure embedding is 2D
        if len(embedding.shape) == 1:
            embedding = embedding.reshape(1, -1)

        for supervisor in supervisors:
            embedding_str = supervisor.get('specter2_averaged_embedding', [])

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
            embedding = embed(str(proposal))
            similarities = calculate_suggestions(embedding, supervisors_db)
            
            for rank, similarity in enumerate(similarities, 1):
                if (similarity['supervisor']['name']['firstName'] == supervisor['firstName'] and
                    similarity['supervisor']['name']['lastName'] == supervisor['lastName']):
                    reciprocal_ranks.append(1.0 / rank)

                    length_results.append((len(str(proposal).split()), rank))

                    break

    mrr = sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0

    doc_lengths = [r[0] for r in length_results]
    ranks = [r[1] for r in length_results]

    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 6))
    plt.scatter(doc_lengths, ranks, alpha=0.7)
    plt.xlabel('Document Length (tokens)')
    plt.ylabel('Rank')
    plt.gca().invert_yaxis()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("backend/test/results/length_results.png")
    plt.close()
        
    return mrr