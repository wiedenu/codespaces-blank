#!/usr/bin/env python3
"""
GreatAmerica.com Website Performance Report
Pulls GA4, GSC, and HubSpot data and generates a static HTML report.

Usage:
  python report.py                            # all standard ranges
  python report.py --output path/to/out.html  # custom output path
  python report.py --start 2026-01-01 --end 2026-01-31  # adds custom range

Required env vars:
  GOOGLE_CLIENT_ID
  GOOGLE_CLIENT_SECRET
  GOOGLE_REFRESH_TOKEN
  HUBSPOT_API_TOKEN
"""

import json
import os
import sys
import argparse
from datetime import date, timedelta, datetime
from pathlib import Path

import requests

GA4_PROPERTY_ID     = "338447662"
PSG_GA4_PROPERTY_ID = "484841062"
IRH_GA4_PROPERTY_ID = "324284248"

GSC_SITE_URL     = "https://www.greatamerica.com/"
PSG_GSC_SITE_URL = "https://www.portfolioservicesgroup.com"
IRH_GSC_SITE_URL = "https://www.irhcapital.com"

GOOGLE_SCOPES   = [
    "https://www.googleapis.com/auth/analytics.readonly",
    "https://www.googleapis.com/auth/webmasters.readonly",
]
GA_DOMAINS  = ["greatamerica.com", "hsforms.com", "meetings.hubspot.com", "app.hubspot.com"]
PSG_DOMAINS = ["portfolioservicesgroup.com"]
IRH_DOMAINS = ["irhcapital.com"]
EXCLUDE_DOMAINS = ["accountservicing.com"]

