# CLAUDE.md — Agent Context for the CapEx Project

Read this before editing anything in this repo. This file captures non-obvious design decisions, known gotchas, and conventions that are not derivable from the code.

---

## What this project is

Internal tooling + documentation for **software capitalization process** under **ASC 350-40** (internal-use software). Three user groups:

1. **Engineering** tags Epics in Jira with 4 custom fields. No per-ticket time logging.
2. **A monthly Python report** (GH Actions cron, 06:00 UTC on the 1st) pulls Jira data and emits an XLSX for Finance.
3. **Accounting** maintains an asset register XLSX (starter template provided) and posts monthly JEs.

Org scale: sized for $10–100M ARR SaaS businesses with engineering teams of 20–200. Expected capitalizable ratio is typically 20–40% of engineering spend.

**Status:** Draft. Pending Finance Controller sign-off on policy + first live monthly run.

---

## Critical design decisions (and why)

Do not casually reverse these. They are load-bearing.

| Decision | Why | If you're tempted to change this... |
|---|---|---|
| **Epic-level tagging, not per-ticket time tracking** | Per-ticket time logs are the #1 reason capex processes fail at SaaS shops. Engineers won't do it. | Don't. If finer granularity is required, upgrade to Tempo, don't bolt on worklog requirements. |
| **Story points as effort proxy** | Points are already captured for planning. No new engineer burden. Noisy at individual level but fine aggregated. | Keep. Document the assumption when reporting to auditors. |
| **ASC 350-40 only (not ASC 985-20)** | The company doesn't sell software as a product. 985-20 would be wrong scope. | If the company ships an SDK/on-prem product, ASC 985-20 would apply — new policy doc needed. |
| **GitHub Actions for cron, not dedicated infra** | Zero ops burden. Secrets in GH Secrets. Versioned alongside code. | Only move to dedicated infra if runtime >30min or if secrets model changes. |
| **Stock-based comp IS capitalizable** (per policy §4) | ASC 350-40 + ASC 718 permits it. Excluding it understates the asset. | Finance Controller may want to exclude for v1 simplicity — that's a one-line policy edit, not an architectural change. |
| **Placed-in-service = first 1% production rollout** | Conservative amortization-start trigger. Standard at feature-flagged SaaS. | If Finance prefers GA-date, update policy doc + `Placed in Service Date` usage in engineering-guide. |
| **3-year default useful life** | Industry standard for SaaS internal-use software. | Per-project overrides live in `config/projects.yaml` → `useful_life_months`. |
| **Contractor labor out of scope for v1** | Simplifies first rollout. Different cost-input pipeline (invoices not payroll). | v2 work; use the same allocation framework, different data source. |

---

## File ownership map

