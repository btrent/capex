# Finance Process: Monthly Capitalization Close

**Audience:** Engineering Finance partner and Accounting close team
**Goal:** Run the monthly capitalization close repeatably, reconcile to GL, and flag anomalies before books close.

> Living doc. Propose changes via PR. Policy: [`capitalization-policy.md`](./capitalization-policy.md).

---

## 1. Cadence overview

Close runs against the Accounting team's standard working-day calendar. `WD-N` = N working days before month-end; `WD+N` = N working days after.

| Day | Who | What |
|---|---|---|
| **WD-3** | EMs | Verify all closed Epics this month have correct `CapEx Eligible`, `CapEx Stage`, `Placed in Service Date`. Run the 15-min EM checklist (see `engineering-guide.md` §6). |
| **WD-1** | Eng Finance partner | Sanity-check Jira state: run the JQL filter, scan for obvious miscategorizations, ping EMs on anything suspicious. |
| **WD+1, 06:00 UTC** | Automated | Scheduled report script runs. Pulls Jira Epics + engineer cost data, produces `CapEx_Report_YYYY-MM.xlsx`, drops it in the shared Drive folder, emails the distribution list. |
| **WD+2** | Eng Finance partner | Review report. Sanity checks: total within expected range (~30% of eng salary; see §2). Flag any anomalies to EMs; get resolution same day. |
| **WD+3** | Accounting | Load report into `CapEx_AssetRegister_FYxxxx.xlsx`. New projects get new Asset Register rows. Amortization computed. JEs drafted from the helper tab. |
| **WD+4** | Accounting + Controller | Controller reviews JEs. Posts to GL. |
| **WD+5** | All | Close complete. File report + JE backup in close binder. |

**Distribution list for the report email:**
Eng Finance partner, Controller, VP Engineering, Accounting close team, Internal Audit (read-only).

**Drive location:**
`Finance / CapEx / FYxxxx / YYYY-MM /` — contains the generated XLSX and any supporting notes.

## 2. Reconciliation to GL

### Expected ratio

Target: capitalized labor should be **~30% of total engineering salary expense** in the period (typical for a SaaS company; adjust to your actual engineering spend and expected capitalizable ratio under ASC 350-40).

| Observed ratio | Action |
|---|---|
| 25%-35% | Normal. Proceed. |
| 20%-25% **or** 35%-40% | Yellow flag. Document reason (seasonality, major launch, planning cycle). Brief note in close binder. |
| **<20% or >40%** | Red flag. Halt close. Investigate before posting JEs. |

### Reconciliation procedure

1. Pull total engineering-department salary expense from GL for the period (fully loaded: salary + employer taxes + benefits). Use the same cost basis as the report uses for engineers. Include stock-based comp if the report includes it.
2. Pull total capitalized labor from the report's Summary tab.
3. Compute ratio = capitalized / total.
4. Compare to prior 3 months rolling average; alert if delta > 10 percentage points month-over-month.
5. If red flag: investigate common causes in this order:
    - Jira coverage gap: are engineer account IDs in `config/engineer_costs.csv` complete? Missing engineers under-report.
    - Classification drift: are EMs marking too many / too few Epics as eligible? Sample a few.
    - Cost data stale: did someone join or leave without the cost CSV being updated?
    - Period mismatch: are we comparing the same period on both sides?

## 3. Handling a killed project mid-development

When an Epic is abandoned before placed-in-service, capitalized costs accumulated to date must be **expensed in the period of abandonment** (policy §7).

Procedure:

1. **Identify.** EM flags the kill at Epic close (resolution like `Won't Do`), or Eng Finance partner catches it at WD-1 review.
2. **Quantify.** Pull all labor capitalized to that Epic's Project Code to date from the Asset Register. Sum = write-off amount.
3. **Record in Asset Register.** Mark the project `Retired - Abandoned`, retirement date = current period, reason noted.
4. **Journal entry** (example):
    ```
    Dr.  Impairment / Abandoned Software Expense     $X
    Cr.  Capitalized Software - In Development      $X
    ```
5. **Disclose.** If material (per Controller's threshold), note in the close binder for external audit trail. Internal Audit reviews quarterly.

**Guardrail:** do NOT continue to capitalize to a known-killed Epic in the following period. The Epic should be closed in Jira and the Project Code marked inactive in `config/projects.yaml`.

## 4. Anomaly playbook

Common anomalies and first-pass handling:

| Anomaly | First action |
|---|---|
| Total capex $ is way above prior month | Check for a major launch — large Epic moved from open to closed. Usually legitimate. Confirm placed-in-service is correct. |
| Total capex $ is way below prior month | Check for missing engineer cost entries (new hires not added to CSV). Check for EMs marking everything `No` in an overcautious sprint. |
| An Epic has no placed-in-service date but is closed and `Yes` | The automation rule should have nagged. Follow up with the reporter. Do not capitalize past the close of the Epic. |
| An Epic has placed-in-service in a prior period but shows up as new this period | Check the report script's date filtering. Likely a re-opened Epic or a date correction. |
| Negative amortization row | Bug in the Amortization tab formula. Investigate before close; do not post. |
| Engineer in the cost CSV with no Jira account ID match | Their time won't be allocated. Fix the CSV; re-run the report. |

## 5. Contacts and escalation

| Issue | Contact |
|---|---|
| Classification questions (is this Epic capex?) | **Eng Finance partner** (first stop). |
| Policy interpretation (novel situation not covered) | Eng Finance partner → **VP Engineering** → **Controller**. |
| Report script errors / data issues | Eng Finance partner (they own the script; if they're out, the Engineering platform team owns the runtime). |
| Material impairments, useful life overrides, policy changes | **Controller** must sign off. |
| Audit requests (internal or external) | Controller + Eng Finance partner. |

Escalate in order — don't skip the Eng Finance partner. They resolve ~90% of questions.

## 6. Quarterly tasks

In addition to monthly close:

- **Internal Audit sample review.** Internal Audit pulls ~10% of capitalized Epics (min 5) and verifies classification and placed-in-service dates against Epic history. Eng Finance partner supports with data pulls.
- **Impairment indicator review.** Scan the Asset Register for projects with reduced scope, unused tech, or discontinued business lines. Escalate material items to the Controller.
- **Ratio trend review.** Look at the monthly capitalized/total ratio across the quarter; smooth out any period-specific distortions when reporting to leadership.

## 7. Annual tasks

- **Useful life re-assessment.** Review in-service assets for any whose expected life has changed materially. Controller approves any changes.
- **Policy review.** Read `capitalization-policy.md` end-to-end with VP Eng and Controller. Log updates to the change log.
- **Contractor scope revisit (v2).** Decide whether to expand v1 scope to include contractor labor.

