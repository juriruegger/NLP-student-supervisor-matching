from flask import Flask, request, jsonify
import numpy as np
from transformers import BertTokenizer, BertModel, pipeline
import torch
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

@app.route('/api', methods=['POST'])
def api():
    text = request.get_json().get('text')
    supervisors = request.get_json().get('supervisors')

    if not text or not supervisors:
        return jsonify({'error': 'Invalid input data'}), 400

    embedding = get_embedding(str(text))
    suggestions = calculate_suggestions(embedding, supervisors)
    return jsonify(suggestions)

def get_embedding(sentence):
        inputs = tokenizer(sentence, return_tensors='pt', truncation=False, padding=True)
        with torch.no_grad():
            outputs = model(**inputs)
        return outputs.last_hidden_state[:, 0, :].numpy()

def calculate_suggestions(embedding, supervisors):

    similarities = []

    for supervisor in supervisors:
        embedding_str_list = supervisor.get('embedding_bert_768', [])

        supervisor_embedding = np.array([float(x) for x in embedding_str_list]).reshape(1, -1)

        similarity = cosine_similarity(embedding, supervisor_embedding)[0][0]
        similarities.append({
            'supervisor': supervisor.get('name'),
            'email': supervisor.get('email'),
            'similarity': similarity
        })
    
    similarities.sort(key=lambda x: x['similarity'], reverse=True)

    return (similarities)

if __name__ == '__main__':
    app.run(debug=True)