| Area | Source of truth | Who edits it |
|---|---|---|
| Policy (what's capex) | `docs/capitalization-policy.md` | Finance Controller approves; Eng Finance partner drafts |
| Jira field definitions | `docs/jira-setup.md` + `scripts/config.example.yaml` `jira.custom_fields` | Jira admin |
| Allocation math | `scripts/monthly_capex_report.py` (fn `compute_allocations`) | Engineer |
| Project registry | `config/projects.yaml` | Eng Finance partner (PR review) |
| Engineer cost data | `config/engineer_costs.csv` (gitignored; real file lives in Drive) | Finance, monthly refresh from HRIS |
| Accounting template | `templates/capex_asset_register.xlsx` (generated) + `scripts/build_asset_register_template.py` (source) | Accountant uses template; Engineer edits generator |

**Always edit the generator, never the generated XLSX directly.** Run `python scripts/build_asset_register_template.py` to regenerate.

---

## Config schema contract

`config/projects.yaml` is consumed by `monthly_capex_report.py`. The schema contract is:

```yaml
projects:
  - code: <string, required>              # matches Jira CapEx Project Code field verbatim
    name: <string, required>              # human-readable
    useful_life_months: <int, required>   # 36 default; override per-project
    # these are additional fields the docs use but the script ignores:
    owner: <string>                       # team slug, display only
    status: <active|retired|abandoned>    # not yet enforced, v2 will gate
    notes: <string>                       # free-form
```

If you add a required field to the script, update the schema doc in `config/projects.yaml`'s top comment AND `docs/accounting-guide.md` simultaneously.

---

## How to run / test locally

```bash
# one-time setup
python -m venv .venv && source .venv/bin/activate
pip install -r scripts/requirements.txt

# run the tests (should be 7 passing, ~0.2s)
pytest scripts/tests/ -v

# syntax check only
python -c "import ast; ast.parse(open('scripts/monthly_capex_report.py').read())"

# dry-run the report against mock fixtures (no network)
# (add a --fixtures flag if you build one; currently tests use fixtures directly)

# regenerate the XLSX template
python scripts/build_asset_register_template.py

# validate GH Actions workflow yaml
python -c "import yaml; yaml.safe_load(open('.github/workflows/monthly-capex-report.yml'))"
```

**The venv already exists** at `.venv/` if a prior run left it. Reuse it.

---

## Known gotchas

### Jira Cloud custom-field-on-child quirk
Jira Cloud's REST API does NOT reliably return parent-Epic custom fields when you query child stories. The script works around this by:
1. Querying all child issues resolved in month M by `resolutiondate`.
2. Collecting unique parent Epic keys.
3. Fetching each Epic in a second pass via `GET /rest/api/3/issue/{key}` to read its capex fields.

If you refactor to a single-query approach you will get empty capex fields for most stories. Don't.

### Story-point missing → fallback to 1
Stories without story points are treated as 1 point and a warning is added to the `Warnings` tab. This is conservative (avoids crash, under-weights the story). Don't change the fallback without updating the tests and the policy doc.

### Custom field IDs are NOT hardcoded
All `customfield_XXXXX` references live in `scripts/config.example.yaml` → `jira.custom_fields`. If someone files a bug saying "fields aren't being read," check that they copied `config.example.yaml` to `config.yaml` and populated real IDs from their Jira instance.

### XLSX Summary Dashboard has hardcoded year strings
`templates/capex_asset_register.xlsx` Summary Dashboard uses `SUMIF` with `"2026-01"`-style keys. These need annual update, or the accountant swaps to a new file per fiscal year (the accepted convention). A future improvement: replace with `YEAR()` formulas.

### GH Actions schedule drift
`cron: '0 6 1 * *'` is UTC. If the org moves to a different accounting close window, update BOTH the cron AND the description in `docs/finance-process.md §1`.

### Drive upload is best-effort, Jira auth is not
The script exits non-zero on Jira auth failure (exit 2), no-issues-found (exit 3), warning-threshold breach (exit 4). Drive upload failures emit a warning and continue (the XLSX is always uploaded as a GH Actions artifact, so the report is retrievable either way).

---

## Troubleshooting common failures

| Symptom | Likely cause | Fix |
|---|---|---|
| Script exits 3 ("no issues found") | JQL misconfigured or wrong `customfield_XXXXX` IDs | Run `curl -u email:token $JIRA_BASE_URL/rest/api/3/field` and update `config.yaml` |
| Many engineers missing from report | `config/engineer_costs.csv` stale; new hires not added | Finance re-exports from HRIS |
| Capex ratio way off (>40% or <20%) | Either a classification error (EMs over/under tagging) or a legitimate launch-heavy / maintenance-heavy month | Check `By Project` tab for anomalies; spot-check 3 Epics |
| XLSX opens but formulas broken | Regenerated template incompatible with old data | Regenerate via `build_asset_register_template.py`; if the accountant has live data, manually port rows |
| GH Actions run succeeded but no email | SMTP creds rotated or `delivery.email` not configured | Check `SMTP_USER`/`SMTP_PASS` secrets; check logs for SMTP errors |
| pytest fails on fresh clone | `pytest` not in requirements.txt (it is now, but if removed) | `pip install pytest==8.3.3` |

---

## Do / Don't for future edits

**Do:**
- Update `docs/capitalization-policy.md` change log for any material policy change.
- Bump a `SCRIPT_VERSION` constant (if added) when changing allocation math; it appears in the `Metadata` tab of every report for audit trail.
- Add a new pytest case when changing edge-case handling (missing fields, mid-month departures, etc.).
- Keep the docs/ files in sync with code changes — the docs are the contract with non-engineers.
- When adding a new Jira custom field: update `docs/jira-setup.md`, `scripts/config.example.yaml`, the main script, and `docs/engineering-guide.md` in the same PR.

**Don't:**
- Hardcode `customfield_XXXXX` IDs in Python. Ever.
- Add a per-ticket time-logging requirement. Violates core design intent.
- Capitalize contractor labor without explicit Finance approval AND a policy update (currently out of scope).
- Edit the generated `templates/capex_asset_register.xlsx` by hand — edit the generator and regenerate.
- Remove the `Warnings` tab from the report. Auditors rely on it for methodology transparency.
- Skip the change log at the bottom of `capitalization-policy.md` — even for small edits.

---

## Open decisions / pending items

Tracked in `next_steps.md`. As of the latest commit:

1. Finance Controller has not yet signed off on the policy doc.
2. Real Jira `customfield_XXXXX` IDs are NOT yet in any committed config (placeholders only).
3. Real Drive folder ID, email distribution list, and Slack webhook are placeholders.
4. No GH Actions secrets are configured in the live repo.
5. No production dry-run has been executed.

Until (1)-(5) are resolved, the system is documentation + automation scaffolding only. Do not run the workflow against live Jira data with placeholder config.

---

## Useful references

- ASC 350-40 full text: https://asc.fasb.org/ (subscription — reference docs/capitalization-policy.md instead)
- Jira Cloud REST API v3: https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/
- openpyxl docs: https://openpyxl.readthedocs.io/
- GitHub Actions cron syntax: https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule

