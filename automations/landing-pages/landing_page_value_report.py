"""Compare traffic/conversion performance: sales rep & account-support pages vs general marketing pages."""
import json
from pathlib import Path

buckets = json.load(open("landing_page_buckets.json"))

SUPPORT_BUCKETS = ["vendor", "individual"]
COMPARE_BUCKETS = ["general"]


def totals(pages: list[dict]) -> dict:
    t = {"count": len(pages), "rawViews": 0, "submissions": 0, "leads": 0, "customers": 0}
    zero_view = 0
    zero_submission_with_traffic = 0
    for p in pages:
        t["rawViews"] += p.get("rawViews", 0)
        t["submissions"] += p.get("submissions", 0)
        t["leads"] += p.get("leads", 0)
        t["customers"] += p.get("customers", 0)
        if p.get("rawViews", 0) == 0:
            zero_view += 1
        elif p.get("submissions", 0) == 0:
            zero_submission_with_traffic += 1
    t["zero_view_count"] = zero_view
    t["zero_submission_with_traffic_count"] = zero_submission_with_traffic
    return t


def report(label: str, bucket_names: list[str]):
    pages = [p for name in bucket_names for p in buckets[name]]
    t = totals(pages)
    print(f"\n=== {label} ({t['count']} pages) ===")
    print(f"  Total views (90d):       {t['rawViews']}")
    print(f"  Total submissions:       {t['submissions']}")
    print(f"  Total leads:             {t['leads']}")
    print(f"  Total customers:         {t['customers']}")
    print(f"  Pages with 0 views:      {t['zero_view_count']}")
    print(f"  Pages with traffic but 0 submissions: {t['zero_submission_with_traffic_count']}")
    if t["rawViews"] > 0:
        print(f"  Submission rate:         {t['submissions']/t['rawViews']*100:.2f}%")
    return pages, t


support_pages, support_totals = report("SALES REP / ACCOUNT SUPPORT PAGES", SUPPORT_BUCKETS)
general_pages, general_totals = report("GENERAL MARKETING PAGES", COMPARE_BUCKETS)

infra = buckets["excluded_infra"]
print(f"\n=== EXCLUDED: TEAM/CONTACT SHEETS ({len(infra)} pages, not evaluated) ===")

# Detail: support pages with zero traffic in the last 90 days -- candidates for retirement
print("\n--- Support pages with ZERO views in 90 days (retirement candidates) ---")
zero_traffic_support = sorted(
    [p for p in support_pages if p.get("rawViews", 0) == 0], key=lambda p: p["name"]
)
for p in zero_traffic_support:
    print(f"  {p['name']} -> {p['url']}")
print(f"  ({len(zero_traffic_support)} of {len(support_pages)} support pages, "
      f"{len(zero_traffic_support)/len(support_pages)*100:.0f}%)")

# Detail: top performing support pages
print("\n--- Top 15 support pages by views ---")
top_support = sorted(support_pages, key=lambda p: p.get("rawViews", 0), reverse=True)[:15]
for p in top_support:
    print(f"  {p.get('rawViews',0):>5} views | {p.get('submissions',0):>3} submissions | {p['name']}")

Path("landing_page_value_summary.json").write_text(json.dumps({
    "support_totals": support_totals,
    "general_totals": general_totals,
    "support_pages": support_pages,
    "general_pages": general_pages,
    "excluded_infra": infra,
}, indent=2))
