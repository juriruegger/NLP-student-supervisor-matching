import json
import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
import joblib
from umap import UMAP
from hdbscan import HDBSCAN
from collections import defaultdict
from bertopic import BERTopic

# Models and tokenizers
model_id = "answerdotai/ModernBERT-base"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModel.from_pretrained(model_id)

def keywords_matching(supervisors, supervisors_db, topics_db, supervisor_topic_relation):
    vectorizer = joblib.load("vectorizer.joblib")    

    for supervisor in supervisors:
        for proposal in supervisor['proposals']:
            n_neighbors = 10
            min_cluster = 2

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
            topics, probs = topic_model.fit_transform([proposal])

            sup_topic_scores = defaultdict(lambda: defaultdict(float))

            label = topics[0]
            if label == -1:
                continue
            score = probs[0][label] if probs is not None else 1.0
            sup_topic_scores[supervisor["uuid"]][label] += float(score) 

    

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