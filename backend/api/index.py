import json
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import numpy as np
from transformers import AutoModel, AutoTokenizer
import torch
from sklearn.metrics.pairwise import cosine_similarity
import os
from supabase import create_client, Client

app = Flask(__name__)

model_id = "answerdotai/ModernBERT-base"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModel.from_pretrained(model_id)

load_dotenv(".env.local")

url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

supabase: Client = create_client(url, key)

BATCH_SIZE = 50
offset = 0
supervisors = []

while True: # Fetching supervisors in batches
    response = (
        supabase.table("supervisor")
        .select("*")
        .range(offset, offset + BATCH_SIZE - 1)
        .execute()
    )
    batch = response.data or []
    if not batch:
        break

    supervisors.extend(batch)
    offset += BATCH_SIZE

response = supabase.table("supervisor_topic").select("*").execute()
supervisors_topic_db = response.data

@app.route('/api', methods=['POST'])
def api(): 
    data = request.get_json()
    project_type = data.get('projectType')
    if project_type == "specific":
        text = data.get('text')
        if not text or not supervisors:
            return jsonify({'error': 'Invalid input data'}), 400

        embedding = get_embedding(str(text))
        suggestions = calculate_suggestions(embedding, supervisors)
        return jsonify(suggestions)
    
    elif project_type == "general":
        topics = data.get('topics')
        if not topics:
            return jsonify({'error': 'Invalid input data'}), 400

        suggestions = calculate_topic_suggestions(topics, supervisors_topic_db)
        sorted_suggestions = sorted(suggestions.items(), key=lambda x: x[1], reverse=True)
        top_suggestions = sorted_suggestions[:5]
        final_suggestions = []
        for supervisor_id, score in top_suggestions:
            final_suggestions.append({
                'supervisor': supervisor_id,
                'similarity': score
            })
        return jsonify(final_suggestions)
    
    else:
        return jsonify({'error': 'Invalid project type'}), 400

def get_embedding(sentence):
    inputs = tokenizer(sentence, max_length=8192, truncation=True, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    embedding = torch.mean(outputs.last_hidden_state * inputs["attention_mask"].unsqueeze(-1), dim=1).squeeze()
    return embedding

def calculate_suggestions(embedding, supervisors):
    similarities = []

    # Ensure embedding is 2D
    if len(embedding.shape) == 1:
        embedding = embedding.reshape(1, -1)

    for supervisor in supervisors:
        embedding_str = supervisor.get('averaged_embedding', [])

        if not embedding_str:
            continue

        embedding_list = json.loads(embedding_str)

        try:
            supervisor_embedding = np.array([float(x) for x in embedding_list]).reshape(1, -1)
        except ValueError:
            print('Error parsing supervisor embedding')
            continue


        if embedding.shape[1] != supervisor_embedding.shape[1]:
            continue

        similarity = cosine_similarity(embedding, supervisor_embedding).item()

        similarities.append({
            'supervisor': supervisor,
            'similarity': similarity,
        })

    similarities.sort(key=lambda x: x['similarity'], reverse=True)
    top_suggestions = similarities[:5]

    final_suggestions = []
    for suggestion in top_suggestions:
        supervisor = suggestion['supervisor']
        top_paper = calculate_top_paper(embedding, supervisor)
        final_suggestions.append({
            'supervisor': supervisor.get('uuid'),
            'similarity': suggestion['similarity'],
            'top_paper': top_paper
        })


    return final_suggestions

def calculate_top_paper(embedding, supervisor):
    abstracts = supervisor.get('abstracts', [])

    if not abstracts:
        return None

    similarities = []

    for abstract in abstracts:
        abstract_embedding = abstract.get('embedding', [])
        if not abstract_embedding:
            continue

        try:
            abstract_embedding = np.array([float(x) for x in abstract_embedding]).reshape(1, -1)
        except ValueError:
            print('Error parsing abstract embedding')
            continue

        if embedding.shape[1] != abstract_embedding.shape[1]:
            continue

        similarity = cosine_similarity(embedding, abstract_embedding).item()
        similarities.append({
            'title': abstract.get('title'),
            'url': abstract.get('url'),
            'similarity': similarity
        })

    similarities.sort(key=lambda x: x['similarity'], reverse=True)

    top_paper = similarities[0]

    return top_paper

def calculate_topic_suggestions(topics, supervisors_topic_db):
    suggested_supervisors = {}

    for supervisor_topic in supervisors_topic_db:
        supervisor_id = supervisor_topic.get('uuid')
        if not supervisor_id:
            continue

        for topic in topics:
            topic_id = topic.get('topicId')

            if supervisor_topic.get('topic_id') == topic_id:
                supervisor_score = supervisor_topic.get('score', 0)
                suggested_supervisors[supervisor_id] = suggested_supervisors.get(supervisor_id, 0) + supervisor_score

    return suggested_supervisors


if __name__ == '__main__':
    app.run(debug=True)