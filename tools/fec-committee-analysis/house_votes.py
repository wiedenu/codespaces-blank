#!/usr/bin/env python3
"""
Build an index of U.S. House roll call votes from the Clerk's site, and look up
how a named member voted on a given date.

This is the only public, verifiable record of where a House member physically
was on a given day. Use it to test whether a campaign-finance "travel" date
could possibly be a travel date.

    # which days did the House vote, and how did Hinson vote on these dates?
    python3 house_votes.py --years 2022 2024 2026 \
        --member Hinson --dates 2022-04-27 2024-03-22 2026-02-05

    # just the session calendar
    python3 house_votes.py --years 2026 --calendar

CAVEAT -- proxy voting: from May 2020 to January 2023 the House allowed voting
by proxy, and the Clerk's XML does NOT distinguish a proxy vote from an
in-person one. For any date in that window you must independently establish
that the member did not vote by proxy before treating a recorded vote as proof
of physical presence.
"""
import argparse, re, sys, urllib.request, collections

UA = {"User-Agent": "Mozilla/5.0 (research script)"}
MONTHS = dict(zip("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(), range(1, 13)))
ROW = re.compile(r'rollnumber=(\d+)">\d+</A></TD>\s*<TD><FONT[^>]*>(\d{1,2}-[A-Za-z]{3})</FONT>', re.S)


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA)).read().decode("utf-8", "replace")


def year_index(year):
    """Return {iso_date: [roll numbers]} for one calendar year."""
    idx = get(f"https://clerk.house.gov/evs/{year}/index.asp")
    pages = sorted(set(re.findall(r"ROLL_\d+\.asp", idx)))
    days = collections.defaultdict(list)
    for page in pages:
        for roll, dt in ROW.findall(get(f"https://clerk.house.gov/evs/{year}/{page}")):
            d, mon = dt.split("-")
            days[f"{year}-{MONTHS[mon]:02d}-{int(d):02d}"].append(int(roll))
    return dict(days)


def member_vote(year, roll, member):
    """Return (iso_date, time, vote, description) for one member on one roll call."""
    xml = get(f"https://clerk.house.gov/evs/{year}/roll{roll:03d}.xml")
    m = re.search(r'sort-field="%s"[^>]*>.*?</legislator><vote>([^<]*)</vote>' % re.escape(member), xml, re.S)
    date = re.search(r"<action-date>([^<]*)</action-date>", xml)
    time = re.search(r"<action-time[^>]*>([^<]*)</action-time>", xml)
    desc = re.search(r"<vote-desc>([^<]*)</vote-desc>", xml)
    return (date.group(1) if date else "?",
            time.group(1) if time else "?",
            m.group(1) if m else "NOT RECORDED",
            desc.group(1) if desc else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", nargs="+", type=int, required=True)
    ap.add_argument("--member", help="Clerk sort-field surname, e.g. Hinson")
    ap.add_argument("--dates", nargs="*", default=[], help="ISO dates to test")
    ap.add_argument("--calendar", action="store_true", help="print voting days and exit")
    ap.add_argument("--max-rolls", type=int, default=3, help="roll calls to sample per date")
    args = ap.parse_args()

    index = {}
    for y in args.years:
        print(f"indexing {y} ...", file=sys.stderr)
        index.update(year_index(y))
    print(f"{sum(len(v) for v in index.values())} roll calls across "
          f"{len(index)} voting days\n", file=sys.stderr)

    if args.calendar:
        for d in sorted(index):
            print(f"{d}  {len(index[d]):>2} roll calls")
        return

    for date in args.dates:
        rolls = index.get(date)
        year = int(date[:4])
        print(f"\n{date}")
        if not rolls:
            nearby = sorted(d for d in index if d[:7] == date[:7])
            print("  NO ROLL CALL VOTES this day")
            print(f"  voting days that month: {', '.join(nearby) if nearby else '(none)'}")
            continue
        print(f"  {len(rolls)} roll calls")
        if args.member:
            for roll in sorted(rolls)[:args.max_rolls]:
                d, t, v, desc = member_vote(year, roll, args.member)
                print(f"    roll {roll}: {d} {t} -> {args.member}: {v}   {desc[:50]}")


if __name__ == "__main__":
    main()
