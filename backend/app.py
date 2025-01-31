from flask import Flask, request, jsonify
import numpy as np
from transformers import AutoModel, AutoTokenizer
import torch
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

model_id = "answerdotai/ModernBERT-base"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModel.from_pretrained(model_id)

@app.route('/api', methods=['POST'])
def api():
    data = request.get_json()
    text = data.get('text')
    supervisors = data.get('supervisors')

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

    # Ensure `embedding` is 2D
    if len(embedding.shape) == 1:
        embedding = embedding.reshape(1, -1)

    for supervisor in supervisors:
        embedding_str_list = supervisor.get(f'embedding', [])

        if not embedding_str_list:
            continue

        try:
            supervisor_embedding = np.array([float(x) for x in embedding_str_list]).reshape(1, -1)
        except ValueError:
            continue

        if embedding.shape[1] != supervisor_embedding.shape[1]:
            continue

        similarity = cosine_similarity(embedding, supervisor_embedding).item()

        similarities.append({
            'supervisor': supervisor.get('uuid'),
            'email': supervisor.get('email', 'Email not provided'),
            'similarity': similarity
        })

    similarities.sort(key=lambda x: x['similarity'], reverse=True)

    return similarities[:5]

if __name__ == '__main__':
    app.run(debug=True)