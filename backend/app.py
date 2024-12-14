from flask import Flask, request, jsonify
import numpy as np
from transformers import BertTokenizer, BertModel
import torch
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

@app.route('/api', methods=['POST'])
def api():
    text = request.get_json().get('text')
    supervisors = request.get_json().get('supervisors')
    bert_model = request.get_json().get('model')

    if not text or not supervisors:
        return jsonify({'error': 'Invalid input data'}), 400

    embedding = get_embedding(str(text), str(bert_model))
    suggestions = calculate_suggestions(embedding, supervisors, bert_model)
    return jsonify(suggestions)

def get_embedding(sentence, bert_model):
    full_model = model_switch(bert_model)
    tokenizer = BertTokenizer.from_pretrained(full_model)
    model = BertModel.from_pretrained(full_model)
    
    inputs = tokenizer(sentence, max_length=512, padding="max_length", truncation=True, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    embedding = torch.mean(outputs.last_hidden_state * inputs["attention_mask"].unsqueeze(-1), dim=1).squeeze()
    return embedding

def calculate_suggestions(embedding, supervisors, model):
    similarities = []

    # Ensure `embedding` is 2D
    if len(embedding.shape) == 1:
        embedding = embedding.reshape(1, -1)

    for supervisor in supervisors:
        embedding_str_list = supervisor.get(f'embedding_{model}_768', [])

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

    return similarities

def model_switch(model):
    match model:
        case 'bert':
            return 'bert-base-uncased'
        case 'scibert':
            return 'allenai/scibert_scivocab_uncased'
        case _:
            raise ValueError('Unknown model')

if __name__ == '__main__':
    app.run(debug=True)