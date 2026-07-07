"""Classify published landing pages into:
  - excluded_infra: team/contact sheets, generic team directory pages (no person name) -- not part of the analysis
  - vendor: named after a specific manufacturer/franchise/vendor partner
  - individual: named after a specific person (rep "Meet X" pages, "Contact Page - Lastname")
  - general: everything else (webinars, ebooks, thank-you pages, internal/test pages, etc.)
"""
import json
import re
from pathlib import Path

data = json.load(open("landing_pages_summary.json"))

EXCLUDED_PATTERNS = [
    r"contact sheet",
    r"team sheet",
]

# Generic regional/segment team contact pages or servicing-team directories
# with NO person name attached (these end cleanly without a trailing "- Name")
GENERIC_TEAM_CONTACT = re.compile(
    r"(contact page|servicing team|distribution team)\s*$",
    re.I,
)

VENDOR_KEYWORDS = [
    "ag leader", "yanmar", "whitecap", "leica", "skyjack", "topcon", "hcp retail",
    "hcp aramsco", "hcp sherwin-williams", "westernglobal", "icee", "hunter engineering",
    "hunter end-user", "chargepoint", "myers industries", "tke", "national tire wholesale",
    "trimble", "husqvarna", "adwerx", "napa", "kyocera", "toshiba", "ferguson", "carroll",
    "palo alto networks", "sophos", "fortinet", "nutanix", "jenne", "little caesars",
    "dominos", "jersey mike", "great clips", "firehouse", "marco's pizza", "marcos pizza",
    "marcos ghost kitchen", "dippin dots", "papa murphy", "smoothie king", "sports clips",
    "denny", "dairy queen", "dunkin", "qdoba", "tropical smoothie", "wingstop", "insitu",
    "dq coupon",
]

INDIVIDUAL_PATTERNS = [
    re.compile(r"meet (?!us\b)[a-z]+ [a-z]+", re.I),
    re.compile(r"contact page\s*-\s*[a-z' ]+$", re.I),  # e.g. "... Contact Page - Von Ahsen"
]


def classify(name: str) -> str:
    lname = name.lower().strip()

    if any(re.search(p, lname) for p in EXCLUDED_PATTERNS):
        return "excluded_infra"
    if any(p.search(name) for p in INDIVIDUAL_PATTERNS):
        return "individual"
    if GENERIC_TEAM_CONTACT.search(lname):
        return "excluded_infra"
    if any(kw in lname for kw in VENDOR_KEYWORDS):
        return "vendor"
    return "general"


buckets = {"excluded_infra": [], "vendor": [], "individual": [], "general": []}
for p in data:
    bucket = classify(p["name"])
    buckets[bucket].append(p)

for bucket, items in buckets.items():
    print(f"\n=== {bucket.upper()} ({len(items)}) ===")
    for p in items:
        print(f"  {p['name']}")

Path("landing_page_buckets.json").write_text(json.dumps(buckets, indent=2))
