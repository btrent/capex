# Software Capitalization (ASC 350-40)

This repository is a ready-to-fork template for how a SaaS company identifies, measures, records, and audits capitalized software development costs under **ASC 350-40**. Designed as a joint artifact of Engineering and Finance, versioned like code, and reviewed via PR.

---

## Who are you?

| You are... | Start here |
|---|---|
| **Engineering Manager or Tech Lead** — classifying Epics | [`docs/engineering-guide.md`](./docs/engineering-guide.md) |
| **Eng Finance partner or Accounting close team** — running monthly close | [`docs/finance-process.md`](./docs/finance-process.md) |
| **Accountant** — maintaining the asset register spreadsheet | [`docs/accounting-guide.md`](./docs/accounting-guide.md) |
| **Jira Cloud admin** — setting up fields, screens, automation | [`docs/jira-setup.md`](./docs/jira-setup.md) |
| **VP Eng, Controller, Internal Audit, or new-hire onboarding** — start with policy | [`docs/capitalization-policy.md`](./docs/capitalization-policy.md) |

**Canonical policy document:** [`docs/capitalization-policy.md`](./docs/capitalization-policy.md). All other docs defer to it.

---

## Quickstart

### For Engineering Managers
- Every Epic gets a 30-second classification: capex `Yes` / `No` / `TBD`.
- Fill 4 Jira fields on the Epic; update them if the stage changes.
- 15-minute monthly review before working day -3; see [engineering-guide.md §6](./docs/engineering-guide.md#6-monthly-15-minute-em-review-checklist).

### For Finance partners
- Monthly script runs WD+1; review report WD+2; Accounting posts JEs WD+3-4.
- Reconcile capitalized labor to GL: expected ~30% ratio; halt close if <20% or >40%.
- Kill-mid-development projects get expensed the period they're killed; see [finance-process.md §3](./docs/finance-process.md#3-handling-a-killed-project-mid-development).

### For Accountants
- One XLSX per fiscal year. Tabs: Instructions, Asset Register, Monthly Additions, Amortization Schedule, Summary Dashboard, Journal Entry Helper.
- Monthly: append to Monthly Additions, add new projects as Asset Register rows, copy JEs from helper tab to GL.
- Migrate off the spreadsheet when you hit any trigger in [accounting-guide.md §6](./docs/accounting-guide.md#6-when-to-migrate-off-the-spreadsheet).

---

## Architecture

High-level data flow:

```
┌────────────────────┐          ┌──────────────────────┐
│  Engineering Mgrs  │          │  HR / Payroll / Plan │
│  classify Epics    │          │  eng fully-loaded    │
│  in Jira           │          │  cost data           │
└────────┬───────────┘          └──────────┬───────────┘
         │ (4 custom fields)                │ (monthly CSV)
         ▼                                  ▼
┌────────────────────┐          ┌──────────────────────┐
│   Jira Cloud       │          │ config/              │
│   (Epics + fields) │          │  engineer_costs.csv  │
│                    │          │  projects.yaml       │
└────────┬───────────┘          └──────────┬───────────┘
         │                                  │
         └─────────────┬────────────────────┘
                       ▼
          ┌────────────────────────────┐
          │  Report script (WD+1)      │
          │  scripts/generate_report.py│
          │  (owned by other agent)    │
          └────────────┬───────────────┘
                       │ XLSX
                       ▼
          ┌────────────────────────────┐
          │  Drive: CapEx_Report_      │
          │  YYYY-MM.xlsx              │
          │  + email distribution      │
          └────────────┬───────────────┘
                       │
         ┌─────────────┴────────────────┐
         ▼                              ▼
┌────────────────────┐        ┌─────────────────────┐
│  Eng Finance WD+2  │        │  Accounting WD+3    │
│  review + anomaly  │        │  load into          │
│  triage            │        │  CapEx_AssetRegister│
└────────────────────┘        │  _FYxxxx.xlsx       │
                              │  compute amort →    │
                              │  post JEs to GL     │
                              └─────────────────────┘
```

## Repo layout

```
capex/
├── README.md                            ← you are here
├── CLAUDE.md                            ← context for AI agents iterating on this repo
├── next_steps.md                        ← go-live checklist
├── docs/
│   ├── capitalization-policy.md         ← canonical policy (ASC 350-40)
│   ├── engineering-guide.md             ← for EMs / Tech Leads
│   ├── finance-process.md               ← for Eng Finance + Accounting close
│   ├── accounting-guide.md              ← for the asset-register accountant
│   └── jira-setup.md                    ← for the Jira admin
├── scripts/
│   ├── monthly_capex_report.py          ← the monthly report generator
│   ├── build_asset_register_template.py ← regenerates the XLSX template
│   ├── requirements.txt                 ← pinned Python deps
│   ├── config.example.yaml              ← template config (copy to config.yaml)
│   └── tests/
│       ├── test_allocation.py           ← 7 pytest tests for allocation math
│       └── fixtures/sample_issues.json  ← mock Jira payload
├── .github/workflows/
│   └── monthly-capex-report.yml         ← GH Actions cron (1st of month, 06:00 UTC)
├── templates/
│   └── capex_asset_register.xlsx        ← starter workbook for accounting
└── config/
    ├── projects.yaml                    ← project code registry (sample)
    ├── engineer_costs.example.csv       ← fake sample; real file gitignored
    └── .gitignore
```

## Running the report locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r scripts/requirements.txt
cp scripts/config.example.yaml scripts/config.yaml   # edit with real values
pytest scripts/tests/                                 # 7 tests should pass
python scripts/monthly_capex_report.py \
    --month 2026-03 --config scripts/config.yaml \
    --out /tmp/capex_2026-03.xlsx --dry-run
```

Rebuild the accounting XLSX template after design changes:

```bash
python scripts/build_asset_register_template.py
```

## Related

- GAAP reference: [ASC 350-40 — Internal-Use Software](https://asc.fasb.org/) (subscription required).
- Out of scope for v1: ASC 985-20 (software to be sold), contractor labor. See policy §2.

## License

This project is licensed under the MIT License. See [LICENSE](./LICENSE) for details.

