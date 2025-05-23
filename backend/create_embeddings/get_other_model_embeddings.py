from transformers import BertTokenizer, BertModel
import torch
from transformers import AutoTokenizer
from adapters import AutoAdapterModel

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
    
    def average_pooling(embeddings):
        return torch.mean(torch.stack(embeddings), dim=0)

    for supervisor in supervisors:
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

    return supervisors

scibert_model_id = "allenai/scibert_scivocab_uncased"
scibert_tokenizer = BertTokenizer.from_pretrained(scibert_model_id)
scibert_model = BertModel.from_pretrained(scibert_model_id)

def get_scibert_embeddings(supervisors):

    def embed(text):
        inputs = scibert_tokenizer(
            text, 
            max_length=512, 
            padding=True, 
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
    
    def average_pooling(embeddings):
        return torch.mean(torch.stack(embeddings), dim=0)

    for supervisor in supervisors:
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

    return supervisors


specter_tokenizer = AutoTokenizer.from_pretrained('allenai/specter2_base')
specter_model = AutoAdapterModel.from_pretrained('allenai/specter2_base')

specter_model.load_adapter("allenai/specter2", source="hf", load_as="specter2", set_active=True)

def get_specter2_embeddings(supervisors):
    def embed(text):
        inputs = specter_tokenizer(
            text,
            padding=True,
            truncation=True,
            max_length=512,
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

    def average_pooling(embeddings):
        return torch.mean(torch.stack(embeddings), dim=0)

    for supervisor in supervisors:
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

        supervisor['specter2_averaged_embedding'] = average_pooling(embeddings).tolist() if embeddings else []

    return supervisors