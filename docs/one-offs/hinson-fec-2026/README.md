# Case data — Hinson campaign expense analysis (August 2026)

Supporting data for
[`../hinson-campaign-expense-schedule-analysis-2026-08-31.md`](../hinson-campaign-expense-schedule-analysis-2026-08-31.md).

Generated with [`tools/fec-committee-analysis/`](../../../tools/fec-committee-analysis/).

| File | What it is |
|---|---|
| `ashley-for-iowa-disbursements.csv` | All 7,210 de-duplicated disbursements by FEC committee `C00706267`, cycles 2020/2022/2024/2026, through the Q2 2026 report (June 30, 2026). The full primary-source extract. |
| `lodging-set.csv` | The 10 transactions / 8 properties behind the article's "nearly $10,000" claim. Totals **$9,559.20**. |
| `amex-batch-2026-03-16.csv` | The 24 memo sub-items under one $5,568.24 American Express payment — the proof that FEC dates on memo rows are statement dates. Contains the Lido House charge alongside a storage-unit bill and a gas station. |
| `dining-aggregates.csv` | Each dining figure the article cites, with the verified FEC total. |
| `vote-crosscheck.csv` | Each lodging date against the House roll call record, plus the Greenbrier control case. |
| `article-source-text.md` | Transcription of the source article, for provenance. |

Reproduce:

```bash
cd tools/fec-committee-analysis
python3 fec_extract.py --committee C00706267 --cycles 2020 2022 2024 2026 --out out.csv
python3 flag_date_artifacts.py out.csv --vendor "LIDO HOUSE"
python3 house_votes.py --years 2022 2024 2026 --member Hinson --dates 2022-04-27 2024-03-22
```
