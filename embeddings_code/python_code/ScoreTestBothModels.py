import pandas as pd
from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F

# Models and tokenizers
bert_tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
bert_model = AutoModel.from_pretrained("bert-base-uncased")
scibert_tokenizer = AutoTokenizer.from_pretrained("allenai/scibert_scivocab_uncased")
scibert_model = AutoModel.from_pretrained("allenai/scibert_scivocab_uncased")

# Load CSV file
professor_data = pd.read_csv("embeddings_code/embeddings/embeddings.csv")

# Extract and count occurrences of organizational units (better for data analysis)
org_unit_counts = {}
professor_data["organisational_units"].apply(
    lambda x: [
        org_unit_counts.update({unit: org_unit_counts.get(unit, 0) + 1})
        for unit in x.split(" // ")
    ]
)
valid_org_units = {unit for unit, count in org_unit_counts.items() if count >= 2}

# -----------------
# Helper functions
# -----------------
def embed_text(text, tokenizer, model):
    inputs = tokenizer(text, max_length=512, padding="max_length", truncation=True, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    embedding = torch.mean(outputs.last_hidden_state * inputs["attention_mask"].unsqueeze(-1), dim=1).squeeze()
    return embedding

def cosine_similarity(vec1, vec2):
    return F.cosine_similarity(vec1, vec2, dim=0).item()

# -----------------
# Student input texts (key-value)
# -----------------
student_texts = {
    "Panir Tözün":
    "I am deeply interested in Deep Learning Hardware Evaluation, particularly in understanding how hardware influences the performance of complex models. Exploring the challenges of long runtimes and optimizing performance aligns with my desire to contribute to projects that push the boundaries of computational efficiency. I am eager to work on projects that enhance our understanding of hardware's role in advancing deep learning.",

    "Roman Beck":
    "Blockchain-as-a-Service is an area that I find incredibly exciting, especially in terms of enabling companies to adopt blockchain technology efficiently. I am interested in bridging technological advancements and business needs, exploring blockchain's potential to transform industries through secure and scalable solutions.",

    "Andrzej Wasowski":
    "I am passionate about Software Modernization, particularly in converting legacy code to new architectures to improve efficiency and maintainability. I am interested in tackling complex code transformations that can bring modern, scalable solutions to legacy systems and enhance their performance.",

    "Rune Kristian Lundedal Nielsen":
    "My primary interest is in understanding the psychological impact of gaming, particularly the factors that contribute to gaming addiction. Researching gaming disorders aligns closely with my goal of exploring both the positive and negative effects of gaming on mental health. I am excited about the opportunity to contribute to projects that address these challenges through rigorous psychological research.",
    
    "Philippe Bonnet":
    "I am deeply interested in Cache-Conscious Data Structures, particularly in optimizing data access to improve performance. Developing efficient data management solutions and working on performance optimization projects resonate with my passion for pushing the boundaries of high-performance data structures.",

    "Toine Bogers":
    "Book Recommendation Systems are an area of great interest to me, especially in understanding how to leverage both professional and user-generated data to improve recommendations. I am eager to work on projects that use data-driven approaches to enhance users' discovery experiences and create more intuitive recommendation systems.",
    
    "Tom Jenkins":
    "I am passionate about leveraging technology for civic engagement and community building. Working on critical design and the use of cultural probes to understand user behaviors resonates with my goal to create technologies that encourage active civic participation. I would love the opportunity to collaborate on projects that emphasize ethical design and foster meaningful community engagement.",

    "Sebastian Risi":
    "I am deeply interested in the intersection of artificial intelligence and robotics, particularly in developing adaptive and creative machines. Research on computational evolution and deep learning aligns perfectly with my aspirations to create systems capable of lifelong learning and human collaboration. I am eager to contribute to projects that explore innovative AI applications in robotics and beyond.",

    "Peter Sestoft":
    "My passion lies in the development and implementation of programming languages, with a focus on functional and parallel paradigms. Working in this area resonates with my goal to design efficient and reliable software systems. I am enthusiastic about the opportunity to collaborate on projects that advance programming language theory and its practical applications.",

    "Vedran Sekara":
    "I am passionate about analyzing human behavior through data, especially with a focus on ethical considerations. Research on computational social science and algorithmic auditing inspires me to explore how large-scale behavioral data can be analyzed responsibly. I would love to work on projects that emphasize transparency, fairness, and ethical practices in the study of human behavioral data."
}

# -----------------
# 1) Embed all student texts
# -----------------
student_embeddings = {}
idx = 1
for prof_name, text in student_texts.items():
    student_embeddings[f"text {idx}"] = {
        "student_key": prof_name,  # store the original "key" (the student’s name)
        "bert": embed_text(text, bert_tokenizer, bert_model).detach(),
        "scibert": embed_text(text, scibert_tokenizer, scibert_model).detach()
    }
    idx += 1

# -----------------
# 2) Compute + save all professor scores to CSV
# -----------------
output_results = []

for _, row in professor_data.iterrows():
    professor_name = row["name"]
    professor_org_units = row["organisational_units"].split(" // ")

    # Convert stored string embeddings to tensors
    embedding_bert = torch.tensor(
        [float(x) for x in row["embedding_bert_768"].strip("[]").split(", ")],
        dtype=torch.float
    )
    embedding_scibert = torch.tensor(
        [float(x) for x in row["embedding_scibert_768"].strip("[]").split(", ")],
        dtype=torch.float
    )
    
    result = {"professor name": professor_name}
    
    # Calculate BERT & SciBERT similarities for each "text {N}"
    for text_label, emb_dict in student_embeddings.items():
        result[f"{text_label} bert score"] = cosine_similarity(emb_dict["bert"], embedding_bert)
        result[f"{text_label} scibert score"] = cosine_similarity(emb_dict["scibert"], embedding_scibert)
    
    # Mark relevant organizational units
    for unit in valid_org_units:
        result[unit] = 1 if unit in professor_org_units else 0
    
    output_results.append(result)

# Save to CSV
output_df = pd.DataFrame(output_results)
output_file = "embeddings_code/embeddings/test_results.csv"
output_df.to_csv(output_file, index=False)
print(f"Scores saved to {output_file}")

# -----------------
# 3) For each "text {N}", pick top 5 professors (BERT & SciBERT), store + print
# -----------------
top_5_matches = {}  # will store results keyed by text label

print("\n=== TOP 5 PROFESSOR MATCHES PER TEXT (Unique Professors) ===\n")

for text_label, emb_dict in student_embeddings.items():
    # Compute similarity lists
    bert_scores = []
    scibert_scores = []
    
    for _, row in professor_data.iterrows():
        embedding_bert = torch.tensor(
            [float(x) for x in row["embedding_bert_768"].strip("[]").split(", ")],
            dtype=torch.float
        )
        embedding_scibert = torch.tensor(
            [float(x) for x in row["embedding_scibert_768"].strip("[]").split(", ")],
            dtype=torch.float
        )
        bert_scores.append(cosine_similarity(emb_dict["bert"], embedding_bert))
        scibert_scores.append(cosine_similarity(emb_dict["scibert"], embedding_scibert))
    
    # Sort indices by score (descending)
    sorted_indices_bert = sorted(range(len(bert_scores)), key=lambda i: bert_scores[i], reverse=True)
    sorted_indices_scibert = sorted(range(len(scibert_scores)), key=lambda i: scibert_scores[i], reverse=True)
    
    # Collect top-5 BERT matches
    unique_bert_indices = []
    seen_bert_profs = set()
    for i in sorted_indices_bert:
        prof_name = professor_data.iloc[i]["name"]
        if prof_name not in seen_bert_profs:
            seen_bert_profs.add(prof_name)
            unique_bert_indices.append(i)
        if len(unique_bert_indices) == 5:
            break
    top_bert_matches = [professor_data.iloc[i]["name"] for i in unique_bert_indices]

    # Collect top-5 SciBERT matches
    unique_scibert_indices = []
    seen_scibert_profs = set()
    for i in sorted_indices_scibert:
        prof_name = professor_data.iloc[i]["name"]
        if prof_name not in seen_scibert_profs:
            seen_scibert_profs.add(prof_name)
            unique_scibert_indices.append(i)
        if len(unique_scibert_indices) == 5:
            break
    top_scibert_matches = [professor_data.iloc[i]["name"] for i in unique_scibert_indices]

    # Store top-5 matches in a dict
    top_5_matches[text_label] = {
        "student_key": emb_dict["student_key"],
        "bert": top_bert_matches,
        "scibert": top_scibert_matches
    }
    
    # Print results
    print(f"TEXT: {text_label} (corresponds to '{emb_dict['student_key']}')")
    print("  Top 5 BERT Matches:")
    for rank, prof in enumerate(top_bert_matches, start=1):
        print(f"    {rank}. {prof}")
    print("  Top 5 SciBERT Matches:")
    for rank, prof in enumerate(top_scibert_matches, start=1):
        print(f"    {rank}. {prof}")
    print("-" * 50)


# -----------------
# 4) Check how many times a given student name is in Top-1 / Top-5
#    across all texts.
# -----------------

# We will check each "text {N}" to see if the 'student_key'
# is the top-1 or in the top-5 for BERT and SciBERT

bert_top1_count = 0
bert_top5_count = 0
scibert_top1_count = 0
scibert_top5_count = 0

print("\n=== TOP-1 / TOP-5 MATCHES COUNT CHECK ===\n")

for text_label, matches_dict in top_5_matches.items():
    student_name = matches_dict["student_key"]   # e.g. "Roman Beck"
    top5_bert = matches_dict["bert"]             # top 5 from BERT
    top5_scibert = matches_dict["scibert"]       # top 5 from SciBERT
    
    # Check BERT
    if student_name in top5_bert:
        bert_top5_count += 1
        if student_name == top5_bert[0]:
            bert_top1_count += 1
    
    # Check SciBERT
    if student_name in top5_scibert:
        scibert_top5_count += 1
        if student_name == top5_scibert[0]:
            scibert_top1_count += 1

print(f"BERT Top-1 matches: {bert_top1_count}")
print(f"BERT Top-5 matches: {bert_top5_count}")
print(f"SciBERT Top-1 matches: {scibert_top1_count}")
print(f"SciBERT Top-5 matches: {scibert_top5_count}")
