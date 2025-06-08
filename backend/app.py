import json
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import numpy as np
from transformers import AutoTokenizer
from adapters import AutoAdapterModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
import os
from supabase import create_client, Client

"""
The backend application for the supervisor suggestion system.
This application uses the SPECTER 2 model to generate embeddings for the student text and
calculates cosine similarities to the supervisors embeddings, fetched from the database, 
to suggest supervisors based on user input.
It also supports topic-based suggestions by calculating the similarity of user-selected topics
to supervisors' topics in the database.
"""

app = Flask(__name__)

specter_tokenizer = AutoTokenizer.from_pretrained('allenai/specter2_base')
specter_model = AutoAdapterModel.from_pretrained('allenai/specter2_base')

specter_model.load_adapter("allenai/specter2", source="hf", load_as="specter2", set_active=True)

load_dotenv(".env.local")

url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

supabase: Client = create_client(url, key)

BATCH_SIZE = 25
offset = 0
supervisors = []

while True: # Fetching supervisors in batches
    response = (
        supabase.table("supervisor")
        .select("uuid", "specter2_averaged_embedding_with_keywords", "abstracts")
        .eq("available", True)
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

NUM_OF_SUPERVISORS = 5

@app.route('/api', methods=['POST'])
def api(): 
    """
    API endpoint to suggest supervisors based on project type and input data.
    Expects the following structure:
        projectType: "specific" or "general"
        - If "specific": 
            text: The project description text.
        - If "general": 
            topics: List of topics related to the project.
    Returns:
        - For "specific": JSON list of 6 supervisor suggestions based on text embedding similarity.
        - For "general": JSON list of up to 6 supervisor suggestions based on topic similarity, each with supervisor ID and similarity score.
        - On error: JSON object with an 'error' message and HTTP 400 status code.
    """
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
        top_suggestions = sorted_suggestions[:NUM_OF_SUPERVISORS]
        top_suggestions_with_top_paper = calculate_top_topic_paper(topics, top_suggestions, supervisors)
        final_suggestions = []
        for supervisor_id, score, top_paper in top_suggestions_with_top_paper:
            final_suggestions.append({
                'supervisor': supervisor_id,
                'similarity': score,
                'top_paper': top_paper,
            })
        return jsonify(final_suggestions)
    
    else:
        return jsonify({'error': 'Invalid project type'}), 400

def get_embedding(sentence):
    """
    Generates a mean-pooled embedding for a given sentence using the SPECTER model.
    """
    inputs = specter_tokenizer(sentence, max_length=8192, truncation=True, return_tensors="pt")
    with torch.no_grad():
        outputs = specter_model(**inputs)

    mask = inputs["attention_mask"].unsqueeze(-1)
    token_embeddings = outputs.last_hidden_state
    summed = (token_embeddings * mask).sum(dim=1)
    counts = mask.sum(dim=1)
    mean_pooled = summed / counts 

    return mean_pooled.squeeze().detach() 

def calculate_suggestions(embedding, supervisors):
    """
    Calculates and returns a list of supervisor suggestions based on the cosine similarity
    between a given embedding and each supervisor's embedding.

    Returns a list of dictionaries, each containing:
        - 'supervisor' (str): The UUID of the suggested supervisor.
        - 'similarity' (float): The cosine similarity score between the input embedding and the supervisor's embedding.
        - 'top_paper' (Any): The result of the calculate_top_paper function for the supervisor.
    """
    similarities = []

    # Ensure embedding is 2D
    if len(embedding.shape) == 1:
        embedding = embedding.reshape(1, -1)

    for supervisor in supervisors:
        embedding_str = supervisor.get('specter2_averaged_embedding_with_keywords', [])

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
    top_suggestions = similarities[:NUM_OF_SUPERVISORS]

    final_suggestions = []
    for suggestion in top_suggestions:
        supervisor = suggestion['supervisor']
        top_paper = calculate_top_embedding_paper(embedding, supervisor)
        final_suggestions.append({
            'supervisor': supervisor.get('uuid'),
            'similarity': suggestion['similarity'],
            'top_paper': top_paper
        })

    return final_suggestions

def calculate_top_embedding_paper(embedding, supervisor):
    """
    Calculates the most similar abstract for a given embedding from a supervisor's list of abstracts.

    Returns a dictionary with the 'uuid' and 'similarity' of the most similar abstract, or None if no valid abstracts are found.
    """
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
            'uuid': abstract.get('uuid'),
            'similarity': similarity,
        })

    similarities.sort(key=lambda x: x['similarity'], reverse=True)

    if similarities:
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        top_paper = similarities[0]
        return top_paper
    return None

def calculate_topic_suggestions(topics, supervisors_topic_db):
    """
    Calculates suggested supervisors based on the overlap between provided topics and a database of supervisor-topic associations.

    Returns a dictionary mapping supervisor UUIDs to their accumulated suggestion scores based on matching topics.
    """
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

def calculate_top_topic_paper(topics, top_suggestions, supervisors):
    """
    Calculates the most relevant paper for each supervisor based on the provided topics.
    """

    topic_ids = {int(topic['topicId']) for topic in topics}

    top_suggestions_with_papers = []

    for supervisor_id, score in top_suggestions:

        best_paper = {
            'uuid': None,
            'score': -1
        }

        supervisor_abstracts = []
        for supervisor in supervisors:
            if supervisor.get('uuid') == supervisor_id:
                supervisor_abstracts = supervisor.get('abstracts', [])
                break

        for abstract in supervisor_abstracts:
            abstract_score = 0
            for topic_id, topic_score in abstract.get('topics', {}).items():
                if int(topic_id) in topic_ids:
                    abstract_score += topic_score
                
            if abstract_score > best_paper['score']:
                best_paper = {
                    'uuid': abstract.get('uuid'),
                    'score': abstract_score
                }
        top_suggestions_with_papers.append((supervisor_id, score, best_paper))
    return top_suggestions_with_papers

if __name__ == '__main__':
    app.run(debug=True)