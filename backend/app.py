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

@app.route('/api', methods=['POST'])
def api():
    data = request.get_json()
    text = data.get('text')
    response = supabase.table("supervisor").select("*").execute()
    supervisors = response.data

    if not text or not supervisors:
        return jsonify({'error': 'Invalid input data'}), 400

    embedding = get_embedding(str(text))
    suggestions = calculate_suggestions(embedding, supervisors)

    return jsonify(suggestions)

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
        embedding_str = supervisor.get('embedding', [])

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

if __name__ == '__main__':
    app.run(debug=True)