import pandas as pd
from transformers import AutoTokenizer, AutoModel
import torch

# Load tokenizers and models
bert_tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
bert_model = AutoModel.from_pretrained("bert-base-uncased")

scibert_tokenizer = AutoTokenizer.from_pretrained("allenai/scibert_scivocab_uncased")
scibert_model = AutoModel.from_pretrained("allenai/scibert_scivocab_uncased")

# Load data
data = pd.read_csv("embeddings_code/researcher_data/CurrentFaculty_byRO_expanded.csv")
org_units_data = pd.read_csv("embeddings_code/researcher_data/CurrentFaculty_Person.csv")

# Remove rows with empty abstracts
data = data.dropna(subset=["Abstract"])

# Merge the two datasets on "Researcher name"
data = data.merge(
    org_units_data[["Researcher name", "Researcher UUID", "Organisational units"]],
    on="Researcher name",
    how="left"
)
data.rename(columns={"Researcher UUID_y": "Researcher UUID"}, inplace=True)

def embed_abstract(text, tokenizer, model):
    # Print length of the abstract in tokens
    tokens = tokenizer(text, add_special_tokens=False)["input_ids"]
    print(f"Abstract length (in tokens): {len(tokens)}")
    if len(tokens) > 512:
        print(f"Abstract exceeds 512 tokens, truncating: {len(tokens)} tokens")

    # Tokenize with truncation/padding up to 512 tokens
    inputs = tokenizer(
        text,
        max_length=512,
        truncation=True,
        padding="max_length",
        return_tensors="pt"
    )

    with torch.no_grad():
        outputs = model(**inputs)
    
    # Mean-pool the embeddings (masking out padded tokens)
    embeddings = outputs.last_hidden_state
    mask = inputs["attention_mask"].unsqueeze(-1)
    embedding = torch.sum(embeddings * mask, dim=1) / torch.sum(mask, dim=1)
    return embedding.squeeze().cpu().numpy()

rows = []
for i, row in data.iterrows():
    researcher_name = row["Researcher name"]
    # Reformat "Last, First" to "First Last"
    if ", " in researcher_name:
        last, first = researcher_name.split(", ")
        display_name = f"{first} {last}"
    else:
        display_name = researcher_name

    abstract = row["Abstract"]
    researcher_uuid = row["Researcher UUID"]
    organisational_units = row["Organisational units"]

    print(f"--- Processing researcher: {researcher_name} ---")

    # Get BERT & SciBERT embeddings
    bert_emb = embed_abstract(abstract, bert_tokenizer, bert_model)
    scibert_emb = embed_abstract(abstract, scibert_tokenizer, scibert_model)

    rows.append({
        "name": display_name,
        "researcher_name": researcher_name,
        "researcher_uuid": researcher_uuid,
        "organisational_units": organisational_units,
        "abstract": abstract,
        "embedding_bert_768": bert_emb.tolist(),
        "embedding_scibert_768": scibert_emb.tolist()
    })

# Convert results to DataFrame and save
output_df = pd.DataFrame(rows)
output_file = "embeddings_code/embeddings/abstract_embeddings.csv"
output_df.to_csv(output_file, index=False)

print(f"Embeddings for individual abstracts saved to {output_file}")
