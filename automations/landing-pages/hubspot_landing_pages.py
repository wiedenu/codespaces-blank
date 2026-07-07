"""Pull HubSpot landing pages and available analytics for analysis.

Reads HUBSPOT_TOKEN from landing-page.env (gitignored, not committed).
"""
import json
import sys
import urllib.request
import urllib.error
from datetime import date, timedelta
from pathlib import Path

ENV_PATH = Path(__file__).parent / "landing-page.env"
BASE_URL = "https://api.hubapi.com"


def load_token() -> str:
    for line in ENV_PATH.read_text().splitlines():
        line = line.strip()
        if line.startswith("HUBSPOT_TOKEN="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError(f"HUBSPOT_TOKEN not found in {ENV_PATH}")


def api_get(path: str, token: str, params: dict | None = None) -> dict:
    url = f"{BASE_URL}{path}"
    if params:
        query = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{url}?{query}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"GET {path} failed: {e.code} {body}") from e


def get_all_landing_pages(token: str) -> list[dict]:
    pages = []
    after = None
    while True:
        params = {"limit": 100}
        if after:
            params["after"] = after
        data = api_get("/cms/v3/pages/landing-pages", token, params)
        pages.extend(data.get("results", []))
        after = data.get("paging", {}).get("next", {}).get("after")
        if not after:
            break
    return pages


def get_landing_page_analytics(token: str, start: str, end: str) -> dict[str, dict]:
    """Returns {page_id: metrics} for the given date range."""
    params = {"start": start, "end": end}
    data = api_get("/analytics/v2/reports/landing-pages/total", token, params)
    return {b["breakdown"]: b for b in data.get("breakdowns", [])}


def main():
    token = load_token()

    end_date = date.today()
    start_date = end_date - timedelta(days=90)
    start = start_date.strftime("%Y%m%d")
    end = end_date.strftime("%Y%m%d")

    print("Pulling landing pages...")
    pages = get_all_landing_pages(token)
    print(f"Found {len(pages)} landing pages.")

    published = [p for p in pages if p.get("state") == "PUBLISHED_OR_SCHEDULED"]
    print(f"{len(published)} are published. Pulling analytics for {start}-{end}...\n")

    analytics_by_id = get_landing_page_analytics(token, start, end)

    summary = []
    for p in published:
        page_id = str(p.get("id"))
        metrics = analytics_by_id.get(page_id, {})
        row = {
            "id": page_id,
            "name": p.get("name"),
            "slug": p.get("slug"),
            "url": p.get("url"),
            "created": p.get("created"),
            "updated": p.get("updated"),
            "rawViews": metrics.get("rawViews", 0),
            "entrances": metrics.get("entrances", 0),
            "exits": metrics.get("exits", 0),
            "pageBounceRate": metrics.get("pageBounceRate"),
            "ctaViews": metrics.get("ctaViews", 0),
            "ctaClicks": metrics.get("ctaClicks", 0),
            "submissions": metrics.get("submissions", 0),
            "leads": metrics.get("leads", 0),
            "customers": metrics.get("customers", 0),
        }
        summary.append(row)

    summary.sort(key=lambda r: r["rawViews"], reverse=True)

    for row in summary[:20]:
        print(
            f"- {row['rawViews']:>6} views | {row['submissions']:>4} submissions | "
            f"{row['name']} -> {row['url']}"
        )

    out_path = Path(__file__).parent / "landing_pages_summary.json"
    out_path.write_text(json.dumps(summary, indent=2))
    print(f"\nSaved {len(summary)} published pages with analytics to {out_path}")


if __name__ == "__main__":
    main()
