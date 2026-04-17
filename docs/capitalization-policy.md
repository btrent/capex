# Software Capitalization Policy

**Status:** Draft — pending Finance Controller sign-off
**Owner:** Engineering Finance
**Applies to:** [Your Company] internal engineering organization
**Effective:** FY2026
**Governing standard:** ASC 350-40 (Internal-Use Software)

---

## 1. Purpose

Define how the company identifies, measures, and records internally developed software costs as capitalized assets rather than operating expense. Goal is consistent application across engineering teams so that financial statements accurately reflect the value of software assets being built and the economic cost of software being consumed.

## 2. Scope

**In scope (v1):**
- Internal-use software developed by the company's engineering team for use in delivering the company's SaaS product.
- Governed by **ASC 350-40, Internal-Use Software**.
- Direct labor of full-time employees assigned to in-scope projects.

**Out of scope (v1):**
- **ASC 985-20** (software to be sold, leased, or otherwise marketed). The company does not sell software-as-a-product today; revenue is subscription access to the platform. If business model changes, this policy must be revisited.
- **Contractor / staff-aug spend.** Explicitly excluded from v1 to keep the initial system simple. Revisit in v2 once labor-based capitalization is stable.
- Hardware, hosted infrastructure (AWS, vendor SaaS), and third-party software licenses — tracked separately under their own policies.

## 3. The Three Stages (ASC 350-40)

Every capitalizable project passes through three stages. Only costs in the Application Development stage are capitalized.

| Stage | Capitalize? | What happens here |
|---|---|---|
| Preliminary | No (expense) | Conceptual formulation, alternatives evaluation, vendor selection, feasibility |
| Application Development | **Yes** | Design of chosen path, coding, installation, testing (including parallel testing prior to go-live) |
| Post-Implementation | No (expense) | Training, ongoing maintenance, bug fixes, minor enhancements |

### SaaS engineering examples

| Activity | Stage | Cap? |
|---|---|---|
| Discovery spike: "should we build or buy an SSO provider?" | Preliminary | No |
| Architecture RFC for new billing engine | Preliminary | No |
| Writing code, QA, production readiness review for new billing engine | Application Development | **Yes** |
| Pre-launch load testing of billing engine | Application Development | **Yes** |
| Post-launch hotfix on billing engine | Post-Implementation | No |
| Routine dependency upgrades on shipped code | Post-Implementation | No |
| Net-new mobile feature (e.g., new visitor type) | Application Development | **Yes** |
| Refactor of unchanged functionality (no new capability) | Post-Implementation / maintenance | No |
| New infra platform enabling new features (e.g., event bus) | Application Development (for the enabling build) | **Yes** |

## 4. Capitalizable Costs

**Capitalizable (v1):**
- **Direct labor, fully loaded.** Time spent by full-time engineers, EMs, designers, and PMs on Application Development stage work for in-scope projects. Fully loaded cost = base salary + employer taxes + benefits (health, 401k match, etc.). Stock-based compensation **is** included per ASC 718 / 350-40 guidance.

**Not capitalizable:**
- Contractor and staff-augmentation spend (excluded in v1; revisit in v2).
- Training of users or developers.
- Data conversion costs (unless meeting the narrow ASC 350-40 exception for new data structures; default: expense).
- Research, discovery, feasibility, vendor selection (Preliminary stage).
- Routine maintenance and bug fixes after placed-in-service date.
- Administrative and general overhead not traceable to a specific project.
- Idle time, PTO, on-call, all-hands, performance reviews, hiring activities.

## 5. Useful Life and Amortization

- **Default useful life: 36 months (3 years), straight-line.**
- Amortization begins the month the asset is placed in service.
- Finance (Eng Finance partner + Controller) may override the default per project if there is documented justification (e.g., short-lived migration tool = 12 months; platform expected to run much longer = up to 5 years). Overrides must be recorded in the Asset Register with a rationale note.
- Partial-month convention: full month of amortization in the month of placed-in-service.

## 6. Placed-in-Service Trigger

An asset is placed in service on the date of the **first production release delivering the intended functionality to end users** (internal or external). In practice this is the date of the production deploy that "ships" the feature, not the merge date and not the GA announcement date.

- If a project ships in phased rollouts (e.g., 1% → 50% → 100%), placed-in-service = date of the first production rollout that delivers meaningful functionality (usually the 1% cut, if users can exercise the feature).
- The Epic's `Placed in Service Date` field in Jira is the authoritative record.

## 7. Impairment and Retirement

**Impairment (project killed pre-launch):**
If a project is abandoned before being placed in service, **expense the full accumulated capitalized cost** in the period of abandonment. Do not amortize going forward; write off to the P&L.

**Retirement (asset removed from service):**
If a placed-in-service asset is retired (feature sunset, system replaced), **write off the remaining net book value** in the retirement period. Note the retirement date and reason in the Asset Register.

**Impairment trigger review:** Quarterly, Finance reviews the Asset Register for indicators of impairment (project scope materially reduced, technology no longer in use, business line discontinued). Material impairments are escalated to the Controller.

## 8. Governance

| Role | Responsibility |
|---|---|
| **Engineering Manager (EM)** | Classifies each Epic: CapEx Eligible (Yes/No/TBD), Stage, Project Code. Updates fields as stage changes. Sets Placed in Service Date at launch. |
| **Tech Lead** | Supports the EM; sanity-checks classification during Epic refinement. |
| **Eng Finance Partner** | Monthly audit of classifications, reconciles report to GL, reviews anomalies, loads asset register. First line of dispute resolution. |
| **VP Engineering** | Escalation for contested classifications; signs off on impairments of material projects. |
| **Controller** | Policy owner; signs off on useful life overrides, material impairments, and policy changes. |
| **Internal Audit** | Quarterly audit of a sample of capitalized Epics. Reviews source Jira records, time allocations, and placed-in-service documentation. |

### Dispute escalation path

EM classification → Eng Finance Partner → VP Engineering → Controller. Escalate only when the prior level has reviewed and disagrees — don't skip levels.

### Cadence

- **Monthly:** EMs verify fields by working day -3. Eng Finance Partner reconciles and flags anomalies.
- **Quarterly:** Internal audit samples N epics (target: 10% of closed capitalized Epics, minimum 5), verifies classification and documentation.
- **Annually:** Policy reviewed by Controller and VP Eng. Updates logged below.

## 9. Documentation Requirements

For each capitalized Epic, the following must exist:

- Jira Epic with `CapEx Eligible = Yes`, `CapEx Stage` set, `CapEx Project Code` assigned.
- `Placed in Service Date` populated at go-live.
- At least one description or RFC linked from the Epic explaining what is being built (used by auditors to corroborate new functionality vs. maintenance).

## 10. Change Log

| Date | Version | Change | Author |
|---|---|---|---|
| 2026-04-16 | 0.1 | Initial draft. Scope: ASC 350-40 only. Contractors excluded. 3-year default useful life. | Eng Finance |

