import os
import torch
import torch.nn.functional as F
from transformers import BertTokenizer, BertModel

# Load pre-trained BERT base model and tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

# Ensure we're using GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
model.eval()  # Set model to evaluation mode to disable dropout and other training-specific behavior

def embed_student_text(text):
    """Generate the embedding for the student text using BERT."""
    inputs = tokenizer(text, return_tensors="pt", max_length=512, truncation=True)
    inputs = {key: val.to(device) for key, val in inputs.items()}  # Move tensors to the same device as the model

    with torch.no_grad():
        outputs = model(**inputs)

    # Get the mean of the last hidden state (mean pooling), resulting in 768-dimensional embedding
    student_embedding = outputs.last_hidden_state.mean(dim=1).squeeze().cpu()
    return student_embedding

def resize_student_embedding(student_embedding, professor_embedding):
    """Resize student embedding to match the size of the professor embedding."""
    professor_size = professor_embedding.shape[0]
    student_size = student_embedding.shape[0]

    if student_size == professor_size:
        return student_embedding  # No resizing needed

    elif student_size < professor_size:
        # If the student embedding is smaller, repeat or pad it to match the professor's size
        repeat_times = professor_size // student_size
        resized_student_embedding = student_embedding.repeat(repeat_times)

        # If repeating didn't exactly match the size, trim or pad the rest
        if resized_student_embedding.shape[0] < professor_size:
            padding = professor_size - resized_student_embedding.shape[0]
            resized_student_embedding = torch.cat((resized_student_embedding, torch.zeros(padding)))

        return resized_student_embedding

    else:
        # If the student embedding is larger than the professor embedding, truncate it
        return student_embedding[:professor_size]

def calculate_cosine_similarity(student_embedding, professor_embedding):
    """Calculate the cosine similarity between two embeddings."""
    professor_embedding = professor_embedding.squeeze()

    # Resize the student embedding to match the professor embedding size
    resized_student_embedding = resize_student_embedding(student_embedding, professor_embedding)

    similarity_score = F.cosine_similarity(professor_embedding, resized_student_embedding, dim=0)
    return similarity_score.item()

def get_similarity_scores_for_professors(student_text, professor_embeddings_folder):
    """Calculate similarity scores between student text and pre-computed professor embeddings."""
    # Embed the student's text
    student_embedding = embed_student_text(student_text)

    similarities = []

    # Loop through all professor embeddings in the folder
    for file_name in os.listdir(professor_embeddings_folder):
        if file_name.endswith(".pt"):
            professor_path = os.path.join(professor_embeddings_folder, file_name)

            # Load pre-computed professor embedding
            professor_embedding = torch.load(professor_path)

            # Calculate cosine similarity
            similarity_score = calculate_cosine_similarity(student_embedding, professor_embedding)
            similarities.append((file_name, similarity_score))

    # Sort similarities in descending order
    similarities.sort(key=lambda x: x[1], reverse=True)

    # Output result
    for professor_file, score in similarities:
        print(f"Professor: {professor_file} - Cosine Similarity: {score}")

    return similarities

if __name__ == "__main__":
    # Example student text
    student_text = "I like AI and machine learning. Farms used in AI are also great for interesting research."

    # Path to the folder containing pre-computed professor embeddings
    professor_embeddings_folder = "NLP/professor_embeddings_bert_small"  # Change this to your embeddings folder path

    # Get and display similarity scores for all professors
    get_similarity_scores_for_professors(student_text, professor_embeddings_folder)
