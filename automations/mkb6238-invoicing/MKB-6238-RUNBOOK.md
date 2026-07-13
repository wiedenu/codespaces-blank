# MKB-6238 — Henry Schein $0 Invoice Send (Runbook)

Quarterly process. Sends a "$0 invoice / rebate applied" email to Henry Schein Flex
customers whose dental-supply rebates covered their GreatAmerica finance payment.

- **Script:** `mkb6238-rebate-sender.py` (same folder as this file)
- **Cadence:** Quarterly (April, July, Oct, Jan — driven by the rebate cycle)
- **Jira:** MKB-6238
- **Owner:** John Wiedenheft (Marketing Ops)

---

## How the email is sent

It does **not** use SMTP. It uses HubSpot's **Single-Send Transactional Email API**:

- Endpoint: `POST https://api.hubapi.com/marketing/v3/transactional/single-email/send`
- **HubSpot email ID: `216664065950`** (the saved email the API sends)
- Auth: a HubSpot **private-app token** with the `transactional-email` scope
- One API call per recipient (`message.to`), with personalization passed as `contactProperties`

The email's visible "From" (`Account Servicing <customersupport-11@accountservicing.com>`)
and BCC (`jwiedenheft@greatamerica.com`) are configured **inside** the HubSpot email, not
in the script.

---

## Prerequisites (each quarter)

1. **The recipient export** — an `.xlsx` from the rebate process (see format below).
2. **The HubSpot token** in your terminal environment:
   ```bash
   export HUBSPOT_PRIVATE_APP_TOKEN="pat-na1-..."
   ```
   (`HUBSPOT_ACCESS_TOKEN` / `HUBSPOT_TOKEN` also accepted.) Keep it out of the repo and
   out of any chat transcript.
3. **Python deps:** `requests` and `openpyxl` (already present in the Codespace).

---

## Input file format

The export has **preamble rows** above the real headers (an "Average Savings for the
Quarter" title). The script auto-detects the header row (the first row containing a cell
exactly equal to `Email`) and ignores trailing all-blank rows, so you don't need to clean
the file first.

Expected columns (only three feed the email; the rest are source data):

| Export column   | Feeds HubSpot property            | Notes |
|-----------------|-----------------------------------|-------|
| `Email`         | recipient (`message.to`)          | may hold 2 addresses (see below) |
| `Description`   | `smg_henry_schein_description`     | the pre-built "You saved 41%..." line |
| `ApplicationID` | `pm_contract_id`                  | use this, NOT `Application Clean` |
| `Billing Name`  | `pm_lessee_name`                  | the lessee/customer name |

> These are `contact.` tokens in the HubSpot email, so the script sends them as
> `contactProperties` — which **also writes the values onto the contact record** in
> HubSpot. That is expected for these purpose-built fields.

If a future export renames these columns, update `CONTACT_PROPERTY_MAP` at the top of
the script.

---

## Pre-flight check (do this every quarter — it has bitten us)

**The payment due date is HARDCODED static text inside HubSpot email `216664065950`.**
It does not come from the file and does not auto-update. In the July '26 run it still
said "April 30, 2026" from the prior quarter.

Before any live send:
1. Open email `216664065950` in HubSpot.
2. Update the "...due on <Month DD, YYYY>" text to this quarter's correct due date.
3. Send yourself a **live test** (a 2-row file to your own addresses) and **open the
   email** — confirm the date AND that the three tokens render. Do not trust the API
   `200`s alone; they only mean HubSpot accepted the request, not that the content is right.

---

## How the script handles messy data

- **Trailing/leading `;` or `,`** — stripped, then validated.
- **Two addresses in one cell** (`AP@x.com; bcruse@x.com`) — **split and sent to BOTH**
  (John's decision, 7/7/26). Every split piece must be a valid address.
- **Any invalid piece** (e.g. `drgme45@msn,.com`, missing `@`, missing TLD, internal
  space, `@@`) — the whole row is flagged `malformed` and **not** sent. It goes to the
  resend workbook for human correction. This is the guardrail; do not bypass it.
- **Blank personalization value** — the row still sends, but the script WARNS (that
  token renders empty for that recipient).
- **Duplicates** — same email + same agreement = flagged as an exact duplicate (would
  double-invoice). Same email across *different* agreements = reported as INFO only and
  still sent (a customer with multiple contracts legitimately gets one email per contract).

---

## Run procedure

### 1. Dry-run (sends nothing — always do this first)
```bash
python3 mkb6238-rebate-sender.py "<export file>.xlsx" --dry-run
```
Review the output:
- `clean sends` / `flagged rows` counts
- how many rows split into multiple addresses
- the duplicate INFO/WARNING lines
- the blank-token warning, if any

The dry-run writes any flagged rows to **`OPS - Henry Schein Resend - MMDDYY.xlsx`**.

### 2. Fix the flagged rows
Send the flagged addresses back to the requester / Account Servicing for correct
addresses (they have them on file). Put the corrected rows into a resend workbook.

### 3. Live send — main file
```bash
python3 mkb6238-rebate-sender.py "<export file>.xlsx" --send
```
Writes a log: **`mkb6238-send-YYYYMMDD-HHMMSS.log`** — one line per recipient
(`OK 200 <addr>` / `ERR <code> <addr>` with the error body), plus a `SUMMARY:` footer
with ok/err/flagged totals. Review it (or have Claude review it).

### 4. Live send — resend pass
Once corrected addresses are back:
```bash
python3 mkb6238-rebate-sender.py "OPS - Henry Schein Resend - MMDDYY.xlsx" --send
```

Sending behavior: one send at a time, ~0.2s apart, with automatic retry/backoff on
`429` and `5xx`. Safe to re-run a resend file; it only sends the rows in that file.

---

## Reference numbers

- **April '26:** 1,304 contacts, 22 flagged (corrected + resent). *(Live send.)*
- **July '26 — DRY-RUN / EMAIL TEST ONLY, LIVE SEND NOT YET RUN as of 2026-07-13.**
  Dry-run showed 1,440 records → **1,448 would-be sends** after splitting 14 two-address
  cells; 6 flagged malformed (5 typos + 1 with no usable address) to correct. The live
  send is tracked under **MKB-7737, scheduled 2026-07-15**. Do NOT read these numbers as a
  completed send when checking for double-sends.

---

## History / why this runbook exists

The original script was lost in the May 20, 2026 claude-brain public-exposure mass-delete
(it lived in the Codespace workspace, not the claude-brain repo, so the June 29 restore
missed it). Rebuilt from the April run notes on July 7, 2026, at which point the SMTP
assumption was corrected to the HubSpot Transactional API, the token mapping was confirmed
against live test emails, and the multi-address split + duplicate checks were added.
This runbook exists so it never has to be reverse-engineered again.
