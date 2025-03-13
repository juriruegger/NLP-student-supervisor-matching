import os

from dotenv import load_dotenv
import requests

load_dotenv("backend/.env.local")

PURE_API_KEY = os.environ.get("PURE_API_KEY")
PURE_BASE_URL = os.environ.get("PURE_BASE_URL")

print("PURE_API_KEY:", PURE_API_KEY)
print("PURE_BASE_URL:", PURE_BASE_URL)

person_url = f"{PURE_BASE_URL}/persons"
person_headers = {
    "accept": "application/json", 
    "api-key": PURE_API_KEY,
}
person_params = {
    "size": 2,
    "order": "lastName",
}
response = requests.get(person_url, headers=person_headers, params=person_params)
response.raise_for_status()
persons = response.json()
researchers = persons.get("items", [])

for researcher in researchers:
    for keyWordGroup in researcher.get("keywordGroups", []):
        if keyWordGroup.get("typeDiscriminator") == "FreeKeywordsKeywordGroup":
            for keywordObj in keyWordGroup.get("keywords", []):
                for keyword in keywordObj.get("freeKeywords", []):
                    if keyword:
                        print(f"Keyword: {keyword}")