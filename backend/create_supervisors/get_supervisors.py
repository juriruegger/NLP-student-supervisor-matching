import os
from dotenv import load_dotenv
import requests

from backend.create_supervisors.utils import extract_en_abstract

def get_supervisors():
    """
    Fetches supervisors from the PURE API and filters them based on their job titles.
    Returns:
        A tuple containing two lists:
            - filtered_researchers: List of researchers who are allowed as supervisors.
            - all_researchers: List of all researchers fetched from the PURE API.
    """
    # PURE setup
    load_dotenv("backend/.env.local")

    PURE_API_KEY = os.environ.get("PURE_API_KEY")
    PURE_BASE_URL = os.environ.get("PURE_BASE_URL")

    # Get researchers from PURE API
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
    researchers = persons.get("items", [])
    all_researchers = researchers.copy() # all researcher will be used for the topic modelling vocabulary, so this should be unchanged

    # Filter researchers who are allowed as supervisors.
    allowed_titles = {
        "Associate Professor",
        "PhD fellow",
        "Assistant Professor",
        "Professor",
        "Postdoc",
        "Head of Section",
        "Head of PhD School",
        "Head of Studies",
        "Head of Study Programme",
        "Head of Center",
        "Deputy Head of Department",
        "Deputy Head of Center",
        "Co-head of study programme",
        "Co-head of Study Programme",
        "Co-head of PhD School",
        "Full Professor",
        "Full Professor, Head of PhD School",
        "Full Professor, Co-head of PhD School",
        "Full Professor, Head of Center",
        "Full Professor, Co-head of Center",
        "Full Professor, Deputy Head of Department",
        "Full Professor, Deputy Head of Center",
        "Full Professor, Head of Studies",
        "Full Professor, Head of Study Programme",
        "Full Professor, Co-head of Study Programme"
    }

    filtered_researchers = []
    for researcher in researchers:
        associations = researcher.get("staffOrganizationAssociations", [])
        for association in associations:
            title = association.get("jobTitle", {}).get("term", {}).get("en_GB")
            if title and title in allowed_titles:
                filtered_researchers.append(researcher)
                break

    # Get abstracts from PURE API
    research_outputs = []

    url = f"{PURE_BASE_URL}/research-outputs"
    headers = {
        "accept": "application/json", 
        "api-key": PURE_API_KEY,
    }
    params = {
        "size": 1,
        "order": "authorLastName",
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    # Getting the total number of research outputs
    count = data.get("count", 0)

    # Fetching the actual research outputs
    while len(research_outputs) < count:
        params = {
            "size": 1000,
            "offset": len(research_outputs),
            "order": "authorLastName",
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        research_outputs.extend(data.get("items", []))

    # Filter abstracts:
    filtered_abstracts = []
    for abstract in research_outputs:
        text = extract_en_abstract(abstract)
        if not text:
            continue
        if not abstract.get("contributors"):
            continue
        if not abstract.get("title"):
            continue
        valid_contributer = False
        for contributor in abstract.get("contributors", []):
            if not contributor.get("person"):
                continue
            if contributor["person"].get("uuid") in [researcher["uuid"] for researcher in filtered_researchers]:
                valid_contributer = True
                break
        if not valid_contributer:
            continue
        filtered_abstracts.append(abstract)

    # Associate abstracts with researchers
    researchers_with_abstracts = []
    for researcher in filtered_researchers:
        has_any_abstract = False
        researcher_abstracts = []
        for abstract in filtered_abstracts:
            for contributor in abstract.get("contributors", []):
                if not contributor.get("person"):
                    continue
                if contributor["person"].get("uuid") == researcher["uuid"]:
                    researcher_abstracts.append(abstract)
                    has_any_abstract = True
                    break
        if not has_any_abstract:
            continue

        researcher["abstracts"] = researcher_abstracts
        researchers_with_abstracts.append(researcher)

    researchers = researchers_with_abstracts

    return researchers, all_researchers