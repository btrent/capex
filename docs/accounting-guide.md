# Accounting Guide: CapEx Asset Register

**Audience:** Accountant maintaining the CapEx asset register spreadsheet
**Goal:** Keep the XLSX asset register current each month, produce clean JEs, and know when to migrate off the spreadsheet.

> Living doc. Propose changes via PR. Policy: [`capitalization-policy.md`](./capitalization-policy.md).

---

## 1. Getting started: copy the template

Each fiscal year, create a fresh file from the starter template.

1. Open the template: `Finance/CapEx/Templates/CapEx_AssetRegister_TEMPLATE.xlsx` (owned by the other agent; same repository).
2. **File → Make a copy** (or Save As) into `Finance/CapEx/FY2026/`.
3. Rename: `CapEx_AssetRegister_FY2026.xlsx`. (Use `FYxxxx` for your fiscal year.)
4. Lock permissions: editors = Eng Finance partner, Controller, Accounting close lead. Everyone else = viewer.
5. On the `Instructions` tab, update the **"Fiscal Year"** cell and the **"Last updated"** cell at top.
6. Commit the file's path into the close binder so close team knows where it lives.

One file per fiscal year keeps amortization schedules manageable and gives auditors a clean boundary. Assets remaining in service at year-end are copied forward into the next year's file on the first close of the new FY.

## 2. Tab reference

| Tab | Purpose |
|---|---|
| **Instructions** | Cover sheet. Explains what each tab does, lists the owner, last-updated date, and fiscal year. Read first if unfamiliar. |
| **Asset Register** | One row per capitalized project. Source of truth for assets in service. Columns: Project Code, Name, Owner Team, Placed-in-Service Date, Useful Life (months), Total Capitalized Cost, Status (Active / Retired / Abandoned), Retirement Date, Notes. |
| **Monthly Additions** | Append-only log of labor capitalized each month by project code. Columns: Period, Project Code, Amount, Source Report Filename. Fed from the monthly report. |
| **Amortization Schedule** | Auto-computed. One column per period, one row per asset. Straight-line. References Asset Register. |
| **Summary Dashboard** | Roll-ups: total gross capitalized, total accumulated amortization, net book value, monthly additions trend, active project count. Charts. Read-only — formulas only. |
| **Journal Entry Helper** | Generates JE lines from Monthly Additions and the Amortization Schedule for the current period. Copy/paste into the GL import. |

## 3. Monthly workflow

Runs WD+3 per `finance-process.md`. Assumes the monthly report XLSX is in the Drive folder.

1. **Open** `CapEx_AssetRegister_FY2026.xlsx`.
2. **Open** the monthly report `CapEx_Report_YYYY-MM.xlsx` alongside it.
3. **Copy new Project Codes into Asset Register.**
    - Any Project Code in the report that is NOT yet a row in `Asset Register` = a new asset.
    - Add a row. Fill Project Code, Name, Owner (from `config/projects.yaml`), Placed-in-Service Date (from the Jira report), Useful Life (default 36 months unless Finance has documented an override in `projects.yaml`), Status = `Active`.
    - Total Capitalized Cost = this month's addition; will grow over time as the project continues in Application Development.
4. **Append to Monthly Additions.**
    - For each (Project Code, Amount) pair from the report, append one row to `Monthly Additions`.
    - Period = the closing month (e.g., `2026-04`). Source Report Filename = the exact report file name (for audit trail).
    - The `Total Capitalized Cost` column on Asset Register is a SUMIF against Monthly Additions; it updates automatically.
5. **Verify Amortization Schedule updated.**
    - For assets with Placed-in-Service date in the current or prior months, amortization for the current period should auto-populate.
    - Assets still in Application Development (no Placed-in-Service date) should show `$0` amortization — they're "in development", not yet amortizing.
6. **Generate JEs from Journal Entry Helper.**
    - The helper tab produces four standard JE blocks (see §4 below). Copy the current-period block into the GL import template.
