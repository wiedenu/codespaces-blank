# Rep. Ashley Hinson — Campaign Expenses vs. Schedule

**Research date:** August 31, 2026
**Subject article:** Troy Matthews, "Ashley Hinson Spent Hundreds of Thousands of Dollars of Campaign Funds on Luxury Trips, Fine Dining," MeidasNews, **August 17, 2026**
**Committee analyzed:** FEC ID `C00706267` — filed successively as ASHLEY HINSON FOR CONGRESS → ASHLEY FOR IOWA. This is one committee under three display names; the article's screenshot captions ("Hinson for Congress" / "Ashley for Iowa") both refer to it. It is **not** related to `C00607127` "Hinson for Congress," an unrelated Minnesota committee.

> **Revision note.** An earlier version of this report was written before I had the article text (meidasnews.com blocks automated requests) and worked from secondary summaries. Two things were wrong and are corrected here: I mis-identified the transaction set behind the "nearly $10,000" figure, and I criticized the article for including a Greenbrier charge it never mentions. Details in "Corrections" at the end.

---

## Bottom line

1. **Every checkable figure in the article is accurate.** I verified each against FEC primary-source data independently of the article. Several match to the dollar. I found no factual error in its numbers.

2. **The article is more careful with dates than it first appears.** It frames every trip at month level — "In February 2026," "In April 2022" — and never asserts a specific day. That framing is defensible.

3. **Two of its ten transactions are credit-card statement entries, where even the month is unreliable.** The Lido House and Omni Homestead charges are memo sub-items batched onto the date the campaign paid American Express. Notably, **the article's own screenshot of the Omni Homestead record shows the "Memo Item" box checked with an X** — the evidence is visible in its own exhibit.

4. **Four trips are independently corroborated as real travel** — Palm Beach (Feb 2026), Las Vegas (Aug 2024), Park City (Aug 2022), and Las Vegas (Feb 2024) — each falling in a window with no House floor votes.

5. **One is not corroborated at all.** Despite $3,384.71 in charges to The Peninsula Beverly Hills across April 2022, there is **no other California charge anywhere in that entire election cycle** between March and July 2022. And the largest of the three charges is dated a day Hinson spent voting on the House floor in Washington.

6. **Nothing here establishes impropriety, and the article does not claim illegality.** Its argument is hypocrisy — luxury spending against a "working mom" self-description — not a legal violation. That is a fair frame to argue, and the spending is real. But no trip's *purpose* is established anywhere in the piece, and purpose is the entire legal test.

---

## Method and sourcing

**Expenses.** I did not rely on the article's arithmetic. I pulled FEC bulk "operating expenditures" (Schedule B) files for the 2020, 2022, 2024, and 2026 cycles and extracted all **7,210 disbursements** by `C00706267`, de-duplicating amended filings by keeping the highest `FILE_NUM` per report/transaction. Coverage runs through the Q2 2026 report (June 30, 2026); Q3 2026 was not yet filed.

**Schedule.** No day-by-day schedule for a member of Congress exists publicly, and I made no attempt to obtain a private one. The usable proxy for verifiable physical location is the **House roll call vote record**, which timestamps each member's individual vote. I pulled every roll call for 2021, 2022, 2024, 2025, and 2026 — **2,160 votes across 473 voting days** — and checked Hinson's own vote on the relevant dates.

**Confounder checked and closed.** COVID-era proxy voting existed in the House from 2020 to January 2023, which would break the inference from "recorded vote" to "physically present." Hinson is on the record: *"I've never voted by proxy and I never will."* She campaigned publicly to abolish it. Her 2022 votes are in-person. Proxy voting had ended before the 2024 and 2026 votes cited here.

---

## The article's claims, verified

### Lodging — the "nearly $10,000" set

Ten transactions across eight properties, **totaling $9,559.20**:

