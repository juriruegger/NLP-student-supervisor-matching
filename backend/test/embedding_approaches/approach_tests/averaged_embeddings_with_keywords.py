import json
import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity

# Models and tokenizers
model_id = "answerdotai/ModernBERT-base"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModel.from_pretrained(model_id)

def averaged_embeddings_with_keywords(supervisors, supervisors_db):
    def embed(text):
        inputs = tokenizer(text, max_length=8192, truncation=True, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)

        # Mean pooling for the entire text
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
            embedding_str = supervisor.get('averaged_embedding_with_keywords', []) # Getting the averaged embedding instead'

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

    reciprocal_ranks = []
    for supervisor in supervisors:
        for proposal in supervisor['proposals']:
            embedding = embed(proposal)
            similarities = calculate_suggestions(embedding, supervisors_db)
            
            for rank, similarity in enumerate(similarities, 1):
                if (similarity['supervisor']['name']['firstName'] == supervisor['firstName'] and
                    similarity['supervisor']['name']['lastName'] == supervisor['lastName']):
                    reciprocal_ranks.append(1.0 / rank)
                    break

    mrr = sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0
        
    return mrr