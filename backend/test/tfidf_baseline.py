from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def tfidf_baseline(supervisors, supervisors_db):
    reciprocal_ranks = []
    
    for supervisor in supervisors:
        for proposal in supervisor['proposals']:
            similarities = calculate_tfidf_similarities(proposal, supervisors_db)
            
            for rank, similarity in enumerate(similarities, 1):
                db_supervisor = similarity['supervisor']
                db_first_name = db_supervisor.get('name', {}).get('firstName', '')
                db_last_name = db_supervisor.get('name', {}).get('lastName', '')
                
                if db_first_name == supervisor['firstName'] and db_last_name == supervisor['lastName']:
                    reciprocal_ranks.append(1.0 / rank)
                    break
    
    mrr = sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0
    return mrr

def calculate_tfidf_similarities(query_text, supervisors_db):
    corpus = [query_text]
    supervisor_map = []
    
    for supervisor in supervisors_db:
        abstracts = supervisor.get('abstracts', [])
        if not abstracts:
            continue
        
        # Combine all abstracts for this supervisor
        supervisor_text = ""
        for abstract in abstracts:
            text = abstract.get('text', '')
            if text:
                supervisor_text += text + " "
        
        if supervisor_text:
            corpus.append(supervisor_text)
            supervisor_map.append(supervisor)
    
    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2)
    )
    tfidf_matrix = vectorizer.fit_transform(corpus)
    
    # Calculate similarities
    query_vector = tfidf_matrix[0:1]
    supervisor_vectors = tfidf_matrix[1:]
    
    # Handle case where no supervisors have abstracts
    if supervisor_vectors.shape[0] == 0:
        return []
    
    # Calculate cosine similarities
    similarity_scores = cosine_similarity(query_vector, supervisor_vectors).flatten()
    
    # Create results
    results = []
    for i, score in enumerate(similarity_scores):
        results.append({
            'supervisor': supervisor_map[i],
            'similarity': float(score)
        })
    
    # Sort by similarity
    results.sort(key=lambda x: x['similarity'], reverse=True)
    
    return results