from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def tfidf_baseline_with_keywords(supervisors, supervisors_db):
    """
    Baseline evaluation using TF-IDF vectorization and cosine similarity.
    
    Parameters:
        supervisors: List of supervisors with their proposals to evaluate
        supervisors_db: List of supervisor records from database with abstracts
        
    Returns:
        The Mean Reciprocal Rank score for the TF-IDF baseline approach
    """
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
    """
    Calculates TF-IDF similarities between query text and supervisor abstracts.
    """
    corpus = [query_text]
    supervisor_map = []
    
    for supervisor in supervisors_db:
        abstracts = supervisor.get('abstracts', [])
        keywords = supervisor.get('keywords', [])
        if not abstracts:
            continue

        supervisor_text = " ".join(keywords) + " " if keywords else ""
        for abstract in abstracts:
            text = abstract.get('text', '')
            if text:
                supervisor_text += text + " "
        
        if supervisor_text:
            corpus.append(supervisor_text)
            supervisor_map.append(supervisor)
    
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(corpus)
    
    query_vector = tfidf_matrix[0:1]
    supervisor_vectors = tfidf_matrix[1:]
    
    if supervisor_vectors.shape[0] == 0:
        return []
    
    similarity_scores = cosine_similarity(query_vector, supervisor_vectors).flatten()
    
    results = []
    for i, score in enumerate(similarity_scores):
        results.append({
            'supervisor': supervisor_map[i],
            'similarity': float(score)
        })
    
    results.sort(key=lambda x: x['similarity'], reverse=True)

    return results