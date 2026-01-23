import json
import re
from collections import Counter

INPUT_FILE = "all.json"

GOOD = []
NEEDS_FIX = []
CRITICAL = []

# ---------- RULE SETS ----------

BAD_PATTERNS = [
    r"is used for\?",
    r"stands for\?",
    r"who was .* year",
    r"who won",
    r"which scheme is",
    r"creator of .* stands for",
    r"expansion of .* is used for",
    r"full form of .* now is"
]

PEOPLE_NAMES = [
    "steve jobs", "bill gates", "linus torvalds",
    "jawaharlal nehru", "b r ambedkar", "mahatma gandhi"
]

SCHEME_KEYWORDS = [
    "scheme", "yojana", "mission", "abhiyan",
    "programme", "program", "ministry", "beneficiary", "launch"
]

# ---------- HELPERS ----------

def has_bad_pattern(question):
    q = question.lower()
    return any(re.search(p, q) for p in BAD_PATTERNS)

def duplicate_options(options):
    lowered = [o.strip().lower() for o in options]
    return len(lowered) != len(set(lowered))

def people_in_technical_options(options):
    joined = " ".join(o.lower() for o in options)
    return any(name in joined for name in PEOPLE_NAMES)

def scheme_domain_mismatch(domain, question):
    if domain.lower() != "gk" and "scheme" not in domain.lower():
        return False
    q = question.lower()
    return not any(k in q for k in SCHEME_KEYWORDS)

def invalid_structure(q):
    if not q.get("question"):
        return True
    if not isinstance(q.get("options"), list):
        return True
    if len(q["options"]) != 4:
        return True
    if not isinstance(q.get("answer_index"), int):
        return True
    if q["answer_index"] < 0 or q["answer_index"] > 3:
        return True
    return False

# ---------- MAIN ----------

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

for q in data:
    reasons = []

    question_text = q.get("question", "")
    options = q.get("options", [])
    domain = q.get("topic", "") or q.get("domain", "")

    if invalid_structure(q):
        q["_phase1_status"] = "critical_mismatch"
        q["_phase1_reason"] = ["invalid_structure"]
        CRITICAL.append(q)
        continue

    if duplicate_options(options):
        reasons.append("duplicate_option")

    if has_bad_pattern(question_text):
        reasons.append("bad_question_pattern")

    if people_in_technical_options(options):
        reasons.append("irrelevant_people_in_options")

    if scheme_domain_mismatch(domain, question_text):
        reasons.append("domain_topic_mismatch")

    if reasons:
        if "duplicate_option" in reasons or "domain_topic_mismatch" in reasons:
            q["_phase1_status"] = "critical_mismatch"
            q["_phase1_reason"] = reasons
            CRITICAL.append(q)
        else:
            q["_phase1_status"] = "needs_fix"
            q["_phase1_reason"] = reasons
            NEEDS_FIX.append(q)
    else:
        q["_phase1_status"] = "good"
        q["_phase1_reason"] = []
        GOOD.append(q)

# ---------- OUTPUT ----------

with open("good.json", "w", encoding="utf-8") as f:
    json.dump(GOOD, f, ensure_ascii=False, indent=2)

with open("needs_fix.json", "w", encoding="utf-8") as f:
    json.dump(NEEDS_FIX, f, ensure_ascii=False, indent=2)

with open("critical_mismatch.json", "w", encoding="utf-8") as f:
    json.dump(CRITICAL, f, ensure_ascii=False, indent=2)

print("PHASE 1 COMPLETE")
print("Good:", len(GOOD))
print("Needs Fix:", len(NEEDS_FIX))
print("Critical:", len(CRITICAL))
