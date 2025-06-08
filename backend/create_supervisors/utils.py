# Utils
import math

"""
Utility functions for processing supervisor data.
This module provides functions to extract keywords, abstracts, emails, and validate supervisor topics.
"""

def extract_keywords(obj):
    """
    Extract and normalize keywords from a supervisor's research data.
    """
    keywords = set()
    for keyWordGroup in obj.get("keywordGroups", []):
        if not isinstance(keyWordGroup, dict):
            continue
        for keywordObj in keyWordGroup.get("keywords", []):
            if not isinstance(keywordObj, dict):
                continue
            for keyword in keywordObj.get("freeKeywords", []):
                if isinstance(keyword, str) and keyword:
                    keyword = keyword.strip()
                    keywords.add(keyword.lower())
    return keywords

def extract_en_abstract(abstract_obj):
    """
    Extract English abstract text from abstract object.
    """
    if not isinstance(abstract_obj, dict):
        return ""
    return (abstract_obj.get("abstract", {}).get("en_GB", "") or "")

def extract_email(person):
    """
    Extract primary email address from person's organizational associations.
    """
    for association in person.get("staffOrganizationAssociations", []):
        emails = association.get("emails", [])
        if emails:
            email = emails[0].get("value")
            if email:
                return email
    return None

def valid_supervisor_topic(x):
    """
    Validate if a supervisor topic value is valid (not NaN or infinite).
    """
    return isinstance(x, (int, float)) and not (math.isnan(x) or math.isinf(x))