| FEC date | Amount | Property | Location | Entry type |
|---|---|---|---|---|
| 2021-07-09 | $523.30 | Nemacolin Resort | Farmington, PA | direct |
| 2022-04-01 | $500.00 | The Peninsula | Beverly Hills, CA | direct |
| 2022-04-15 | $100.00 | The Peninsula | Beverly Hills, CA | direct |
| 2022-04-27 | $2,784.71 | The Peninsula | Beverly Hills, CA | direct |
| 2022-08-24 | $549.09 | Stein Eriksen Lodge | Park City, UT | direct |
| 2024-02-09 | $565.77 | Wynn Resorts | Las Vegas, NV | direct |
| 2024-08-30 | $1,520.27 | Fontainebleau | Las Vegas, NV | direct |
| 2025-08-15 | $778.97 | Omni Homestead Resort | Hot Springs, VA | **statement batch** |
| 2026-02-05 | $1,443.75 | The Breakers | Palm Beach, FL | direct |
| 2026-03-16 | $793.34 | Lido House | Newport Beach, CA | **statement batch** |

Every per-property figure the article cites is correct.

### Dining and aggregates

| Article claim | FEC actual | Status |
|---|---|---|
| "over $39,000" — Capitol Hill Club | **$39,748.14** / 72 txns | ✅ |
| "over $9,500" — Capital Grille, 2021–2026 | **$9,516.14** / 18 txns | ✅ |
| "over $4,300 on 34 separate occasions" — Bullfeathers | **$4,305.42 / exactly 34 txns** | ✅ |
| "over $700" — Old Ebbitt Grill | **$726.75** | ✅ |
| "over $400" — Charlie Palmers | **$402.04** food/beverage (4 txns) | ✅ — conservative; a 5th $450 facility-rental charge would make it $852.04 |
| "over $80,000" — DC meals | **$88,023.74** (DC food/beverage less $67,575 to Socko Strategies, a consulting vendor) | ✅ |
| "nearly $110,000" combined | consistent | ✅ |

---

## Finding 1 — two entries are statement dates, not stay dates

The Lido House charge is not a payment to a hotel. It is a **memo sub-item** (`MEMO_CD = X`) under parent transaction `SB17.10179` — a single **$5,568.24 payment to American Express dated March 16, 2026**. All 24 sub-items in that batch carry that identical date:

```
2026-03-16  $793.34  LIDO HOUSE            Newport Beach, CA
2026-03-16  $620.34  FAIRFIELD INN         Waterloo, IA
2026-03-16  $486.44  THE WARRIOR HOTEL     St. Louis, MO
2026-03-16  $325.77  SEAFOOD BAR           Palm Beach, FL
2026-03-16  $201.25  STORAGE DEPOT         Hiawatha, IA      <- storage unit rent
2026-03-16  $130.12  ALLIANT ENERGY        Cedar Rapids, IA  <- monthly utility bill
2026-03-16  $ 42.30  KWIK STAR             Webster City, IA  <- gas station
2026-03-16  $  9.49  THE COFFEE SHOP       Milford, IA
   ... 16 more
```

Nobody paid a storage-unit bill, an electric bill, and bought gas in Webster City while checking into a Newport Beach hotel and eating in Palm Beach the same afternoon. This is one credit card statement itemized on the day it was paid. "March 2026" is when the campaign paid Amex.

The pattern repeats across 39 distinct card-payment parents and 306 memo items in the 2026 cycle alone — and in other batches: **2025-03-21** (five restaurants across Santa Monica, Malibu, and Irvine, one date); **2025-04-07** (two hotels, a car rental, and two restaurants across five SoCal cities, one date); **2026-04-14** (five hotels in four states, one date).

**A control case that confirms the lag.** The Greenbrier — a property the article does *not* cite — shows the same effect with a known ground truth. The committee's $72.60 Greenbrier charge is dated **March 22, 2024**. The official **House Republican Members Retreat was held at The Greenbrier on March 13–14, 2024**. Hinson voted in DC the morning of the 13th, and there were no votes on the 14th — the standard pattern for members traveling to the retreat after morning votes. The FEC date lags the actual event by eight days.

**A related trap in the same data:** FEC city/state fields record the **vendor's corporate address**, not where money was spent. These filings are full of "LYFT — San Francisco, CA," "UBER — San Francisco, CA," "AMERICAN AIRLINES — Fort Worth, TX," "DOORDASH — San Francisco, CA." Read naively the file would suggest Hinson lives in San Francisco. Any location analysis treating those as destinations is broken. To the article's credit, it does not make this mistake.

