#!/usr/bin/env python3
"""
Flag the two date/location artifacts that make FEC disbursement data easy to
misread. Run this BEFORE drawing any conclusion about when or where a campaign
spent money.

    python3 flag_date_artifacts.py ashley-for-iowa.csv
    python3 flag_date_artifacts.py ashley-for-iowa.csv --vendor "LIDO HOUSE"

1. STATEMENT BATCHING. A credit card payment is filed as one parent
   disbursement plus a memo sub-item per underlying charge (MEMO_CD = "X",
   BACK_REF_TRAN_ID -> parent). Every sub-item inherits the PAYMENT date, not
   the date of the charge. A single batch routinely spans months of activity
   and a dozen states, so the date on a memo row tells you when the committee
   paid its card -- nothing more.

2. VENDOR HEADQUARTERS. The CITY/STATE fields are the payee's corporate
   address, not where the money was spent. Uber and Lyft are always "San
   Francisco, CA"; American Airlines is always "Fort Worth, TX". Treating those
   as destinations will put a candidate in cities they never visited.
"""
import argparse, csv, collections

HQ_VENDORS = {
    "UBER", "LYFT", "DOORDASH", "DOOR DASH", "INSTACART", "AIRBNB", "VRBO",
    "AMAZON", "APPLE", "GOOGLE", "META", "FACEBOOK", "X CORP", "NETFLIX",
    "COSTCO", "WALMART", "TARGET", "CVS", "STARBUCKS", "CHIPOTLE",
    "AMERICAN AIRLINES", "UNITED AIRLINES", "DELTA", "SOUTHWEST AIRLINES",
    "ALASKA AIRLINES", "BUDGET RENT A CAR", "BUDGET CAR RENTAL", "AVIS",
    "ZOOM", "ADOBE", "CANVA", "GRAMMARLY", "EVENTBRITE", "PAYPAL", "STRIPE",
    "MARRIOTT INTERNATIONAL", "HILTON", "GOGO AIR",
}


def load(path):
    with open(path) as fh:
        return list(csv.DictReader(fh))


def amt(r):
    return float(r["TRANSACTION_AMT"] or 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_path")
    ap.add_argument("--vendor", help="trace one vendor's rows to their parent payments")
    ap.add_argument("--min-batch", type=int, default=5,
                    help="flag dates carrying at least this many memo sub-items")
    args = ap.parse_args()

    rows = load(args.csv_path)
    by_tran = {r["TRAN_ID"]: r for r in rows}
    memo = [r for r in rows if r["MEMO_CD"] == "X"]

    print(f"{len(rows)} rows | {len(memo)} memo sub-items "
          f"({len(memo)/max(len(rows),1):.0%} of the file)\n")

    if args.vendor:
        hits = [r for r in rows if args.vendor.upper() in r["NAME"].upper()]
        for r in sorted(hits, key=lambda x: x["DATE_ISO"]):
            kind = "MEMO SUB-ITEM" if r["MEMO_CD"] == "X" else "direct payment"
            print(f"{r['DATE_ISO']}  ${amt(r):>10,.2f}  {r['NAME']}  "
                  f"{r['CITY']}, {r['STATE']}  [{kind}]")
            parent = by_tran.get(r["BACK_REF_TRAN_ID"])
            if parent:
                print(f"    -> parent: {parent['NAME']} {parent['DATE_ISO']} "
                      f"${amt(parent):,.2f} ({parent['PURPOSE']})")
                print(f"    -> the date above is when the committee paid "
                      f"{parent['NAME']}, NOT when the charge occurred")
        return

    print("=" * 72)
    print("STATEMENT BATCHES -- dates whose entries are payment dates, not event dates")
    print("=" * 72)
    groups = collections.defaultdict(list)
    for r in memo:
        if r["BACK_REF_TRAN_ID"] in by_tran:
            groups[r["BACK_REF_TRAN_ID"]].append(r)
    flagged = {k: v for k, v in groups.items() if len(v) >= args.min_batch}
    for tran, items in sorted(flagged.items(), key=lambda kv: kv[1][0]["DATE_ISO"]):
        p = by_tran[tran]
        states = sorted({i["STATE"] for i in items if i["STATE"]})
        purposes = sorted({i["PURPOSE"] for i in items if i["PURPOSE"]})
        print(f"\n{p['DATE_ISO']}  {p['NAME']}  ${amt(p):,.2f}  ({len(items)} sub-items)")
        print(f"    spans {len(states)} states: {' '.join(states)}")
        print(f"    purposes: {', '.join(purposes[:6])}")
        for i in sorted(items, key=lambda x: -amt(x))[:4]:
            print(f"      ${amt(i):>9,.2f}  {i['NAME'][:32]:32} {i['CITY'][:16]}, {i['STATE']}")
    print(f"\n{len(flagged)} batched payments covering "
          f"{sum(len(v) for v in flagged.values())} sub-items.")
    print("Any date above is a payment date. Do not report it as a travel date.")

    print("\n" + "=" * 72)
    print("VENDOR-HQ ARTIFACTS -- CITY/STATE is the payee's address, not a destination")
    print("=" * 72)
    seen = collections.Counter()
    for r in rows:
        n = r["NAME"].upper().strip()
        if any(n == h or n.startswith(h + " ") for h in HQ_VENDORS):
            seen[(n, r["CITY"], r["STATE"])] += 1
    for (n, c, s), k in seen.most_common(15):
        print(f"  {k:>4} rows  {n[:34]:34} always filed as {c}, {s}")
    if not seen:
        print("  (none detected)")


if __name__ == "__main__":
    main()