# Maps form GUID → site key. Only forms listed here are counted.
# Any form not in this map is silently skipped (events, internal tools, blog comments, etc.).
FORM_SITE_MAP = {
    # ---- GreatAmerica ----
    "b8712de9-4782-42f1-a9da-f81d062dfb9c": "greatamerica",  # [IM] Website Contact Us / Get In Touch
    "3f033e05-269a-471e-aaec-168f8c7328f5": "greatamerica",  # CTG - Progressive Profiling Form
    "46ca72be-07c1-4c68-965c-8387d69a3543": "greatamerica",  # CTG Form Simple
    "bd001f88-bc64-432c-8787-b5d5b8406d79": "greatamerica",  # CTG - Generic Digital VIR
    "77a22ef4-85b1-4780-8d67-33da55bb38e8": "greatamerica",  # OEG - Simple Download Form
    "8dc456aa-2ba0-41c7-896c-9f4578b19290": "greatamerica",  # CTG Form Simple (copy)
    "0d6b2767-7f8f-4457-9099-7fea5a15bbdb": "greatamerica",  # Basic Download Form
    "e5b576ab-2bc9-4286-81a2-dcfa0fbeee94": "greatamerica",  # CTG BOFU Contact Us
    "b6119e37-b28e-4a61-b136-064c4b30dabe": "greatamerica",  # CDG - AV AMP Progressive Profiling
    "b68abac5-b0cf-4d75-ad4b-d975a614d441": "greatamerica",  # Husqvarna cash box
    "495543f8-2461-4e0f-8b81-d7be0c09c443": "greatamerica",  # Contact Us - HR
    "f7ed879c-1911-41a9-b447-5dce8b01b77e": "greatamerica",  # OEG Blog Subscribe
    "c677884e-11be-4d93-a243-47a73ca7d1b1": "greatamerica",  # CDG Newsletter Subscribe
    "1b09d2be-f52a-4383-86f5-ba4e62ec959c": "greatamerica",  # [IM] Office - BOFU Contact
    "6de243ec-010d-4ec5-aded-1808fff97978": "greatamerica",  # NAPA giveaway
    "50da052d-c53b-41f4-9434-31c4a68981ba": "greatamerica",  # CTG - About You
    "652213da-e89b-45a5-bf02-9e8eb33f0793": "greatamerica",  # SMG - Contact Us
    "011373e2-3820-4183-a374-634231a65f8b": "greatamerica",  # AG [LP] - Commodore Contact Us
    "72786b14-b3bc-413f-b4ea-45ac66c0e8ef": "greatamerica",  # OEG - B2B Toolbox Webinar Registrations
    "b52d2222-ba88-4586-bf95-8343b476a6d2": "greatamerica",  # ACTION REQUIRED: SnappShot Activation
    "64fb0279-1f21-4248-b7e2-e5e1c448375b": "greatamerica",  # OEG - State of the 2021 Technology Buyer
    "a61b474c-ec14-4046-b6a7-598364b2dbd6": "greatamerica",  # [IM] Website Integrations BOFU
    "41c522af-216c-4f83-829a-9ef7c4471b03": "greatamerica",  # OEG - Dealer MPSecure White Paper
    "2f2121d0-604a-4000-af01-b4175cf60cf7": "greatamerica",  # OEG - Tech Sales Hub
    "376c1cac-8c80-4e43-8849-f48f4745eba5": "greatamerica",  # SMG - AAP Dealer Summit Giveaway
    "4d6e5dc6-520e-4c46-ac3d-50fa08e95279": "greatamerica",  # PathShare - Quick Culture Assessment
    "1f4501e9-a845-408b-94a5-e2123002484e": "greatamerica",  # PathShare - Website Contact Us Form
    "1ca1d874-68db-4ca5-877e-7ca0e83de195": "greatamerica",  # Resubscribe Form
    "44c03960-7936-410f-a1d7-ad4bddd4c67c": "greatamerica",  # EVENT - OEG Operational Efficiency Workshop
    "11b5d6f6-ca87-4067-aa99-40e57d6c2c15": "greatamerica",  # SMG - Commodore Auto Care Giveaway
    "32491f87-4c6f-499b-b8da-156794c04175": "greatamerica",  # OEG - Financing Checklist (TaaS)
    "cc12fe60-cddb-458f-9bbe-1dce6a37028c": "greatamerica",  # Schedule a FREE Technology Review
    "72579319-0677-403b-82a6-3fd7cccff637": "greatamerica",  # OEG - Let's Connect (customers)
    "5c4a3fc2-0892-4b26-a813-8c317572084e": "greatamerica",  # OEG - Let's Connect
    "929ab259-cfd9-4460-ab60-3ef045395bcc": "greatamerica",  # SMG - HC Contact Us Form
    "f6145c82-d8b9-404e-b70a-bf418280075c": "greatamerica",  # SMG - C&I ICEE Contact Us
    "0caebb89-aab7-4064-aa1e-fcf8b8605fc5": "greatamerica",  # SMG - Simple form ChargePoint
    "bafd8551-cfce-4ebc-8687-e89e4bc37c51": "greatamerica",  # CTG - Service Provider White Paper
    "11d01c5a-5d8b-42ab-9941-1dbf70c1920b": "greatamerica",  # AG & SMG - Lease Process Contact Us
    "40cf7046-8ca0-463a-bc77-1e0c685080c5": "greatamerica",  # SMG - National Concrete Equipment Lead
    "d52aa5ea-1362-465b-b4eb-5df0928d8cf4": "greatamerica",  # OEG - Download 5 Pillars of Trust
    "131c64a7-4f44-4d91-add9-8d8fb5ee41f4": "greatamerica",  # OEG - 1nVOICE Whitepaper Download
    "be1c0dec-65cf-472a-9574-535d4b9f7c46": "greatamerica",  # Schedule a FREE Technology Review (EtGD)
    "222ec25b-ead1-4b96-9068-30c2797627a2": "greatamerica",  # OEG - Program and Lease Review Checklist
    "90e83e35-5920-4b43-9a81-6cbb7f2c5a10": "greatamerica",  # OEG - HaaR Relaunch Opportunity Calculator
    "5e7f4f2a-3883-4473-a1c0-90a11d9bb5e2": "greatamerica",  # CTG - NSCA BLC Giveaway
    "6d95befd-e13a-4d55-a976-75f468216bc5": "greatamerica",  # AG - Hunter Contact Us Form
    "465e3a47-e563-4e75-911d-b787994d14ee": "greatamerica",  # CTG - MVNO Giveaway
    "cdf0ab0c-c250-4579-a76c-6d0bb50a9387": "greatamerica",  # New blank form (Feb 2026)
    "92a4b657-6edd-4763-b67f-14cbd149e690": "greatamerica",  # CTG - Climb
    "b358e058-48d7-421f-bce9-2d79493cdda7": "greatamerica",  # CTG - Defy Security
    "062e12db-fbbe-4090-8e5c-a2221974242c": "greatamerica",  # Point S Meeting 2026
    "b7a302e6-597b-47d0-9040-fe4254e83572": "greatamerica",  # New blank form (Dec 2025)
    "be430d15-f8f3-4293-8ffc-e4a6d9c5ad12": "greatamerica",  # SMG - HC Landing Page
    "fe861a2e-9918-4111-86e7-0e9a3a807d9c": "greatamerica",  # SMG - Car Wash Show Giveaway
    "15f31f77-2fac-41e9-8148-7aecfe036fde": "greatamerica",  # AG - Commodore Contact Us
    "8f606150-b0df-4bc9-93f9-df039567ce2a": "greatamerica",  # SMG - C&I TKE Contact Us
    "1c1324fc-c928-44e3-8dd4-627a37f809ae": "greatamerica",  # SMG - Skyjack Marketing
    "36da0aa7-86cf-4a90-b197-7569500441e1": "greatamerica",  # OEG - Billing Pains CTA
    "de9f5b5e-54f2-4fe3-b18a-a1beb2d6f667": "greatamerica",  # CTG - giveaway form
    # ---- PSG ----
    "791c6de4-0ad9-4b5f-8650-96bd4b448161": "psg",           # GPSG - Contact Us Form
    # ---- IRH Capital ----
    "27bdac69-9733-41d3-a313-50575865abad": "irhcapital",    # IRH - Landing Page Form
    "c2544f55-849a-47db-b8b5-cbf9c125ee95": "irhcapital",    # IRH - Online Application
    "e451200d-bf45-4a83-a45e-a67eb930071e": "irhcapital",    # IRH - Contact Us
    "f4fc4c12-0779-4281-a86e-d8f70aca29d2": "irhcapital",    # IRH - Great Clips (Coupon)
    "2286aaf2-e982-46a1-9838-abf7ce941420": "irhcapital",    # IRH - Landing Page Tradeshow
    "8eef58d5-539a-4979-9676-3eeb5e55f121": "irhcapital",    # IRH - Firehouse Fryer
    "ffa77294-ae14-45e8-bbb8-eedea384363e": "irhcapital",    # IRH - Default Form
    "cdeddaaa-a918-472e-a222-71f0d1b306f9": "irhcapital",    # IRH - INSITU Form
    "40999ded-b0ca-4e86-923b-b36474004115": "irhcapital",    # IRH Elev8 Form
    "253a0cf3-4f71-40ee-8566-f38307950ac7": "irhcapital",    # IRH - Online Application lc
    "05686b91-7cbb-4a4a-b5c9-8d52280d4ec0": "irhcapital",    # IRH - General for Landing Page
    "e3f3d7e6-50b4-4888-b5c3-0d3fa4b8f5e3": "irhcapital",    # IRH - New Builds Program
    "dff9ff91-a4b6-427f-8255-66bc561d811d": "irhcapital",    # IRH LinkedIn Feb 2026 Form
    "60d5f0e3-d62c-4bb8-a196-3bcea4ae97f2": "irhcapital",    # IRH - Online Application LinkedIn Ads
    "f849ad17-1da3-4388-bc2b-a885f6bc4e66": "irhcapital",    # IRH - Marcos Ghost Form
    "d1ef7215-8320-4c3a-8af9-dedaa09a344a": "irhcapital",    # IRH - Sports Clips Barber Chairs Program
}