---

## Finding 2 — date-by-date cross-reference against the vote record

| Trip | House in session? | Verified location | Assessment |
|---|---|---|---|
| **The Breakers** — Palm Beach, $1,443.75, 2/5/2026 | No votes 2/5–2/8 | Voted DC 2/4 4:13 PM; next voted DC 2/9 6:59 PM | ✅ **Real trip, article correct.** Airline charges 2/2 ($252) and 2/4 (Southwest, $225) bracket it; a $325.77 charge at the Seafood Bar — a restaurant *inside* The Breakers — appears in a later statement batch. Clean four-day non-voting window. |
| **Fontainebleau** — Las Vegas, $1,520.27, 8/30/2024 | **August recess — no votes at all** | — | ✅ **Real trip, article correct.** American Airlines 8/28 ($310.98) and Uber 8/29 precede it. House returned 9/9. |
| **Stein Eriksen Lodge** — Park City, $549.09, 8/24/2022 | Recess (only 8/12 had votes) | — | ✅ **Real trip, article correct on timing.** Corroborated by California Pizza Kitchen and Squatters Pub Brewery in **Salt Lake City on 8/23**, United Airlines $746.52 on 8/23, and GoGo in-flight wifi on 8/24. SLC is the airport for Park City. ⚠️ But this was **late August**. The lodge operates as a summer conference venue then. Calling it "one of the best ski hotels in the US and the world" is true of the property and misleading about the trip. |
| **Wynn** — Las Vegas, $565.77, 2/9/2024 | No votes 2/8–2/12 | Voted DC 2/7; next voted DC 2/13 | ✅ Consistent with a real trip in a scheduled non-voting window. |
| **Nemacolin** — Farmington PA, $523.30, 7/9/2021 | No votes 7/2–7/18 | — | Recess window. No corroborating charges either way. |
| **Omni Homestead** — Hot Springs VA, $778.97, 8/15/2025 | House out all August | — | ⚠️ **Statement-batch entry** — the article's own screenshot shows the Memo Item box checked. Actual date unknown. |
| **Lido House** — Newport Beach, $793.34, 3/16/2026 | No votes 3/16 | — | ⚠️ **Statement-batch entry.** An In-N-Out charge in Los Angeles appears in the 2/20/2026 batch, so a SoCal trip more likely occurred in **February**, not March. |
| **The Peninsula** — Beverly Hills, $3,384.71 across 4/1, 4/15, 4/27/2022 | 4/27: **yes, 12 roll calls** | **Voted DC 4:22 / 5:08 / 6:00 PM on 4/27; also voted DC 4/26 and 4/28** | ⚠️ **Weakest link in the set.** The $2,784.71 charge date cannot be a stay date. The 4/14–4/15 charges coincide with DC restaurant charges (Charlie Palmers, Circa, Capitol Hill Club). The only open window is the **April 8–25 recess** — and there is **no other California charge in the entire cycle** between March and July 2022 to corroborate a trip. The split ($500 / $100 / $2,784.71) looks like a booking deposit and later settlement, which may not correspond to April travel at all. |

---

## What cannot be determined

- **The purpose of any of these trips.** This is the central gap, and it is the gap that matters legally. Federal law permits campaign funds for bona fide campaign and fundraising travel; the FEC's prohibition is on *personal use*, which turns on purpose, not on the price of the hotel. Hinson is a Senate candidate who raised roughly $1.7M in Q4 2025 alone; donor travel to Palm Beach, Newport Beach, and Las Vegas is ordinary at that level. Showing wrongdoing would require showing a trip had no campaign purpose. Neither the article nor this analysis does that, and the article does not allege it.
- **A specific event behind any trip.** The Club for Growth holds its annual donor retreat at The Breakers, which is the obvious candidate for February 2026, but I could not confirm 2026 dates (clubforgrowth.org is bot-protected). **Hypothesis, not finding.**
- **True dates for the Newport Beach, Omni Homestead, and Beverly Hills stays.** Not recoverable from FEC data; would require the underlying card statements.
- **The article's non-expense claims.** I did not verify the "$7 million net worth increase," the reporting on her husband Matthew Arenholz's stock in High Street Insurance Partners, or the sourcing/context of the quoted "working mom" remarks. Those come from financial disclosures and video, outside what I examined.

