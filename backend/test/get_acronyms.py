import os
from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd
import requests

load_dotenv("backend/.env.local")

PURE_API_KEY = os.environ.get("PURE_API_KEY")
PURE_BASE_URL = os.environ.get("PURE_BASE_URL")

person_url = f"{PURE_BASE_URL}/persons"
person_headers = {
    "accept": "application/json", 
    "api-key": PURE_API_KEY,
}
person_params = {
    "size": 1000,
    "order": "lastName",
}
response = requests.get(person_url, headers=person_headers, params=person_params)
response.raise_for_status()
persons = response.json()
supervisors = persons.get("items", [])


def extract_keywords(obj):
    keywords = []
    for keyWordGroup in obj.get("keywordGroups", []):
        if not isinstance(keyWordGroup, dict):
            continue
        for keywordObj in keyWordGroup.get("keywords", []):
            if not isinstance(keywordObj, dict):
                continue
            for keyword in keywordObj.get("freeKeywords", []):
                if isinstance(keyword, str) and keyword:
                    keyword = keyword.strip()
                    keywords.append(keyword.lower())
    return keywords

keywords_list = ""
for supervisor in supervisors:
    keywords = extract_keywords(supervisor)
    for keyword in keywords:
        keywords_list += keyword + ", "

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()
    
response = client.responses.create(
    model="gpt-4.1-mini",
    instructions=(
        'You are a helpful assistant. You are given a list of keywords. Your task is to identify the acronyms within this list of keywords such as NLP, AI, ML, etc. '
        'Please provide the acronyms in a comma-separated format. '
        'Only write each acronym once, even if it appears multiple times in the list. '
        'If there are no acronyms, please respond with "No acronyms found."'
        'Output nothing else.'
    ),
    input=keywords_list,
)

print(response.output_text)