STANDARD_RANGES = [
    ("last_7_days",    "Last 7 Days",    7),
    ("last_28_days",   "Last 28 Days",   28),
    ("last_30_days",   "Last 30 Days",   30),
    ("last_90_days",   "Last 90 Days",   90),
    ("last_12_months", "Last 12 Months", 365),
]


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def google_credentials():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request

    creds = Credentials(
        token=None,
        refresh_token=os.environ["GOOGLE_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["GOOGLE_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
        scopes=GOOGLE_SCOPES,
    )
    creds.refresh(Request())
    return creds


# ---------------------------------------------------------------------------
# Data fetchers
# ---------------------------------------------------------------------------

def fetch_gsc(creds, start: str, end: str, site_url: str = None) -> dict:
    from googleapiclient.discovery import build
    svc = build("searchconsole", "v1", credentials=creds)
    url = site_url or GSC_SITE_URL

    def q(dims):
        return svc.searchanalytics().query(
            siteUrl=url,
            body={"startDate": start, "endDate": end, "dimensions": dims, "rowLimit": 500},
        ).execute()

    totals_resp = q([])
    daily_resp  = q(["date"])

    t = totals_resp.get("rows", [{}])[0]
    return {
        "impressions":  int(t.get("impressions", 0)),
        "clicks":       int(t.get("clicks", 0)),
        "ctr":          round(float(t.get("ctr", 0)) * 100, 2),
        "avg_position": round(float(t.get("position", 0)), 1),
        "daily": [
            {
                "date":        row["keys"][0],
                "impressions": int(row.get("impressions", 0)),
                "clicks":      int(row.get("clicks", 0)),
            }
            for row in daily_resp.get("rows", [])
        ],
    }


def fetch_ga4(creds, start: str, end: str, property_id: str = None) -> dict:
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric, Dimension

    client = BetaAnalyticsDataClient(credentials=creds)
    dr = DateRange(start_date=start, end_date=end)
    prop = f"properties/{property_id or GA4_PROPERTY_ID}"

    totals = client.run_report(RunReportRequest(
        property=prop,
        metrics=[
            Metric(name="sessions"),
            Metric(name="engagedSessions"),
            Metric(name="averageSessionDuration"),
        ],
        date_ranges=[dr],
    ))

    daily = client.run_report(RunReportRequest(
        property=prop,
        dimensions=[Dimension(name="date")],
        metrics=[Metric(name="sessions"), Metric(name="engagedSessions")],
        date_ranges=[dr],
    ))

    r = totals.rows[0] if totals.rows else None
    return {
        "sessions":         int(r.metric_values[0].value) if r else 0,
        "engaged_sessions": int(r.metric_values[1].value) if r else 0,
        "avg_duration_sec": round(float(r.metric_values[2].value)) if r else 0,
        "daily": [
            {
                "date": "{}-{}-{}".format(
                    row.dimension_values[0].value[:4],
                    row.dimension_values[0].value[4:6],
                    row.dimension_values[0].value[6:],
                ),
                "sessions":         int(row.metric_values[0].value),
                "engaged_sessions": int(row.metric_values[1].value),
            }
            for row in sorted(daily.rows, key=lambda x: x.dimension_values[0].value)
        ],
    }


TRACKED_SOURCES = [
    "ORGANIC_SEARCH",
    "DIRECT_TRAFFIC",
    "EMAIL_MARKETING",
    "REFERRALS",
    "SOCIAL_MEDIA",
    "PAID_SEARCH",
    "OTHER_CAMPAIGNS",
]

SITE_CONFIGS = [
    {"key": "greatamerica", "domains": GA_DOMAINS,  "ga4_id": GA4_PROPERTY_ID,     "gsc_url": GSC_SITE_URL},
    {"key": "psg",          "domains": PSG_DOMAINS, "ga4_id": PSG_GA4_PROPERTY_ID, "gsc_url": PSG_GSC_SITE_URL},
    {"key": "irhcapital",   "domains": IRH_DOMAINS, "ga4_id": IRH_GA4_PROPERTY_ID, "gsc_url": IRH_GSC_SITE_URL},
]


def build_fg(domains: list) -> list:
    """HubSpot filterGroups for hs_analytics_first_url matching any of domains.
    Returns [] (no filter) when domains is empty/None.
    OR between groups; each group is date + one domain (AND).
    """
    if not domains:
        return []
    return [
        {"filters": [{"propertyName": "hs_analytics_first_url", "operator": "CONTAINS_TOKEN", "value": d}]}
        for d in domains
    ]


def fetch_hubspot_new_contacts(token: str, start: str, end: str, domain_fg: list = None, exclude_offline: bool = False) -> int:
    h = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    start_ms = int(datetime.strptime(start, "%Y-%m-%d").timestamp() * 1000)
    end_ms   = int(datetime.strptime(end,   "%Y-%m-%d").timestamp() * 1000) + 86_399_999
    date_filters = [
        {"propertyName": "createdate", "operator": "GTE", "value": str(start_ms)},
        {"propertyName": "createdate", "operator": "LTE", "value": str(end_ms)},
    ]
    if exclude_offline:
        date_filters.append({"propertyName": "hs_analytics_source", "operator": "NEQ", "value": "OFFLINE_SOURCES"})
    if domain_fg:
        filter_groups = [{"filters": date_filters + fg["filters"]} for fg in domain_fg]
    else:
        filter_groups = [{"filters": date_filters}]
    r = requests.post(
        "https://api.hubapi.com/crm/v3/objects/contacts/search", headers=h,
        json={"filterGroups": filter_groups, "limit": 1},
    )
    return r.json().get("total", 0) if r.ok else 0


def aggregate_gsc(gsc_list: list) -> dict:
    """Combine GSC results from multiple sites into one."""
    total_imp    = sum(g["impressions"] for g in gsc_list)
    total_clicks = sum(g["clicks"] for g in gsc_list)
    ctr          = round(total_clicks / total_imp * 100, 2) if total_imp else 0.0
    avg_pos      = round(sum(g["avg_position"] * g["impressions"] for g in gsc_list) / total_imp, 1) if total_imp else 0.0
    daily_map: dict = {}
    for g in gsc_list:
        for row in g["daily"]:
            d = row["date"]
            if d not in daily_map:
                daily_map[d] = {"date": d, "impressions": 0, "clicks": 0}
            daily_map[d]["impressions"] += row["impressions"]
            daily_map[d]["clicks"]      += row["clicks"]
    return {
        "impressions": total_imp, "clicks": total_clicks,
        "ctr": ctr, "avg_position": avg_pos,
        "daily": sorted(daily_map.values(), key=lambda x: x["date"]),
    }


def aggregate_ga4(ga4_list: list) -> dict:
    """Combine GA4 results from multiple properties into one."""
    total_sessions = sum(g["sessions"] for g in ga4_list)
    total_engaged  = sum(g["engaged_sessions"] for g in ga4_list)
    avg_dur = round(sum(g["avg_duration_sec"] * g["sessions"] for g in ga4_list) / total_sessions) if total_sessions else 0
    daily_map: dict = {}
    for g in ga4_list:
        for row in g["daily"]:
            d = row["date"]
            if d not in daily_map:
                daily_map[d] = {"date": d, "sessions": 0, "engaged_sessions": 0}
            daily_map[d]["sessions"]         += row["sessions"]
            daily_map[d]["engaged_sessions"] += row["engaged_sessions"]
    return {
        "sessions": total_sessions, "engaged_sessions": total_engaged,
        "avg_duration_sec": avg_dur,
        "daily": sorted(daily_map.values(), key=lambda x: x["date"]),
    }


def fetch_lead_sources(token: str, start: str, end: str, domain_fg: list = None) -> list:
    """One count query per source — no record fetching, scales to any contact volume."""
    h = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    start_ms = int(datetime.strptime(start, "%Y-%m-%d").timestamp() * 1000)
    end_ms   = int(datetime.strptime(end,   "%Y-%m-%d").timestamp() * 1000) + 86_399_999
    date_filters = [
        {"propertyName": "createdate", "operator": "GTE", "value": str(start_ms)},
        {"propertyName": "createdate", "operator": "LTE", "value": str(end_ms)},
    ]
    results = []
    for source in TRACKED_SOURCES:
        src_filter = {"propertyName": "hs_analytics_source", "operator": "EQ", "value": source}
        if domain_fg:
            filter_groups = [{"filters": date_filters + fg["filters"] + [src_filter]} for fg in domain_fg]
        else:
            filter_groups = [{"filters": date_filters + [src_filter]}]
        r = requests.post(
            "https://api.hubapi.com/crm/v3/objects/contacts/search", headers=h,
            json={"filterGroups": filter_groups, "limit": 1},
        )
        count = r.json().get("total", 0) if r.ok else 0
        if count > 0:
            results.append((source, count))
    return sorted(results, key=lambda x: -x[1])


def fetch_all_form_submissions(token: str, since_ms: int) -> list[tuple[int, str]]:
    """Fetch all form submission timestamps since since_ms.
    Returns (timestamp_ms, site_key) tuples. Called once; filtered per range in memory.
    Only processes forms present in FORM_SITE_MAP.
    """
    h = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    submissions = []
    forms_resp = requests.get("https://api.hubapi.com/forms/v2/forms", headers=h)
    if not forms_resp.ok:
        return submissions
    for form in forms_resp.json():
        form_guid = form.get("guid")
        site_key  = FORM_SITE_MAP.get(form_guid)
        if not site_key:
            continue
        after = None
        while True:
            params: dict = {"limit": 50}
            if after:
                params["after"] = after
            sr = requests.get(
                f"https://api.hubapi.com/form-integrations/v1/submissions/forms/{form_guid}",
                headers=h, params=params,
            )
            if not sr.ok:
                break
            subs_data = sr.json()
            results   = subs_data.get("results", [])
            if not results:
                break
            oldest = None
            for sub in results:
                t = sub.get("submittedAt", 0)
                if t >= since_ms:
                    submissions.append((t, site_key))
                if oldest is None or t < oldest:
                    oldest = t
            if oldest and oldest < since_ms:
                break
            after = subs_data.get("paging", {}).get("next", {}).get("after")
            if not after:
                break
    return submissions


# ---------------------------------------------------------------------------
# Compile all ranges
# ---------------------------------------------------------------------------

def compile_all(custom_start: str = None, custom_end: str = None) -> dict:
    creds = google_credentials()
    token = os.environ.get("HUBSPOT_API_TOKEN", "")
    if not token:
        print("Warning: HUBSPOT_API_TOKEN not set — HubSpot data will be empty", file=sys.stderr)

    today  = date.today()
    result = {"generated": today.isoformat(), "ranges": {}}

    ranges = list(STANDARD_RANGES)
    if custom_start and custom_end:
        ranges.append(("custom", f"{custom_start} to {custom_end}", None))

    # Fetch form submissions once for the max range, filter per range in memory
    max_days    = max(d for _, _, d in STANDARD_RANGES if d)
    oldest_date = today - timedelta(days=max_days)
    oldest_ms   = int(datetime.combine(oldest_date, datetime.min.time()).timestamp() * 1000)

    print("  Fetching form submissions (once for all ranges)...", file=sys.stderr)
    try:
        all_sub_timestamps = fetch_all_form_submissions(token, oldest_ms) if token else []
    except Exception as e:
        print(f"    HubSpot forms error: {e}", file=sys.stderr)
        all_sub_timestamps = []
    print(f"    {len(all_sub_timestamps)} submissions loaded", file=sys.stderr)


    for key, label, days in ranges:
        if key == "custom":
            start, end = custom_start, custom_end
        else:
            start = (today - timedelta(days=days)).isoformat()
            end   = (today - timedelta(days=1)).isoformat()

        start_ms = int(datetime.strptime(start, "%Y-%m-%d").timestamp() * 1000)
        end_ms   = int(datetime.strptime(end,   "%Y-%m-%d").timestamp() * 1000) + 86_399_999

        print(f"  [{label}] {start} → {end}", file=sys.stderr)

        _empty_gsc = {"impressions": 0, "clicks": 0, "ctr": 0.0, "avg_position": 0.0, "daily": []}
        _empty_ga4 = {"sessions": 0, "engaged_sessions": 0, "avg_duration_sec": 0, "daily": []}

        # Bucket form submissions by site for this range
        all_site_keys = ["all"] + [c["key"] for c in SITE_CONFIGS]
        site_form_counts: dict[str, int]            = {k: 0 for k in all_site_keys}
        site_daily_forms: dict[str, dict[str, int]] = {k: {} for k in all_site_keys}
        for ts, site in all_sub_timestamps:
            if start_ms <= ts <= end_ms:
                day = datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d")
                site_form_counts[site] += 1
                site_daily_forms[site][day] = site_daily_forms[site].get(day, 0) + 1
                site_form_counts["all"] += 1
                site_daily_forms["all"][day] = site_daily_forms["all"].get(day, 0) + 1

        # Fetch GSC, GA4, contacts, sources per specific site
        sites_data = {}
        for cfg in SITE_CONFIGS:
            site_key = cfg["key"]
            dfg = build_fg(cfg["domains"])
            try:
                gsc = fetch_gsc(creds, start, end, cfg["gsc_url"])
            except Exception as e:
                print(f"    GSC {site_key} error: {e}", file=sys.stderr)
                gsc = _empty_gsc
            try:
                ga4 = fetch_ga4(creds, start, end, cfg["ga4_id"])
            except Exception as e:
                print(f"    GA4 {site_key} error: {e}", file=sys.stderr)
                ga4 = _empty_ga4
            try:
                nc = fetch_hubspot_new_contacts(token, start, end, dfg) if token else 0
                ls = fetch_lead_sources(token, start, end, dfg) if token else []
            except Exception as e:
                print(f"    HubSpot {site_key} error: {e}", file=sys.stderr)
                nc, ls = 0, []
            fs  = site_form_counts[site_key]
            fsd = [{"date": d, "form_submissions": v}
                   for d, v in sorted(site_daily_forms[site_key].items())]
            sites_data[site_key] = {
                "gsc": gsc, "ga4": ga4,
                "new_contacts": nc, "lead_sources": ls,
                "form_submissions": fs, "form_submissions_daily": fsd,
            }
            print(f"    site={site_key} contacts={nc} forms={fs}", file=sys.stderr)

        # "All Sites": aggregate GA/GSC; contacts exclude offline sources
        sites_data["all"] = {
            "gsc": aggregate_gsc([sites_data[c["key"]]["gsc"] for c in SITE_CONFIGS]),
            "ga4": aggregate_ga4([sites_data[c["key"]]["ga4"] for c in SITE_CONFIGS]),
            "new_contacts": sum(sites_data[c["key"]]["new_contacts"] for c in SITE_CONFIGS),
            "lead_sources": (fetch_lead_sources(token, start, end) if token else []),
            "form_submissions": site_form_counts["all"],
            "form_submissions_daily": [{"date": d, "form_submissions": v}
                                       for d, v in sorted(site_daily_forms["all"].items())],
        }
        print(f"    site=all contacts={sites_data['all']['new_contacts']} forms={sites_data['all']['form_submissions']}", file=sys.stderr)

        result["ranges"][key] = {
            "label": label, "start": start, "end": end,
            "sites": sites_data,
        }

    return result


# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GreatAmerica.com — Website Performance</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #f1f5f9;
      color: #1e293b;
      padding: 32px 24px;
    }
    .container { max-width: 1100px; margin: 0 auto; }
    header { margin-bottom: 24px; }
    header h1 { font-size: 22px; font-weight: 700; color: #0f172a; }
    .meta { font-size: 13px; color: #64748b; margin-top: 4px; }

    .range-selector { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 28px; }
    .range-btn {
      padding: 7px 16px; border: 1px solid #cbd5e1; border-radius: 6px;
      background: #fff; color: #475569; font-size: 13px; cursor: pointer;
      transition: all 0.15s;
    }
    .range-btn:hover  { border-color: #2563eb; color: #2563eb; }
    .range-btn.active { background: #2563eb; border-color: #2563eb; color: #fff; font-weight: 600; }

    .funnel-section {
      margin-bottom: 12px; background: #f8fafc; border-radius: 12px;
      padding: 16px 20px; border: 1px solid #e2e8f0;
    }
    .section-label {
      font-size: 11px; font-weight: 600; letter-spacing: 0.08em;
      text-transform: uppercase; color: #94a3b8; margin-bottom: 12px;
    }
    .funnel-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
    .funnel-arrow { font-size: 26px; color: #64748b; flex-shrink: 0; user-select: none; }
    .section-divider { color: #64748b; font-size: 26px; padding: 4px 0 4px 12px; user-select: none; }

    .funnel-card {
      background: #fff; border-radius: 10px; padding: 18px 20px;
      border-left: 4px solid #e2e8f0; flex: 1; min-width: 160px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .funnel-card.gsc     { border-left-color: #2563eb; }
    .funnel-card.ga4     { border-left-color: #16a34a; }
    .funnel-card.hs      { border-left-color: #ea580c; }
    .funnel-card.convert { border-left-color: #0891b2; background: #f0fdfe; }

    .card-source {
      font-size: 10px; font-weight: 700; letter-spacing: 0.06em;
      text-transform: uppercase; color: #94a3b8; margin-bottom: 4px;
    }
    .card-label { font-size: 12px; color: #64748b; margin-bottom: 6px; }
    .card-value { font-size: 28px; font-weight: 700; color: #0f172a; line-height: 1; }
    .card-sub   { font-size: 12px; color: #94a3b8; margin-top: 5px; }

    .charts-grid {
      display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 8px;
    }
    @media (max-width: 720px) { .charts-grid { grid-template-columns: 1fr; } }
    .chart-card {
      background: #fff; border-radius: 10px; padding: 20px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .chart-card h3 { font-size: 13px; font-weight: 600; color: #475569; margin-bottom: 16px; }
    footer { margin-top: 32px; font-size: 12px; color: #94a3b8; text-align: center; }
    .sources-card {
      background: #fff; border-radius: 10px; padding: 20px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.06); margin-top: 20px;
    }
    .sources-card h3 { font-size: 13px; font-weight: 600; color: #475569; margin-bottom: 4px; }
    .sources-subtitle { font-size: 12px; color: #94a3b8; margin-bottom: 16px; }

    /* View toggle */
    .view-toggle { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
    .view-label  { font-size: 13px; color: #64748b; }
    .view-btn {
      padding: 5px 16px; border: 1px solid #cbd5e1; border-radius: 6px;
      background: #fff; color: #475569; font-size: 13px; cursor: pointer; transition: all 0.15s;
    }
    .view-btn.active { background: #0f172a; border-color: #0f172a; color: #fff; font-weight: 600; }

    /* Site selector */
    .site-selector { display: flex; align-items: center; gap: 8px; margin-bottom: 24px; }
    .site-btn {
      padding: 5px 16px; border: 1px solid #cbd5e1; border-radius: 6px;
      background: #fff; color: #475569; font-size: 13px; cursor: pointer; transition: all 0.15s;
    }
    .site-btn:hover  { border-color: #0891b2; color: #0891b2; }
    .site-btn.active { background: #0891b2; border-color: #0891b2; color: #fff; font-weight: 600; }

    /* Marketing funnel */
    .mf-container { max-width: 760px; }
    .mf-zone-header {
      display: flex; align-items: center; gap: 8px;
      font-size: 11px; font-weight: 700; letter-spacing: 0.08em;
      text-transform: uppercase; padding: 20px 0 8px;
    }
    .mf-zone-tag {
      padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 800; color: #fff;
    }
    .tofu-header { color: #1d4ed8; } .tofu-header .mf-zone-tag { background: #2563eb; }
    .mofu-header { color: #0369a1; } .mofu-header .mf-zone-tag { background: #0891b2; }
    .bofu-header { color: #c2410c; } .bofu-header .mf-zone-tag { background: #ea580c; }

    .mf-row { display: flex; justify-content: flex-start; margin-bottom: 4px; }
    .mf-bar-wrap { transition: width 0.4s ease; min-width: 0; }
    .mf-bar {
      display: flex; align-items: center; justify-content: space-between;
      padding: 13px 20px; border-radius: 8px; color: #fff; min-height: 50px;
    }
    .mf-bar.tofu    { background: #2563eb; }
    .mf-bar.mofu    { background: #0891b2; }
    .mf-bar.bofu    { background: #ea580c; }
    .mf-bar.convert { background: #0369a1; }
    .mf-bar-label { font-size: 13px; font-weight: 500; white-space: nowrap; }
    .mf-src-tag   { font-size: 10px; opacity: 0.72; margin-left: 6px; }
    .mf-bar-val   { font-size: 22px; font-weight: 700; white-space: nowrap; margin-left: 20px; }
    .mf-drop-row  { padding: 5px 0 5px 16px; }
    .mf-drop-val  { font-size: 12px; color: #64748b; font-style: italic; }
  </style>
</head>
<body>
<div class="container">

  <header>
    <h1>GreatAmerica.com — Website Performance</h1>
    <p class="meta">Generated <span id="generated-date"></span> &nbsp;·&nbsp; <span id="data-range"></span></p>
  </header>

  <div class="range-selector">
    <button class="range-btn" data-range="last_7_days">Last 7 Days</button>
    <button class="range-btn" data-range="last_28_days">Last 28 Days</button>
    <button class="range-btn active" data-range="last_30_days">Last 30 Days</button>
    <button class="range-btn" data-range="last_90_days">Last 90 Days</button>
    <button class="range-btn" data-range="last_12_months">Last 12 Months</button>
    <button class="range-btn" id="custom-btn" data-range="custom" style="display:none">Custom</button>
  </div>

  <div class="view-toggle">
    <span class="view-label">View:</span>
    <button class="view-btn active" data-view="flow">Flow</button>
    <button class="view-btn" data-view="funnel">Funnel</button>
  </div>

  <div class="site-selector">
    <span class="view-label">Site:</span>
    <button class="site-btn active" data-site="all">All Sites</button>
    <button class="site-btn" data-site="greatamerica">GreatAmerica</button>
    <button class="site-btn" data-site="psg">PSG</button>
    <button class="site-btn" data-site="irhcapital">IRH Capital</button>
  </div>

  <div id="flow-view">

  <div class="funnel-section">
    <div class="section-label">Discovery — Google Search Console</div>
    <div class="funnel-row">
      <div class="funnel-card gsc">
        <div class="card-source">GSC</div>
        <div class="card-label">Impressions</div>
        <div class="card-value" id="gsc-impressions">—</div>
        <div class="card-sub">Times we appeared in search</div>
      </div>
      <div class="funnel-arrow">→</div>
      <div class="funnel-card gsc">
        <div class="card-source">GSC</div>
        <div class="card-label">Organic Clicks</div>
        <div class="card-value" id="gsc-clicks">—</div>
        <div class="card-sub">Visits from search results</div>
      </div>
      <div class="funnel-arrow">→</div>
      <div class="funnel-card gsc">
        <div class="card-source">GSC</div>
        <div class="card-label">Click-Through Rate</div>
        <div class="card-value" id="gsc-ctr">—</div>
        <div class="card-sub">Clicks ÷ Impressions</div>
      </div>
      <div class="funnel-arrow">→</div>
      <div class="funnel-card gsc">
        <div class="card-source">GSC</div>
        <div class="card-label">Avg Position</div>
        <div class="card-value" id="gsc-avg-position">—</div>
        <div class="card-sub">Ranking in search results</div>
      </div>
    </div>
  </div>

  <div class="section-divider">↓</div>

  <div class="funnel-section">
    <div class="section-label">Engagement &amp; Conversion</div>
    <div class="funnel-row">
      <div class="funnel-card ga4">
        <div class="card-source">GA4</div>
        <div class="card-label">Sessions</div>
        <div class="card-value" id="ga4-sessions">—</div>
        <div class="card-sub">All traffic sources</div>
      </div>
      <div class="funnel-arrow">→</div>
      <div class="funnel-card ga4">
        <div class="card-source">GA4</div>
        <div class="card-label">Engaged Sessions</div>
        <div class="card-value" id="ga4-engaged">—</div>
        <div class="card-sub" id="ga4-engagement-rate">—</div>
      </div>
      <div class="funnel-arrow">→</div>
      <div class="funnel-card hs">
        <div class="card-source">HubSpot</div>
        <div class="card-label">Form Submissions</div>
        <div class="card-value" id="hs-form-submissions">—</div>
        <div class="card-sub">Raised their hand</div>
      </div>
      <div class="funnel-arrow">→</div>
      <div class="funnel-card hs convert">
        <div class="card-source">HubSpot</div>
        <div class="card-label">New Contacts</div>
        <div class="card-value" id="hs-new-contacts">—</div>
        <div class="card-sub" id="hs-avg-duration">—</div>
      </div>
    </div>
  </div>

  <div class="charts-grid">
    <div class="chart-card">
      <h3>Search Visibility (GSC)</h3>
      <canvas id="gsc-chart" height="160"></canvas>
    </div>
    <div class="chart-card">
      <h3>Site Engagement (GA4)</h3>
      <canvas id="ga4-chart" height="160"></canvas>
    </div>
  </div>

  </div><!-- /flow-view -->

  <div id="funnel-view" style="display:none">
    <div class="mf-container">

      <div class="mf-zone-header tofu-header">
        <span class="mf-zone-tag">TOFU</span> Top of Funnel
      </div>
      <div class="mf-row"><div class="mf-bar-wrap" style="width:100%">
        <div class="mf-bar tofu">
          <span class="mf-bar-label">Impressions <span class="mf-src-tag">GSC</span></span>
          <span class="mf-bar-val" id="mf-impressions">—</span>
        </div>
      </div></div>
      <div class="mf-drop-row"><span class="mf-drop-val" id="mf-drop-ctr">↓ —</span></div>
      <div class="mf-row"><div class="mf-bar-wrap" style="width:88%">
        <div class="mf-bar tofu">
          <span class="mf-bar-label">Organic Clicks <span class="mf-src-tag">GSC</span></span>
          <span class="mf-bar-val" id="mf-clicks">—</span>
        </div>
      </div></div>

      <div class="mf-zone-header mofu-header">
        <span class="mf-zone-tag">MOFU</span> Middle of Funnel
      </div>
      <div class="mf-row"><div class="mf-bar-wrap" style="width:78%">
        <div class="mf-bar mofu">
          <span class="mf-bar-label">Sessions <span class="mf-src-tag">GA4</span></span>
          <span class="mf-bar-val" id="mf-sessions">—</span>
        </div>
      </div></div>
      <div class="mf-drop-row"><span class="mf-drop-val" id="mf-drop-engaged">↓ —</span></div>
      <div class="mf-row"><div class="mf-bar-wrap" style="width:65%">
        <div class="mf-bar mofu">
          <span class="mf-bar-label">Engaged Sessions <span class="mf-src-tag">GA4</span></span>
          <span class="mf-bar-val" id="mf-engaged">—</span>
        </div>
      </div></div>

      <div class="mf-zone-header bofu-header">
        <span class="mf-zone-tag">BOFU</span> Bottom of Funnel
      </div>
      <div class="mf-row"><div class="mf-bar-wrap" style="width:48%">
        <div class="mf-bar bofu">
          <span class="mf-bar-label">Form Submissions <span class="mf-src-tag">HubSpot</span></span>
          <span class="mf-bar-val" id="mf-forms">—</span>
        </div>
      </div></div>
      <div class="mf-row" style="margin-top:4px"><div class="mf-bar-wrap" style="width:35%">
        <div class="mf-bar convert">
          <span class="mf-bar-label">New Contacts <span class="mf-src-tag">HubSpot</span></span>
          <span class="mf-bar-val" id="mf-contacts">—</span>
        </div>
      </div></div>

    </div>
  </div><!-- /funnel-view -->

  <div class="sources-card" id="sources-section">
    <h3>Where Leads Came From</h3>
    <p class="sources-subtitle" id="sources-subtitle">—</p>
    <div style="position:relative; height:180px;">
      <canvas id="sources-chart"></canvas>
    </div>
  </div>

  <footer>greatamerica.com &nbsp;·&nbsp; GA4 · Google Search Console · HubSpot</footer>
</div>

<script>
  const REPORT = __REPORT_DATA__;

  const fmt = n => (n == null ? '—' : Number(n).toLocaleString());
  const pct = n => (n == null ? '—' : n.toFixed(1) + '%');
  const dur = s => { const m = Math.floor(s / 60); const sec = Math.round(s % 60); return m + ':' + String(sec).padStart(2, '0'); };

  const SOURCE_LABELS = {
    ORGANIC_SEARCH:   'Organic Search',
    DIRECT_TRAFFIC:   'Direct',
    EMAIL_MARKETING:  'Email Marketing',
    REFERRALS:        'Referrals',
    SOCIAL_MEDIA:     'Social Media',
    PAID_SEARCH:      'Paid Search',
    OTHER_CAMPAIGNS:  'Other Campaigns',
    OFFLINE:          'Offline',
    Unknown:          'Unknown',
  };
  const SOURCE_COLORS = {
    ORGANIC_SEARCH:   '#2563eb',
    DIRECT_TRAFFIC:   '#64748b',
    EMAIL_MARKETING:  '#16a34a',
    REFERRALS:        '#0891b2',
    SOCIAL_MEDIA:     '#7c3aed',
    PAID_SEARCH:      '#ea580c',
    OTHER_CAMPAIGNS:  '#d97706',
    OFFLINE:          '#94a3b8',
    Unknown:          '#cbd5e1',
  };

  let gscChart     = null;
  let ga4Chart     = null;
  let sourcesChart = null;
  let currentRange = 'last_30_days';
  let currentSite  = 'all';

  function updateReport() {
    const d = REPORT.ranges[currentRange];
    if (!d) return;
    const site = d.sites[currentSite] || {};
    const gsc  = site.gsc  || { impressions: 0, clicks: 0, ctr: 0, avg_position: 0, daily: [] };
    const ga4  = site.ga4  || { sessions: 0, engaged_sessions: 0, avg_duration_sec: 0, daily: [] };

    document.getElementById('generated-date').textContent = REPORT.generated;
    document.getElementById('data-range').textContent = d.start + ' to ' + d.end;

    document.getElementById('gsc-impressions').textContent   = fmt(gsc.impressions);
    document.getElementById('gsc-clicks').textContent        = fmt(gsc.clicks);
    document.getElementById('gsc-ctr').textContent           = pct(gsc.ctr);
    document.getElementById('gsc-avg-position').textContent  = gsc.avg_position ? gsc.avg_position.toFixed(1) : '—';

    const engRate = ga4.sessions > 0 ? (ga4.engaged_sessions / ga4.sessions * 100).toFixed(1) : 0;
    document.getElementById('ga4-sessions').textContent        = fmt(ga4.sessions);
    document.getElementById('ga4-engaged').textContent         = fmt(ga4.engaged_sessions);
    document.getElementById('ga4-engagement-rate').textContent = engRate + '% engagement rate';

    const newContacts = currentSite === 'all'
      ? ['greatamerica', 'psg', 'irhcapital'].reduce((s, k) => s + (d.sites[k]?.new_contacts || 0), 0)
      : site.new_contacts;

    document.getElementById('hs-form-submissions').textContent = fmt(site.form_submissions);
    document.getElementById('hs-new-contacts').textContent     = fmt(newContacts);
    document.getElementById('hs-avg-duration').textContent     = 'Avg session ' + dur(ga4.avg_duration_sec);

    buildGscChart(gsc.daily);
    buildGa4Chart(ga4.daily, site.form_submissions_daily || []);
    buildSourcesChart(site.lead_sources || []);
    document.getElementById('sources-subtitle').textContent =
      'New contacts by original source · ' + fmt(newContacts) + ' total';

    // Funnel view
    document.getElementById('mf-impressions').textContent  = fmt(gsc.impressions);
    document.getElementById('mf-drop-ctr').textContent     = '↓ ' + pct(gsc.ctr) + ' CTR';
    document.getElementById('mf-clicks').textContent       = fmt(gsc.clicks);
    document.getElementById('mf-sessions').textContent     = fmt(ga4.sessions);
    document.getElementById('mf-drop-engaged').textContent = '↓ ' + engRate + '% engagement rate';
    document.getElementById('mf-engaged').textContent      = fmt(ga4.engaged_sessions);
    document.getElementById('mf-forms').textContent        = fmt(site.form_submissions);
    document.getElementById('mf-contacts').textContent     = fmt(newContacts);
  }

  function toWeekly(rows) {
    const b = {};
    for (const r of rows) {
      const d = new Date(r.date + 'T00:00:00');
      const dow = d.getDay();
      d.setDate(d.getDate() - (dow === 0 ? 6 : dow - 1));
      const key = d.toISOString().slice(0, 10);
      if (!b[key]) b[key] = { date: key };
      for (const [k, v] of Object.entries(r)) {
        if (k !== 'date') b[key][k] = (b[key][k] || 0) + (v || 0);
      }
    }
    return Object.values(b).sort((a, c) => a.date < c.date ? -1 : 1);
  }

  function toMonthly(rows) {
    const b = {};
    for (const r of rows) {
      const key = r.date.slice(0, 7) + '-01';
      if (!b[key]) b[key] = { date: key };
      for (const [k, v] of Object.entries(r)) {
        if (k !== 'date') b[key][k] = (b[key][k] || 0) + (v || 0);
      }
    }
    return Object.values(b).sort((a, c) => a.date < c.date ? -1 : 1);
  }

  function buildGscChart(daily) {
    const plotData = currentRange === 'last_90_days'   ? toWeekly(daily)
                   : currentRange === 'last_12_months' ? toMonthly(daily)
                   : daily;
    if (gscChart) gscChart.destroy();
    gscChart = new Chart(document.getElementById('gsc-chart'), {
      type: 'line',
      data: {
        labels: plotData.map(r => r.date),
        datasets: [
          { label: 'Impressions', data: plotData.map(r => r.impressions), borderColor: '#2563eb', backgroundColor: 'rgba(37,99,235,0.08)', tension: 0.3, pointRadius: 0, fill: true,        yAxisID: 'y'  },
          { label: 'Clicks',      data: plotData.map(r => r.clicks),      borderColor: '#7c3aed', backgroundColor: 'transparent',          tension: 0.3, pointRadius: 0, borderWidth: 2, yAxisID: 'y2' },
        ],
      },
      options: {
        responsive: true, maintainAspectRatio: true,
        plugins: { legend: { labels: { font: { size: 11 }, boxWidth: 12 } } },
        scales: {
          x:  { ticks: { maxTicksLimit: 8, font: { size: 11 } }, grid: { display: false } },
          y:  { position: 'left',  ticks: { font: { size: 11 } }, grid: { color: '#f1f5f9' } },
          y2: { position: 'right', ticks: { font: { size: 11 }, color: '#7c3aed' }, grid: { display: false },
                title: { display: true, text: 'Clicks', font: { size: 10 }, color: '#7c3aed' } },
        },
      },
    });
  }

  function buildGa4Chart(daily, dailyForms) {
    const agg      = arr => currentRange === 'last_90_days'   ? toWeekly(arr)
                          : currentRange === 'last_12_months' ? toMonthly(arr)
                          : arr;
    const plotData = agg(daily);
    const aggForms = agg(dailyForms || []);
    const formsMap = {};
    aggForms.forEach(r => { formsMap[r.date] = r.form_submissions || 0; });
    const is12m  = currentRange === 'last_12_months';
    const dense  = daily.length > 90 && !is12m;
    if (ga4Chart) ga4Chart.destroy();
    ga4Chart = new Chart(document.getElementById('ga4-chart'), {
      type: 'line',
      data: {
        labels: plotData.map(r => r.date),
        datasets: [
          { label: 'Sessions',         data: plotData.map(r => r.sessions),            borderColor: '#16a34a', backgroundColor: dense ? 'transparent' : 'rgba(22,163,74,0.08)', tension: 0.3, pointRadius: 0, fill: !dense, borderWidth: dense ? 1 : 2, yAxisID: 'y' },
          { label: 'Engaged Sessions', data: plotData.map(r => r.engaged_sessions),    borderColor: '#0891b2', backgroundColor: 'transparent', tension: 0.3, pointRadius: 0, fill: false, borderWidth: dense ? 1 : 2, yAxisID: 'y' },
          { label: 'Form Submissions', data: plotData.map(r => formsMap[r.date] || 0), borderColor: '#ea580c', backgroundColor: 'transparent', tension: 0.3, pointRadius: 0, borderDash: [], borderWidth: 2, yAxisID: 'y2' },
        ],
      },
      options: {
        responsive: true, maintainAspectRatio: true,
        plugins: { legend: { labels: { font: { size: 11 }, boxWidth: 12 } } },
        scales: {
          x:  { ticks: { maxTicksLimit: 8, font: { size: 11 } }, grid: { display: false } },
          y:  { position: 'left',  ticks: { font: { size: 11 } }, grid: { color: '#f1f5f9' } },
          y2: { position: 'right', ticks: { font: { size: 11 }, color: '#ea580c' }, grid: { display: false },
                title: { display: true, text: 'Forms', font: { size: 10 }, color: '#ea580c' } },
        },
      },
    });
  }

  function buildSourcesChart(leadSources) {
    const labels = leadSources.map(([src]) => SOURCE_LABELS[src] || src);
    const data   = leadSources.map(([, n]) => n);
    const colors = leadSources.map(([src]) => SOURCE_COLORS[src] || '#cbd5e1');
    const height = Math.max(180, leadSources.length * 32);
    document.querySelector('#sources-section div[style]').style.height = height + 'px';
    if (sourcesChart) sourcesChart.destroy();
    sourcesChart = new Chart(document.getElementById('sources-chart'), {
      type: 'bar',
      data: { labels, datasets: [{ data, backgroundColor: colors, borderRadius: 4, borderSkipped: false }] },
      options: {
        indexAxis: 'y', responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { font: { size: 11 } }, grid: { color: '#f1f5f9' } },
          y: { ticks: { font: { size: 12 } }, grid: { display: false } },
        },
      },
    });
  }

  document.querySelectorAll('.view-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const v = btn.dataset.view;
      document.getElementById('flow-view').style.display   = v === 'flow'   ? '' : 'none';
      document.getElementById('funnel-view').style.display = v === 'funnel' ? '' : 'none';
    });
  });

  document.querySelectorAll('.range-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.range-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentRange = btn.dataset.range;
      updateReport();
    });
  });

  document.querySelectorAll('.site-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.site-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentSite = btn.dataset.site;
      updateReport();
    });
  });

  if (REPORT.ranges.custom) {
    document.getElementById('custom-btn').style.display = '';
  }

  updateReport();
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Generate + write HTML
# ---------------------------------------------------------------------------

def generate_html(data: dict) -> str:
    return HTML_TEMPLATE.replace("__REPORT_DATA__", json.dumps(data))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="docs/website-report.html")
    parser.add_argument("--start",  help="Custom range start YYYY-MM-DD")
    parser.add_argument("--end",    help="Custom range end YYYY-MM-DD")
    args = parser.parse_args()

    print("Fetching data...", file=sys.stderr)
    data = compile_all(custom_start=args.start, custom_end=args.end)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(generate_html(data), encoding="utf-8")
    print(f"Report written → {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
