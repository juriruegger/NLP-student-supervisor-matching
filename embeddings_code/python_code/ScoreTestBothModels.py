import pandas as pd
from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F

# Models and tokenizers
bert_tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
bert_model = AutoModel.from_pretrained("bert-base-uncased")
scibert_tokenizer = AutoTokenizer.from_pretrained("allenai/scibert_scivocab_uncased")
scibert_model = AutoModel.from_pretrained("allenai/scibert_scivocab_uncased")

# Load CSV files
professor_data = pd.read_csv("embeddings_code/embeddings/embeddings.csv")

# Extract and count occurrences of organizational units (better for data analysis)
org_unit_counts = {}
professor_data["organisational_units"].apply(
    lambda x: [org_unit_counts.update({unit: org_unit_counts.get(unit, 0) + 1}) for unit in x.split(" // ")]
)

valid_org_units = {unit for unit, count in org_unit_counts.items() if count >= 2}

# Embed text
def embed_text(text, tokenizer, model):
    inputs = tokenizer(text, max_length=512, padding="max_length", truncation=True, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    embedding = torch.mean(outputs.last_hidden_state * inputs["attention_mask"].unsqueeze(-1), dim=1).squeeze()
    return embedding

def cosine_similarity(vec1, vec2):
    return F.cosine_similarity(vec1, vec2, dim=0).item()

# Student input texts
student_texts = [

    #1 Panir Tözün
    "I am deeply interested in Deep Learning Hardware Evaluation, particularly in understanding how hardware influences the performance of complex models. Exploring the challenges of long runtimes and optimizing performance aligns with my desire to contribute to projects that push the boundaries of computational efficiency. I am eager to work on projects that enhance our understanding of hardware's role in advancing deep learning.",

    #2 Roman Beck
    "Blockchain-as-a-Service is an area that I find incredibly exciting, especially in terms of enabling companies to adopt blockchain technology efficiently. I am interested in bridging technological advancements and business needs, exploring blockchain's potential to transform industries through secure and scalable solutions.",

    #3 Andrzej Wasowski 
    "I am passionate about Software Modernization, particularly in converting legacy code to new architectures to improve efficiency and maintainability. I am interested in tackling complex code transformations that can bring modern, scalable solutions to legacy systems and enhance their performance.",

    #4 Rune Kristian Lundedal Nielsen
    "My primary interest is in understanding the psychological impact of gaming, particularly the factors that contribute to gaming addiction. Researching gaming disorders aligns closely with my goal of exploring both the positive and negative effects of gaming on mental health. I am excited about the opportunity to contribute to projects that address these challenges through rigorous psychological research.",
    
    #5 Philippe Bonnet
    "I am deeply interested in Cache-Conscious Data Structures, particularly in optimizing data access to improve performance. Developing efficient data management solutions and working on performance optimization projects resonate with my passion for pushing the boundaries of high-performance data structures.",

    #6 Toine Bogers 
    "Book Recommendation Systems are an area of great interest to me, especially in understanding how to leverage both professional and user-generated data to improve recommendations. I am eager to work on projects that use data-driven approaches to enhance users' discovery experiences and create more intuitive recommendation systems.",
    
    #7 Tom Jenkins
    "I am passionate about leveraging technology for civic engagement and community building. Working on critical design and the use of cultural probes to understand user behaviors resonates with my goal to create technologies that encourage active civic participation. I would love the opportunity to collaborate on projects that emphasize ethical design and foster meaningful community engagement.",

    #8 Sebastian Risi
    "I am deeply interested in the intersection of artificial intelligence and robotics, particularly in developing adaptive and creative machines. Research on computational evolution and deep learning aligns perfectly with my aspirations to create systems capable of lifelong learning and human collaboration. I am eager to contribute to projects that explore innovative AI applications in robotics and beyond.",

    #9 Peter Sestoft
    "My passion lies in the development and implementation of programming languages, with a focus on functional and parallel paradigms. Working in this area resonates with my goal to design efficient and reliable software systems. I am enthusiastic about the opportunity to collaborate on projects that advance programming language theory and its practical applications.",

    #10 Vedran Sekara
    "I am passionate about analyzing human behavior through data, especially with a focus on ethical considerations. Research on computational social science and algorithmic auditing inspires me to explore how large-scale behavioral data can be analyzed responsibly. I would love to work on projects that emphasize transparency, fairness, and ethical practices in the study of human behavioral data."
]

# Embed all student texts
student_embeddings = {
    f"text {idx + 1}": {
        "bert": embed_text(text, bert_tokenizer, bert_model).detach(),
        "scibert": embed_text(text, scibert_tokenizer, scibert_model).detach()
    }
    for idx, text in enumerate(student_texts)
}

output_results = []

# Compute scores for each professor
for _, row in professor_data.iterrows():
    professor_name = row["name"]
    professor_org_units = row["organisational_units"].split(" // ")
    
    embedding_bert = torch.tensor([float(x) for x in row["embedding_bert_768"].strip("[]").split(", ")], dtype=torch.float)
    embedding_scibert = torch.tensor([float(x) for x in row["embedding_scibert_768"].strip("[]").split(", ")], dtype=torch.float)
    
    result = {"professor name": professor_name}
    
    for text_label, embeddings in student_embeddings.items():
        result[f"{text_label} bert score"] = cosine_similarity(embeddings["bert"], embedding_bert)
        result[f"{text_label} scibert score"] = cosine_similarity(embeddings["scibert"], embedding_scibert)
    
    for unit in valid_org_units:
        result[unit] = 1 if unit in professor_org_units else 0
    
    output_results.append(result)

# Save as CSV
output_df = pd.DataFrame(output_results)
output_file = "embeddings_code/embeddings/test_results.csv"
output_df.to_csv(output_file, index=False)

print(f"Scores saved to {output_file}")
