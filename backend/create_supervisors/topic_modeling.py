from collections import defaultdict
import os
import sys
from dotenv import load_dotenv
import joblib
from openai import OpenAI
from sklearn.feature_extraction.text import CountVectorizer
from adapters import AutoAdapterModel
from bertopic import BERTopic

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.create_supervisors.utils import extract_en_abstract, extract_keywords

"""
Here we create the topic modelling for the supervisors.
This is done by extracting the keywords from the researchers and optionally their research outputs,
and then using these keywords to create a topic model using BERTopic.
The topic model is then used to assign topics to the researchers based on their abstracts.
The topics are then deduplicated to ensure that there are no duplicate topics.
These topics are used for the student to match with the supervisors based on research interests.
"""

# Topic Modelling
load_dotenv("backend/.env.local")
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

specter_topic_model = AutoAdapterModel.from_pretrained('allenai/specter2_base')
specter_topic_model.load_adapter("allenai/specter2", source="hf", load_as="specter2", set_active=True)

used_labels = []

def generate_label(keywords):
    response = client.responses.create(
        model="gpt-4.1-mini", #Changed to gpt-4.1-mini from gpt-4o-mini for better performance
        instructions=(
            "You are given a cluster of keywords related to a research topic. "
            "Your task is to generate a concise, general and descriptive label for this topic based on the keywords provided."
            "The label should be between 1 and 3 words, capturing the research area that these keywords represent."
            "The labels are to be used for students to choose which research areas they want to work with."
            "The labels should be as broad, generic and easily understandable as possible."
            "Avoid uncommon or overly technical words."
            "The labels should be properly capitalized. So 'Machine Learning in Imaging' instead of 'machine learning in imaging'."
            "Output only the label text, no explanation."
            "Examples: Algorithms and Datastructures, Natural Language Processing, Game Design, Software Engineering."
        ),
        input=(f"Here are the keywords in the cluster: \"{', '.join(keywords)}\". "
        f"The following labels have already been used so choose another: \"{', '.join(used_labels)}\". "
        f"Labels are not to be reused."
        )
    )
    label = response.output_text.strip()
    used_labels.append(label)
    return label

def topic_modelling(researchers, all_researchers):
    # Getting possible keywords from all researchers and research outputs
    print("Topic modelling...") 
    all_keywords = set()
    for researcher in all_researchers:
        if not isinstance(researcher, dict):
            continue
        all_keywords.update(extract_keywords(researcher))

    print("Number of unique keywords in researchers:", len(all_keywords))

    """ for output in research_outputs:
        if not isinstance(output, dict):
            continue
        all_keywords.update(extract_keywords(output))

    print("Number of unique keywords:", len(all_keywords)) """

    docs = []
    doc_supervisors = []
    doc_abstracts = []

    for researcher in researchers:
        for abstract in researcher.get("abstracts", []):
            text = extract_en_abstract(abstract)
            if text:
                docs.append(text)
                doc_supervisors.append(researcher["uuid"])
                doc_abstracts.append(abstract)


    vectorizer = CountVectorizer(
        vocabulary = list(all_keywords),
        ngram_range = (1, 4),
        lowercase = True
    )

    joblib.dump(vectorizer, "vectorizer.joblib")

    topic_model = BERTopic(
        embedding_model=specter_topic_model,
        vectorizer_model=vectorizer,
        calculate_probabilities=True,
    )

    topics, probs = topic_model.fit_transform(docs)

    supervisor_topic_scores = defaultdict(lambda: defaultdict(float))

    for idx, prob_vec in enumerate(probs):
        topic_dict = {}
        for topic_id, score in enumerate(prob_vec):
            topic_dict[str(topic_id)] = float(score)

        doc_abstracts[idx]["topics"] = topic_dict

    for idx, supervisor_uuid in enumerate(doc_supervisors):
        topic_id = topics[idx]
        if topic_id == -1:
            continue
        score = probs[idx][topic_id]
        supervisor_topic_scores[supervisor_uuid][topic_id] += float(score)

    topics = {}
    supervisor_topics = []

    existing_labels = set()

    for researcher in researchers:
        tid_scores = supervisor_topic_scores.get(researcher["uuid"], {})
        top_tids = sorted(tid_scores, key=tid_scores.get, reverse=True)
        topic_ids = []
        
        for tid in top_tids:
            # get top n keywords for the topic
            n_keywords = 10
            keywords = [w for w, _ in topic_model.get_topic(tid)[:n_keywords]]
            label = generate_label(keywords)

            for i in range(n_keywords):
                if keywords[i] not in existing_labels:
                    label = keywords[i]
                    break

            existing_labels.add(label)

            topics[tid] = {               
                "topic_id": int(tid),
                "label": label,
                "keywords": keywords,
            }

            supervisor_topics.append({
                "uuid": researcher["uuid"],
                "topic_id": int(tid),
                "score": tid_scores[tid],
            })
            topic_ids.append(int(tid))
        researcher["topic_ids"] = topic_ids

    unique_pairs = {}
    for row in supervisor_topics:
        key = (row["uuid"], row["topic_id"])
        if key not in unique_pairs or row["score"] > unique_pairs[key]["score"]:
            unique_pairs[key] = row

    supervisor_topics = list(unique_pairs.values())
    
    unique_topics, supervisor_topics = deduplicate_topics(topics, supervisor_topics)

    unique_labeled_topics = unique_labels(unique_topics)

    return unique_labeled_topics, supervisor_topics

# Some topics can be duplicated, so we ensure they are unique
def deduplicate_topics(topics, supervisor_topics):
    key_to_correct_id = {}
    id_remap = {}
    unique = []
    for topic in topics.values():
        key = (topic["label"], tuple(topic["keywords"]))
        current_id = topic["topic_id"]
        if key not in key_to_correct_id:
            key_to_correct_id[key] = current_id
            unique.append(topic)
            continue

        correct_id = key_to_correct_id[key]
        id_remap[current_id] = correct_id

    for supervisor_topic in supervisor_topics:
        old_id = supervisor_topic["topic_id"]
        if old_id in id_remap:
            supervisor_topic["topic_id"] = id_remap[old_id]    

    return unique, supervisor_topics

def unique_labels(topics):
    used_labels = set()
    for topic in topics:
        label = topic.get("label")
        if label in used_labels or label == "":
            response = client.responses.create(
            model="gpt-4.1-mini",
            instructions=(
                "The label given already used in another topic. "
                "Your task is to provide a different label that is not already used. "
                "The label should capture the meaning of the keywords, but should not be the same as any of the existing labels. "
            ),
            input=(f"The label '{label}' is already used. Please provide a different label that is not already used. "
            f"The following labels have already been used: {', '.join(used_labels)}. "
            f"The label should be between 1 and 3 words, capturing the research area that these keywords represent. "
            f"The label is meant to represent these keywords: {', '.join(topic['keywords'])}. "
            f"Output only the label text, no explanation."
            )
            )
            label = response.output_text.strip()
            used_labels.add(label)
            topic["label"] = label
        else:
            used_labels.add(label)
    return topics
