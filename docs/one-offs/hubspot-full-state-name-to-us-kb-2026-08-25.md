# HubSpot - Full State Name to United States - KB - 2026-08-25

> SharePoint name when this lands in the KB library:
> `HubSpot - Full State Name to United States - KB - 2026-08-25`
> Index row still needed in `_MOps KB Index.xlsx`.

| | |
|---|---|
| **Workflow name** | SYS - Full State Name to United States |
| **Status** | Active |
| **Object** | Contacts |
| **Owner** | John Wiedenheft |
| **Created** | 2026-08-25 |
| **Last reviewed** | 2026-08-25 |
| **Type** | Reference (12-month review) |
| **Ticket** | _not recorded — add_ |

## Purpose

Sets **Country/Region** to **United States** when a contact's **State/Region** holds a full U.S.
state name or **District of Columbia**. Keeps geography consistent so downstream segmentation and
the Salesforce sync see a country value.

## Enrollment

Both conditions must be true:

1. **State/Region** is any of the 50 state names plus District of Columbia (full names, not
   abbreviations).
2. **Country/Region** is **not** equal to **United States**.

Condition 2 exists so contacts already carrying the correct country are not re-written.

## Re-enrollment

**Enabled.** A contact can enroll again if it meets the criteria after a previous pass.

Self-limiting in normal operation: the action makes condition 2 false, so the workflow cannot
re-trigger itself. It *will* re-fire if Country/Region is later changed away from United States
while State/Region still holds a U.S. state name — including when a person changes it deliberately.
See the Georgia gotcha below.

## Action

Single step — **Edit record**: set **Country/Region** to **United States**.

Simplified from an earlier branch-based design. Correct call: the enrollment trigger already
constrains the set, so branching re-tested a condition that was true by construction.

## Gotchas

### 1. Georgia the country gets relabeled as the United States

A contact in Tbilisi with `Country/Region = Georgia` and `State/Region = Georgia` satisfies both
enrollment conditions, and the workflow overwrites their country to United States. Silent, and with
re-enrollment on it will undo a manual correction.

Georgia is the only full state name that collides with a country name, so the fix is narrow: add a
third enrollment condition excluding contacts whose `Country/Region` is already a recognized
non-U.S. country, or exclude the single case `State/Region = Georgia AND Country/Region = Georgia`.

### 2. An abbreviation-keyed sibling workflow would be far more dangerous

This version is explicitly scoped to full names. If a companion workflow keys on two-letter state
codes, it collides with ISO country codes across a wide surface:

`DE` Delaware / Germany · `IN` Indiana / India · `PA` Pennsylvania / Panama · `VA` Virginia /
Vatican · `MD` Maryland / Moldova · `NE` Nebraska / Niger · `SC` South Carolina / Seychelles ·
`SD` South Dakota / Sudan · `TN` Tennessee / Tunisia · `MT` Montana / Malta · `LA` Louisiana / Laos ·
`ME` Maine / Montenegro · `AL` Alabama / Albania · `AR` Arkansas / Argentina · `CO` Colorado /
Colombia · `MS` Mississippi / Montserrat · `NC` North Carolina / New Caledonia

**Verify whether that sibling exists and whether it guards on country before trusting this family of
workflows.**

### 3. Territories and military addresses are out of scope

Not included: Puerto Rico, Guam, U.S. Virgin Islands, American Samoa, Northern Mariana Islands, and
Armed Forces designations (AA / AE / AP). Whether those should resolve to `United States` is a
business decision, not an oversight — but it should be recorded as a decision either way, since
HubSpot treats several of them as their own country values.

## Verify

- Confirm the written value matches the Salesforce country picklist exactly, if state/country
  picklists are enabled there. A country string HubSpot accepts and Salesforce rejects converts a
  blank-country problem into a sync-validation problem.
- Spot-check enrollment history for any contact whose prior country was not blank — those are the
  overwrites, and the ones most likely to be wrong.

## Related

- MKB-8332 — Breeze workflows preventing sync-error categories at the data level. If this workflow
  exists to stop a Salesforce state/country validation failure, it belongs in that count.
- `reference/mops-kb-library.md` — naming, index, and the Definition-of-Done creation rule.
