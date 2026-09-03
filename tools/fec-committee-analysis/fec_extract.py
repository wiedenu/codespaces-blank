#!/usr/bin/env python3
"""
Extract one committee's itemized disbursements (FEC Schedule B / "operating
expenditures") from FEC bulk downloads, de-duplicated for amended filings.

No API key required. The bulk files are large (40-70MB compressed, ~300MB raw
per cycle), so downloads are cached under --cache.

    python3 fec_extract.py --committee C00706267 \
        --cycles 2020 2022 2024 2026 --out ashley-for-iowa.csv

Why not the OpenFEC API: the DEMO_KEY is capped at 40 calls/hour, which is not
enough to page a mid-size committee (1,700+ records at 100/page). Bulk is
complete, unpaginated, and needs no key.
"""
import argparse, csv, io, os, sys, urllib.request, zipfile

FIELDS = ("CMTE_ID AMNDT_IND RPT_YR RPT_TP IMAGE_NUM LINE_NUM FORM_TP_CD SCHED_TP_CD "
          "NAME CITY STATE ZIP TRANSACTION_DT TRANSACTION_AMT TRANSACTION_PGI PURPOSE "
          "CATEGORY CATEGORY_DESC MEMO_CD MEMO_TEXT ENTITY_TP SUB_ID FILE_NUM TRAN_ID "
          "BACK_REF_TRAN_ID").split()

URL = "https://www.fec.gov/files/bulk-downloads/{cycle}/oppexp{yy}.zip"


def cycle_rows(cycle, committee, cache):
    """Yield raw pipe-delimited lines for `committee` in one two-year cycle."""
    os.makedirs(cache, exist_ok=True)
    cached = os.path.join(cache, f"{committee}_{cycle}.psv")
    if os.path.exists(cached):
        with open(cached) as fh:
            yield from fh
        return

    url = URL.format(cycle=cycle, yy=str(cycle)[2:])
    zpath = os.path.join(cache, f"oppexp{str(cycle)[2:]}.zip")
    if not os.path.exists(zpath):
        print(f"  downloading {url}", file=sys.stderr)
        urllib.request.urlretrieve(url, zpath)

    prefix = committee.encode() + b"|"
    kept = []
    with zipfile.ZipFile(zpath) as z:
        name = next(n for n in z.namelist() if n.endswith(".txt"))
        with z.open(name) as fh:
            for line in io.TextIOWrapper(fh, encoding="utf-8", errors="replace"):
                if line.startswith(committee + "|"):
                    kept.append(line)
    with open(cached, "w") as fh:
        fh.writelines(kept)
    yield from kept


def parse(line):
    parts = line.rstrip("\n").split("|")
    parts += [""] * (len(FIELDS) - len(parts))
    return dict(zip(FIELDS, parts[:len(FIELDS)]))


def iso(row):
    p = row["TRANSACTION_DT"].split("/")
    return f"{p[2]}-{p[0]}-{p[1]}" if len(p) == 3 else ""


def dedupe(rows):
    """FEC bulk files contain BOTH the original and every amended report.

    Keep the highest FILE_NUM for each (report year, report type, transaction
    id) -- that is the most recent version of that transaction. Without this
    step, amended committees are double- and triple-counted.
    """
    best = {}
    for r in rows:
        key = (r["RPT_YR"], r["RPT_TP"], r["TRAN_ID"])
        prior = best.get(key)
        if prior is None or int(r["FILE_NUM"] or 0) > int(prior["FILE_NUM"] or 0):
            best[key] = r
    return list(best.values())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--committee", required=True, help="FEC committee id, e.g. C00706267")
    ap.add_argument("--cycles", nargs="+", type=int, required=True,
                    help="even-numbered cycle years, e.g. 2022 2024 2026")
    ap.add_argument("--out", required=True)
    ap.add_argument("--cache", default=".fec-cache")
    args = ap.parse_args()

    rows = []
    for cycle in args.cycles:
        got = [parse(l) for l in cycle_rows(cycle, args.committee, args.cache)]
        for r in got:
            r["CYCLE"] = str(cycle)
        print(f"  {cycle}: {len(got)} raw rows", file=sys.stderr)
        rows += got

    rows = dedupe(rows)
    rows.sort(key=iso)
    for r in rows:
        r["DATE_ISO"] = iso(r)

    cols = ["DATE_ISO", "CYCLE"] + FIELDS
    with open(args.out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    memo = sum(1 for r in rows if r["MEMO_CD"] == "X")
    total = sum(float(r["TRANSACTION_AMT"] or 0) for r in rows if r["MEMO_CD"] != "X")
    print(f"\n{len(rows)} de-duplicated rows -> {args.out}", file=sys.stderr)
    print(f"  {memo} memo sub-items (excluded from the total below)", file=sys.stderr)
    print(f"  non-memo disbursements: ${total:,.2f}", file=sys.stderr)


if __name__ == "__main__":
    main()
