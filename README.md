# Codespace Working Directory

This is the **execution surface** — where scripts run and deliverables get built.
It is a *different repo* from the brain, and the split is deliberate.

## Two repos, two jobs

| | claude-brain | this repo (`codespaces-blank`) |
|---|---|---|
| **Path** | `~/.claude/projects/-workspaces-codespaces-blank/memory/` | `/workspaces/codespaces-blank/` |
| **Remote** | `wiedenu/claude-brain` (private) | `wiedenu/codespaces-blank` |
| **Holds** | durable knowledge — notes, references, project files, skills, reusable scripts | execution — automations that run here, generated deliverables, working data |
| **Syncs via** | `brain-pull` / `brain-push` | normal `git push` (when you choose) |

**The rule:** if it's *knowledge or a reusable tool worth having on every machine*, it belongs in **claude-brain**. If it's a *data file, a one-off output, or anything with customer info*, it stays here — and if it's data, it lives in `data/` and never leaves this machine.

## Folder map

```
automations/     reusable scripts, grouped by process
  mkb6238-invoicing/   quarterly $0 invoicing sender + runbook
  landing-pages/       HubSpot landing-page classification/reporting
  hubspot-tools/       SOP PDF generation, etc.
  tumblr/              tumblr -> obsidian converter
data/            ⛔ GITIGNORED — spreadsheets, JSON, logs, PII. Never committed, never synced.
  logs/              run logs
docs/            deliverables to share out (HTML/CSS)
  day-plans/         (note: brain/day-plans/ is the live location; these may be stale)
  mkb/               ticket-specific mockups & worksheets
  modules/           HubSpot custom modules
  one-offs/          standalone pages, emails, drafts
  website-report.html  ← written by the monthly GitHub Action, do not move
reference/       SOPs, runbooks, PDFs — candidates to promote to brain
website-report/  monthly report generator (referenced by .github Action — do not move)
ai-use-cases/    workshop docs (referenced by path in brain memory — do not move)
```

## Do-not-move (hard dependencies)
- `website-report/` and `docs/website-report.html` — the GitHub Action hard-codes these paths.
- `ai-use-cases/` — referenced by absolute path in claude-brain memory.
- `hubspot.config.yml`, `*.env` — gitignored secrets the CLIs expect where they are.

## Promoting something to the brain
When a runbook/reference here becomes durable knowledge, copy it into the memory dir
(`reference/` or `scripts/`), add a one-line pointer in `MEMORY.md`, then `brain-push`.

### Drift reconciled 7/7/26
- `ai-roi-log.md` — promoted to `brain/reference/` (its canonical home; the `ai-impact-tracker` skill writes there). No longer kept here.
- `docs/day-plans/*.html` — deleted; `brain/day-plans/` is the live superset.
- `MKB-6238-RUNBOOK.md` — kept (canonical SOP); brain note `mkb6238-invoice-send.md` path pointers updated to the new `automations/` location.

## Heads-up: scripts use cwd-relative paths
These read/write plain filenames from the current directory, so **run them from the repo root**:
- `automations/mkb6238-invoicing/mkb6238-rebate-sender.py` — pass the input file as an argument (point it at `data/`). Its `.xlsx`/`.log` outputs are gitignored wherever they land.
- `automations/landing-pages/*.py` — a June one-off; their JSON inputs now live in `data/`. Re-running needs the three bare filenames repointed (ask and I'll parameterize them).
