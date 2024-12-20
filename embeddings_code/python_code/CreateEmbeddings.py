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
data = pd.read_csv("embeddings_code/researcher_data/CurrentFaculty_byRO_expanded.csv")
org_units_data = pd.read_csv("embeddings_code/researcher_data/CurrentFaculty_Person.csv")

# Remove rows with empty abstracts
data = data.dropna(subset=["Abstract"])

# Merge the two datasets on "Researcher name"
data = data.merge(org_units_data[["Researcher name", "Researcher UUID", "Organisational units"]], 
                  on="Researcher name", 
                  how="left")


data.rename(columns={"Researcher UUID_y": "Researcher UUID"}, inplace=True)

# Debugging:
# print("Columns in merged data:")
# print(data.columns)

# Embed each abstract
def embed_abstract(text, tokenizer, model):
    tokens = tokenizer(text, add_special_tokens=False)["input_ids"]
    print(f"Abstract length (in tokens): {len(tokens)}")
    if len(tokens) > 512:
        print(f"Abstract exceeds 512 tokens, truncating: {len(tokens)} tokens")
    
    inputs = tokenizer(text, max_length=512, truncation=True, padding="max_length", return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)

    # Mean pooling for the entire text
    embedding = torch.mean(outputs.last_hidden_state * inputs["attention_mask"].unsqueeze(-1), dim=1)
    return embedding.squeeze().detach()

# Apply average mean pooling across embeddings for a single researcher
def average_pooling(embeddings):
    embeddings = torch.stack(embeddings)
    attention_weights = F.softmax(torch.ones(len(embeddings), 1), dim=0)  # Uniform weights
    pooled_embedding = torch.sum(embeddings * attention_weights, dim=0)
    return pooled_embedding

results = []

# Generate embeddings for each researcher
for researcher_name, group in data.groupby("Researcher name"):

    organisational_units = group["Organisational units"].iloc[0]
    researcher_uuid = group["Researcher UUID"].iloc[0]
    
    last_name, first_name = researcher_name.split(", ")
    formatted_name = f"{first_name} {last_name}"
    
    bert_embeddings = []
    scibert_embeddings = []
    for abstract in group["Abstract"]:
        bert_embedding = embed_abstract(abstract, bert_tokenizer, bert_model)
        scibert_embedding = embed_abstract(abstract, scibert_tokenizer, scibert_model)
        bert_embeddings.append(bert_embedding)
        scibert_embeddings.append(scibert_embedding)
    
    final_bert_embedding = average_pooling(bert_embeddings).squeeze().detach().cpu().numpy()
    final_scibert_embedding = average_pooling(scibert_embeddings).squeeze().detach().cpu().numpy()
    
    results.append({
        "name": formatted_name,
        "researcher_name": researcher_name,
        "researcher_uuid": researcher_uuid,
        "organisational_units": organisational_units,
        "embedding_bert_768": final_bert_embedding.tolist(),
        "embedding_scibert_768": final_scibert_embedding.tolist()
    })

# Save to CSV file
output_file = "embeddings_code/embeddings/embeddings.csv"
output_df = pd.DataFrame(results)
output_df.to_csv(output_file, index=False)

print(f"Embeddings with organisational units and UUIDs saved to {output_file}")
