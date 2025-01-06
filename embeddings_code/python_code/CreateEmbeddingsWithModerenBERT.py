import pandas as pd
from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F

# Models and tokenizers
bert_tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
bert_model = AutoModel.from_pretrained("bert-base-uncased")
scibert_tokenizer = AutoTokenizer.from_pretrained("allenai/scibert_scivocab_uncased")
scibert_model = AutoModel.from_pretrained("allenai/scibert_scivocab_uncased")
modernbert_tokenizer = AutoTokenizer.from_pretrained("answerdotai/ModernBERT-base")
modernbert_model = AutoModel.from_pretrained("answerdotai/ModernBERT-base")

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

# Generic embedding function
def embed_abstract(text, tokenizer, model):
    tokens = tokenizer(text, add_special_tokens=False)["input_ids"]
    print(f"Abstract length (in tokens): {len(tokens)}")
    if len(tokens) > 512:
        print(f"Abstract exceeds 512 tokens, truncating to 512 tokens.")

    inputs = tokenizer(text, max_length=512, truncation=True, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)

    # Mean pooling
    attention_mask = inputs["attention_mask"].unsqueeze(-1).expand(outputs.last_hidden_state.size())
    sum_embeddings = torch.sum(outputs.last_hidden_state * attention_mask, dim=1)
    sum_mask = torch.clamp(attention_mask.sum(dim=1), min=1e-9)
    embedding = sum_embeddings / sum_mask

    return embedding.squeeze()

# ModernBERT embedding function (no padding)
def embed_abstract_modernbert(text):
    inputs = modernbert_tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        outputs = modernbert_model(**inputs)

    # Mean pooling
    embedding = torch.mean(outputs.last_hidden_state, dim=1).squeeze()

    return embedding.squeeze()

# Average pooling across embeddings
def average_pooling(embeddings):
    embeddings = torch.stack(embeddings)
    pooled_embedding = torch.mean(embeddings, dim=0)
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
    modernbert_embeddings = []

    for abstract in group["Abstract"]:
        bert_embeddings.append(embed_abstract(abstract, bert_tokenizer, bert_model).cpu())
        scibert_embeddings.append(embed_abstract(abstract, scibert_tokenizer, scibert_model).cpu())
        modernbert_embeddings.append(embed_abstract_modernbert(abstract))

    final_bert_embedding = average_pooling(bert_embeddings).numpy()
    final_scibert_embedding = average_pooling(scibert_embeddings).numpy()
    final_modernbert_embedding = average_pooling(
        [torch.tensor(embed) for embed in modernbert_embeddings]
    ).numpy()

    results.append({
        "name": formatted_name,
        "researcher_name": researcher_name,
        "researcher_uuid": researcher_uuid,
        "organisational_units": organisational_units,
        "embedding_bert_768": final_bert_embedding.tolist(),
        "embedding_scibert_768": final_scibert_embedding.tolist(),
        "embedding_modernbert_768": final_modernbert_embedding.tolist()
    })

# Save to CSV file
output_file = "embeddings_code/embeddings/embeddingsWithModernBERT.csv"
output_df = pd.DataFrame(results)
output_df.to_csv(output_file, index=False)

print(f"Embeddings saved to {output_file}")
