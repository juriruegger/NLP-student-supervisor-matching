from transformers import BertTokenizer, BertModel
import torch
from transformers import AutoTokenizer, AutoModel
from adapters import AutoAdapterModel
from tqdm import tqdm

"""
This module provides functions to compute embeddings for supervisors using various models.
It includes functions for ModernBERT, BERT, SciBERT, and SPECTER2 models.
SPECTER 2 is also responsible for assigning embeddings to each abstract, enabling the top paper calculation, for each supervisor.
Note that ModernBERT handles both concatenated and averaged embeddings, and therefore is slower.
"""

def average_pooling(embeddings):
        return torch.mean(torch.stack(embeddings), dim=0)

modernbert_model_id = "answerdotai/ModernBERT-base"
modernbert_tokenizer = AutoTokenizer.from_pretrained(modernbert_model_id)
modernbert_model = AutoModel.from_pretrained(modernbert_model_id)

def get_modernbert_embeddings(supervisors):
    def embed(text):
        inputs = modernbert_tokenizer(text, max_length=8192, truncation=True, return_tensors="pt")
        with torch.no_grad():
            outputs = modernbert_model(**inputs)

        # Mean pooling for the entire text
        mask = inputs["attention_mask"].unsqueeze(-1)
        token_embeddings = outputs.last_hidden_state
        summed = (token_embeddings * mask).sum(dim=1)
        counts = mask.sum(dim=1)
        mean_pooled = summed / counts

        return mean_pooled.squeeze().detach() 
    
    for supervisor in tqdm(supervisors, desc="ModernBERT"):
        embeddings = []
        abstracts = supervisor.get('abstracts') or []
        concat_text = ""

        for abstract in abstracts:
            if not abstract:
                continue
            text = abstract.get('text', '')
            if not text:
                continue
            concat_text += text + " "
            embedding = embed(text)
            embeddings.append(embedding)

        concat_embedding = embed(concat_text)

        supervisor['modernbert_concatenated_embedding'] = concat_embedding.tolist()
        supervisor['modernbert_averaged_embedding'] = average_pooling(embeddings).tolist() if embeddings else []

        keywords = " ".join(supervisor.get("keywords") or [])
        embeddings_keywords = embed(keywords)

        concat_text_with_keywords = concat_text + " " + keywords
        concat_embeddings_with_keywords = embed(concat_text_with_keywords)

        supervisor['modernbert_concatenated_embedding_with_keywords'] = concat_embeddings_with_keywords.tolist()
        supervisor['modernbert_averaged_embedding_with_keywords'] = average_pooling(embeddings + [embeddings_keywords]).tolist() if embeddings else []
    
    return supervisors

bert_model_id = "bert-base-uncased"
bert_tokenizer = BertTokenizer.from_pretrained(bert_model_id)
bert_model = BertModel.from_pretrained(bert_model_id)

def get_bert_embeddings(supervisors):

    def embed(text):
        inputs = bert_tokenizer(
            text, 
            max_length=512, 
            padding="max_length", 
            truncation=True, 
            return_tensors="pt"
        )
        with torch.no_grad():
            outputs = bert_model(**inputs)

        # Mean pooling for the entire text
        mask = inputs["attention_mask"].unsqueeze(-1)
        token_embeddings = outputs.last_hidden_state
        summed = (token_embeddings * mask).sum(dim=1)
        counts = mask.sum(dim=1)
        mean_pooled = summed / counts 
        return mean_pooled.squeeze().detach() 

    for supervisor in tqdm(supervisors, desc="BERT"):
        embeddings = []
        abstracts = supervisor.get('abstracts') or []
        for abstract in abstracts:
            if not abstract:
                continue
            text = abstract.get('text', '')
            if not text:
                continue
            embedding = embed(text)
            embeddings.append(embedding)

        supervisor['bert_averaged_embedding'] = average_pooling(embeddings).tolist() if embeddings else []

        keywords = " ".join(supervisor.get("keywords") or [])
        embeddings_keywords = embed(keywords)
        supervisor['bert_averaged_embedding_with_keywords'] = average_pooling(embeddings + [embeddings_keywords]).tolist() if embeddings else []

    return supervisors

scibert_model_id = "allenai/scibert_scivocab_uncased"
scibert_tokenizer = BertTokenizer.from_pretrained(scibert_model_id)
scibert_model = BertModel.from_pretrained(scibert_model_id)

def get_scibert_embeddings(supervisors):
    def embed(text):
        inputs = scibert_tokenizer(
            text, 
            max_length=512, 
            padding='max_length', 
            truncation=True, 
            return_tensors="pt"
        )
        with torch.no_grad():
            outputs = scibert_model(**inputs)

        # Mean pooling for the entire text
        mask = inputs["attention_mask"].unsqueeze(-1)
        token_embeddings = outputs.last_hidden_state
        summed = (token_embeddings * mask).sum(dim=1)
        counts = mask.sum(dim=1)
        mean_pooled = summed / counts 
        return mean_pooled.squeeze().detach() 

    for supervisor in tqdm(supervisors, desc="SciBERT"):
        embeddings = []
        abstracts = supervisor.get('abstracts') or []

        for abstract in abstracts:
            if not abstract:
                continue
            text = abstract.get('text', '')
            if not text:
                continue
            embedding = embed(text)
            embeddings.append(embedding)

        supervisor['scibert_averaged_embedding'] = average_pooling(embeddings).tolist() if embeddings else []

        keywords = " ".join(supervisor.get("keywords") or [])
        embeddings_keywords = embed(keywords)
        supervisor['scibert_averaged_embedding_with_keywords'] = average_pooling(embeddings + [embeddings_keywords]).tolist() if embeddings else []

    return supervisors


specter_tokenizer = AutoTokenizer.from_pretrained('allenai/specter2_base')
specter_model = AutoAdapterModel.from_pretrained('allenai/specter2_base')
specter_model.load_adapter("allenai/specter2", source="hf", load_as="specter2", set_active=True)

def get_specter2_embeddings(supervisors):
    def embed(text):
        inputs = specter_tokenizer(
            text,
            truncation=True,
            max_length=512,
            padding='max_length',
            return_tensors="pt"
        )

        with torch.no_grad():
            outputs = specter_model(**inputs)

        mask = inputs["attention_mask"].unsqueeze(-1)
        token_embeddings = outputs.last_hidden_state
        summed = (token_embeddings * mask).sum(dim=1)
        counts = mask.sum(dim=1)
        mean_pooled = summed / counts 
        return mean_pooled.squeeze().detach() 

    for supervisor in tqdm(supervisors, desc="SPECTER 2"):
        embeddings = []
        abstracts = supervisor.get('abstracts') or []

        for abstract in abstracts:
            if not abstract:
                continue
            text = abstract.get("text", "")
            if not text:
                continue
            embedding = embed(text)
            embeddings.append(embedding)

            abstract['embedding'] = embedding.tolist() if embedding is not None else []

        supervisor['specter2_averaged_embedding'] = average_pooling(embeddings).tolist() if embeddings else []

        keywords = " ".join(supervisor.get("keywords") or [])
        embeddings_keywords = embed(keywords)
        supervisor['specter2_averaged_embedding_with_keywords'] = average_pooling(embeddings + [embeddings_keywords]).tolist() if embeddings else []

    return supervisors