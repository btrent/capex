# Next Steps — Go-Live Checklist

Ordered list of actions required before the first live monthly capex close. Owners are suggestive; adjust to your org.

Status: **Draft — pending execution.**

---

## 1. Finance Controller policy sign-off
**Owner:** Controller (reviewer), VP Eng (co-signer)
**Blocks:** everything else

Review [`docs/capitalization-policy.md`](./docs/capitalization-policy.md) end-to-end. Specifically confirm or revise the opinionated defaults the documentation agent flagged:

- [ ] **Stock-based comp** treated as capitalizable (ASC 350-40/718 permits this) — accept or exclude for v1?
- [ ] **Placed-in-service = first 1% production rollout** (not GA) — is this the amortization-start trigger you want?
- [ ] **3-year default useful life** with per-project overrides documented in `config/projects.yaml`.
- [ ] **Reconciliation bands:** 20%-40% green, <20% or >40% halts close. Adjust if too tight/loose.
- [ ] **Contractor labor out of scope for v1** — acceptable, or does it need to be in from day one?
- [ ] **Internal audit quarterly sample:** 10% of capitalized Epics, min 5. Adjust per Internal Audit's risk framework.

Sign-off recorded in the change log at the bottom of the policy doc.

---

## 2. Jira admin creates custom fields; capture real IDs
**Owner:** Jira Cloud admin
**Depends on:** (1)

Execute [`docs/jira-setup.md`](./docs/jira-setup.md):

- [ ] Create 4 custom fields on Epic: `CapEx Eligible`, `CapEx Stage`, `CapEx Project Code`, `Placed in Service Date`.
- [ ] Apply to all projects (recommended) or scope as documented.
- [ ] Add fields to Epic Create/View/Edit screens.
- [ ] Set up the "missing placed-in-service on Done" Jira Automation rule.
- [ ] Retrieve the real `customfield_XXXXX` IDs via `GET /rest/api/3/field` (curl example in setup doc).
- [ ] Update `scripts/config.example.yaml` → copy to `scripts/config.yaml` with real field IDs.
- [ ] EMs backfill capex classification on currently-open Epics.

---

## 3. Populate runtime config (Drive, email, Slack)
**Owner:** Eng Finance partner + VP Eng delegate
**Depends on:** (2)

Replace placeholders in `scripts/config.example.yaml`:

- [ ] `delivery.drive_folder_id` — create folder `Finance/CapEx/FY2026/` in the Finance shared drive, copy its ID.
- [ ] `delivery.email.from` and `delivery.email.to` — agree distribution list with Finance.
- [ ] `delivery.email.smtp_host/port` — confirm SMTP path (Gmail relay or company MTA).
- [ ] Slack channel for failure notifications (currently placeholder `#eng-capex-ops`).
- [ ] Update `config/projects.yaml` with real in-flight projects (replace sample entries).
- [ ] Finance exports the first real `config/engineer_costs.csv` from HRIS (fully-loaded monthly cost per engineer, keyed by Jira accountId).

---

## 4. Add GitHub Actions secrets
**Owner:** Repo admin
**Depends on:** (3)

Add these 5 secrets in repo Settings → Secrets and variables → Actions:

- [ ] `JIRA_EMAIL` — service account email for Jira API.
- [ ] `JIRA_API_TOKEN` — generated at https://id.atlassian.com/manage-profile/security/api-tokens.
- [ ] `SMTP_USER`, `SMTP_PASS` — email sender creds (or app password if Gmail).
- [ ] `GOOGLE_SERVICE_ACCOUNT_JSON` — JSON key for a GCP service account with Drive write access to the CapEx folder.
- [ ] *(Optional)* `SLACK_WEBHOOK_URL` — for workflow-failure alerts. Workflow skips gracefully if unset.

Rotate `JIRA_API_TOKEN` annually.

---

## 5. Manual dry-run against last month; Finance validates
**Owner:** Eng Finance partner + Controller
**Depends on:** (4)

- [ ] Trigger `.github/workflows/monthly-capex-report.yml` via **Run workflow** with `month = 2026-03` (prior month) and `dry_run = true`.
- [ ] Download the XLSX artifact from the workflow run.
- [ ] Sanity-check output:
  - Is the total capitalized roughly ~30% of engineering salary expense that month?
  - Are the top projects by dollars the ones Finance expects?
  - Any engineers with surprising ratios (>80% capex or <5%)? Investigate.
  - Check the `Warnings` tab — missing story points, missing engineers.
- [ ] Walk Internal Audit (or external auditor if close to year-end) through the methodology and sample documentation.
- [ ] If all green: enable the cron schedule and run live the following month.

---

## Post-launch (first 90 days)

- [ ] End-of-month 1 retro with Finance: what was confusing in the report, what did accountants have to hand-fix?
- [ ] End-of-quarter 1: first quarterly Internal Audit sample review — pick 3-5 capex Epics at random, verify classification was correct.
- [ ] Re-evaluate whether to bring contractor labor in scope for v2.
- [ ] Re-evaluate whether to migrate off the XLSX asset register (triggers in [`docs/accounting-guide.md §6`](./docs/accounting-guide.md#6-when-to-migrate-off-the-spreadsheet)).