7. **Sanity checks** before posting:
    - Net book value ≥ 0 for all rows.
    - Sum of amortization expense JE = sum of amortization column for current period on Amortization Schedule.
    - Sum of capitalization JE = sum of Monthly Additions rows for current period.
    - No duplicate Project Codes in Asset Register.
8. **Save** the file. Commit the period to the close binder.

## 4. Sample journal entries

Currency: USD. Accounts illustrative — use actual GL accounts per the chart of accounts.

### 4a. Monthly capitalization

When labor is capitalized (i.e., costs already hit P&L as salary expense; this JE moves them to the balance sheet via a contra-expense).

```
Dr.  Capitalized Software - In Development    $XXX,XXX
    Cr.  Capitalized Labor (contra-expense)        $XXX,XXX
```

Detail line per Project Code (the Asset Register is the subsidiary ledger).

### 4b. Monthly amortization

For each in-service asset.

```
Dr.  Amortization Expense - Software          $XX,XXX
    Cr.  Accumulated Amortization - Software       $XX,XXX
```

Detail line per asset. Amount = Total Capitalized Cost / Useful Life (months).

### 4c. Placed-in-service reclass

When an asset moves from in-development to in-service (first month amortizing):

```
Dr.  Capitalized Software - Placed in Service   $X,XXX,XXX
    Cr.  Capitalized Software - In Development      $X,XXX,XXX
```

This moves the prior accumulated cost out of the "WIP" software account and into the active asset account. Amortization begins this month.

### 4d. Impairment (project killed pre-launch)

Accumulated capitalized cost is written off (policy §7).

```
Dr.  Impairment / Abandoned Software Expense  $XXX,XXX
    Cr.  Capitalized Software - In Development    $XXX,XXX
```

Asset Register: set Status = `Abandoned`, Retirement Date = current period, add a note.

### 4e. Retirement (asset removed from service)

Write off remaining net book value.

```
Dr.  Accumulated Amortization - Software      $XXX,XXX   (remove accumulated amort)
Dr.  Loss on Retirement of Software           $XX,XXX    (remaining NBV)
    Cr.  Capitalized Software - Placed in Service   $X,XXX,XXX  (original cost)
```

Asset Register: Status = `Retired`, Retirement Date = current period, note the reason.

## 5. Year-end rollover

On the first close of a new fiscal year:

1. Create next year's file from the template (§1).
2. Copy all **Active** rows from this year's Asset Register to next year's Asset Register. Do not copy Abandoned or fully-amortized-and-Retired rows (those rows stay archived in the prior year's file).
3. Monthly Additions starts empty (append-only log is per-fiscal-year).
4. Amortization Schedule auto-rebuilds from Asset Register; confirm prior accumulated amortization carries via the `Prior Accumulated` column on Asset Register.
5. Reconcile Dec 31 / FY-end net book value across files: end of old file = start of new file.

## 6. When to migrate off the spreadsheet

The XLSX is deliberately simple — fine for v1, not forever. Escalate to the Controller to fund a proper fixed-asset / intangible-asset system when any of these triggers:

- **>50 active projects on the Asset Register.** Spreadsheet row-level formulas start to lag and error rates climb.
- **External audit finding** related to the register (completeness, accuracy, control design). Audit expectations scale with company stage.
- **M&A activity.** Acquisition adds a different register with different conventions; consolidation is painful in Excel.
- **Revenue > ~$250MM ARR** or **public filing preparation.** SOX-grade controls want a system of record, not a spreadsheet.
- **>2 full FY rollovers.** By that point the pattern is proven and the business case for a real system is easy to make.

Candidate systems: NetSuite FAM, Sage Intacct Fixed Assets, or a dedicated intangible-asset module in whichever ERP your company standardizes on.

## 7. Contacts

- **Eng Finance partner** — source-of-truth for the monthly report, classification questions.
- **Controller** — signs off on useful-life overrides, impairments, JEs, policy changes.
- **Internal Audit** — quarterly sample reviews; provide register extracts on request.

See `finance-process.md` for escalation path.

