from __future__ import annotations
from typing import List, Set

# starter list; extend as needed or load from a CSV later
SKILL_LIST = {
    "python","java","c++","c#","javascript","typescript","go","rust",
    "pandas","numpy","scikit-learn","tensorflow","pytorch","keras",
    "nlp","computer vision","opencv","transformers",
    "sql","postgresql","mysql","mongodb","redis","elasticsearch","spark",
    "docker","kubernetes","k8s","aws","gcp","azure","linux","git","ci/cd",
    "react","node","django","fastapi","flask","rest","graphql",
    "hadoop","airflow","kafka","tableau","power bi"
}

def extract_skills(text: str) -> List[str]:
    low = text.lower()
    found: Set[str] = set()
    for s in SKILL_LIST:
        if s in low:
            found.add(s)
    return sorted(found)

def diff_skills(required: List[str], present: List[str]):
    r = set(map(str.lower, required))
    p = set(map(str.lower, present))
    return sorted(p.intersection(r)), sorted(r - p)
