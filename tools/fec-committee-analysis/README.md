# FEC committee analysis

Pull any federal committee's itemized spending from FEC bulk data, then test
claims about **when** and **where** that money was spent against the House roll
call record.

Built August 2026 while fact-checking a story about Rep. Ashley Hinson's
campaign spending. Case write-up:
[`docs/one-offs/hinson-campaign-expense-schedule-analysis-2026-08-31.md`](../../docs/one-offs/hinson-campaign-expense-schedule-analysis-2026-08-31.md).

Python 3 standard library only. No API key. No dependencies.

---

## Read this before you conclude anything

Two properties of FEC disbursement data make it easy to get a story wrong.
Both bit me on the first pass.

### 1. The transaction date is often a payment date, not an event date

When a committee pays a credit card, the filing is **one parent disbursement
plus one memo sub-item per underlying charge** (`MEMO_CD = "X"`, with
`BACK_REF_TRAN_ID` pointing at the parent). **Every sub-item inherits the date
the card was paid.** A single batch routinely spans months of real-world
activity and a dozen states.

Real example from this committee — 24 sub-items, all stamped `2026-03-16`,
under one $5,568.24 American Express payment:

```
2026-03-16  $793.34  LIDO HOUSE        Newport Beach, CA
2026-03-16  $325.77  SEAFOOD BAR       Palm Beach, FL
2026-03-16  $201.25  STORAGE DEPOT     Hiawatha, IA      <- storage unit rent
2026-03-16  $130.12  ALLIANT ENERGY    Cedar Rapids, IA  <- monthly utility bill
2026-03-16  $ 42.30  KWIK STAR         Webster City, IA  <- gas station
```

Nobody paid an electric bill and bought gas in Webster City while checking into
a Newport Beach hotel and eating in Palm Beach that afternoon. That date says
when the committee paid Amex. Nothing else.

**Direct (non-memo) payments are better but still not event dates** — a hotel
folio can settle days or weeks after checkout. A known-ground-truth example
from this data: the House Republican retreat at The Greenbrier ran March 13-14,
2024; the committee's Greenbrier charge is dated **March 22, 2024**. An
eight-day lag on an event whose date is a matter of public record.

### 2. CITY / STATE is the payee's headquarters, not a destination

Uber and Lyft are always "San Francisco, CA." American Airlines is always "Fort
Worth, TX." Marriott International is always "Bethesda, MD." Read naively,
this committee's file would put the candidate in the Bay Area several hundred
times.

`flag_date_artifacts.py` detects both.

### 3. De-duplicate amendments or you will double-count

Bulk files contain the original **and** every amended report. Keep the highest
`FILE_NUM` per `(RPT_YR, RPT_TP, TRAN_ID)`. `fec_extract.py` does this; the raw
files for this committee held 7,210 rows across four cycles after dedupe, from
a larger raw count.

### 4. Proxy voting breaks the location inference (May 2020 - Jan 2023)

A recorded House vote is good evidence a member was physically in the chamber
— **except** during COVID-era proxy voting, and the Clerk's XML does not mark
proxy votes. For any date in that window, establish independently that the
member did not vote by proxy. (In the Hinson case she was on record refusing to
ever use it, which is what made the April 2022 finding usable.)

---

## Usage

```bash
# 1. pull a committee's disbursements, de-duplicated, as CSV
python3 fec_extract.py --committee C00706267 \
    --cycles 2020 2022 2024 2026 --out ashley-for-iowa.csv

# 2. find the dates you cannot trust
python3 flag_date_artifacts.py ashley-for-iowa.csv

# 3. trace one vendor to its parent payment
python3 flag_date_artifacts.py ashley-for-iowa.csv --vendor "LIDO HOUSE"

# 4. test specific dates against the House floor record
python3 house_votes.py --years 2022 2024 2026 --member Hinson \
    --dates 2022-04-27 2024-03-22 2026-02-05

# 5. just the session calendar
python3 house_votes.py --years 2026 --calendar
```

Bulk downloads are 40-70MB per cycle and are cached in `.fec-cache/`
(gitignored). First run is slow; later runs are instant.

`--member` takes the Clerk's `sort-field` surname, usually just the last name.

## Finding a committee id

<https://www.fec.gov/data/committees/> — search the candidate. Watch for
committees that were **renamed**: `C00706267` files as "Ashley Hinson for
Congress" in older reports and "Ashley for Iowa" in newer ones. Same committee.
Conversely, a similar name can be a different person entirely — `C00607127`
"Hinson for Congress" is an unrelated Minnesota committee.

## What this does not tell you

Whether spending was proper. Campaign funds may lawfully cover campaign and
fundraising travel; the FEC's prohibition is on **personal use**, which turns on
the purpose of each trip. Purpose is not in this data. A large number next to a
famous hotel is not evidence of a violation.

## Data sources

- Disbursements: <https://www.fec.gov/files/bulk-downloads/> (`oppexpNN.zip`)
- Roll call votes: `https://clerk.house.gov/evs/{year}/`
- Bulk file column definitions: <https://www.fec.gov/campaign-finance-data/operating-expenditures-file-description/>