---

## Assessment

The reporting is **accurate and, on the numbers, careful**. It pulled real transactions from real filings, added them correctly, and framed dates at month level rather than overclaiming a specific day. I tried to break its figures against primary source data and could not.

Its real weaknesses are narrower than the numbers:

- **Two of ten entries are statement-batched**, so even the month is unreliable — and for Omni Homestead the memo flag is visible in the article's own exhibit.
- **The Beverly Hills trip, the second-largest item in the set, is uncorroborated**, and its largest charge is dated a day she spent on the House floor.
- **An August stay is characterized by the property's ski ranking**, which does rhetorical work the facts don't support.
- **No purpose is established for any trip**, which leaves the hypocrisy argument resting entirely on venue prestige.

The strongest version of the story needs none of the trips: **$39,748 at a single private Republican club and $88,024 on Washington restaurant meals**, both solidly documented, both indisputably dated, and neither dependent on any inference about travel.

---

## Corrections to the first version of this report

| Claim | Correction |
|---|---|
| "I reverse-engineered the exact 12 transactions behind the $10,000 figure — $9,294.24" | **Wrong set.** The actual set is 10 transactions totaling **$9,559.20**. I missed the Fontainebleau charge ($1,520.27) because the filing misspells it "FONTAINBLEAU," and I wrongly included The Greenbrier, Four Seasons NY, and St. Regis DC, none of which the article cites. The totals were coincidentally similar. |
| "A $72.60 incidental at The Greenbrier is folded into a list of luxury resort stays" | **Withdrawn.** The article never mentions The Greenbrier. The Greenbrier data is still useful, but as an independent control case for date lag — not as a criticism. |
| "At least one luxury trip date is provably impossible" | **Overstated.** The article says "In April 2022," not April 27. The vote-record finding stands on the *charge date*, but it does not contradict the article's claim. |
| "The article lets venue prestige carry the argument" (three distortions listed) | Reduced to one that survives: the August ski-lodge framing. |

---

## Files

| Path | What it is |
|---|---|
| [`hinson-fec-2026/`](hinson-fec-2026/) | Case data — full 7,210-row disbursement extract, the 10-transaction lodging set, the Amex batch, dining aggregates, vote cross-check, and the article transcription |
| [`../../tools/fec-committee-analysis/`](../../tools/fec-committee-analysis/) | Reusable pipeline (stdlib only, no API key). Its README documents the FEC date/location traps in general form |

Reproduce the core findings:

```bash
cd tools/fec-committee-analysis
python3 fec_extract.py --committee C00706267 --cycles 2020 2022 2024 2026 --out out.csv
python3 flag_date_artifacts.py out.csv --vendor "LIDO HOUSE"
python3 house_votes.py --years 2022 2024 2026 --member Hinson --dates 2022-04-27 2024-03-22
```

---

## Sources

- FEC bulk operating expenditure files, cycles 2020/2022/2024/2026 — `fec.gov/files/bulk-downloads/`
- FEC committee record, [C00706267](https://www.fec.gov/data/committee/C00706267/?cycle=2026)
- U.S. House Clerk roll call votes — `clerk.house.gov/evs/{year}/`
- [CNN — House GOP retreat at The Greenbrier, March 2024](https://www.cnn.com/2024/03/12/politics/house-gop-retreat/index.html)
- [Roll Call — House GOP retreat, March 13, 2024](https://rollcall.com/2024/03/13/house-gop-members-well-some-of-them-head-for-the-hills/)
- [Telegraph Herald — Hinson on proxy voting](https://www.telegraphherald.com/news/politics/article_11fbe2a6-a8fd-5523-befa-1d74be0edc95.html)
- [Iowa Democratic Party release, Aug 24, 2026](https://iowademocrats.org/2026/08/24/ashley-hinson-lives-lavishly-using-campaign-funds-while-the-hinson-backed-iran-war-squeezes-iowans-at-the-gas-pump/)
