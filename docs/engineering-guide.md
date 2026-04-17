# Engineering Guide: Software Capitalization

**Audience:** Engineering Managers and Tech Leads
**TL;DR:** When you create an Epic, decide if it's capex. Fill 4 Jira fields. Update them if stage changes. 15 min/month review.

---

## 1. Why you're reading this

Your company capitalizes ~30% of engineering spend under ASC 350-40. Which epics get capitalized is **your call as the EM**, because you know what the work actually is. Finance audits; they don't classify. Bad classification = restated financials = bad day for everyone. Good news: the decision is almost always obvious.

Canonical policy: [`capitalization-policy.md`](./capitalization-policy.md).

## 2. One-page decision tree

```
Start: I have a new Epic.
│
├─ Is the team still figuring out whether / how to build it?
│   (spikes, RFCs, vendor evals, feasibility work)
│        │
│        └─ YES → CapEx Eligible = TBD
│                 CapEx Stage    = Preliminary
│                 (Revisit once the team commits to build.)
│
├─ Is this net-new functionality OR a significant enhancement
│   to existing functionality?
│        │
│        ├─ YES → CapEx Eligible = Yes
│        │        CapEx Stage    = Application Development
│        │        → Assign a CapEx Project Code
│        │
│        └─ NO  → Continue ↓
│
├─ Is this a bug fix, security patch, routine maintenance,
│   dependency bump, performance tuning (no new feature),
│   or on-call / toil?
│        │
│        └─ YES → CapEx Eligible = No
│
└─ Judgment call: large refactor, vendor migration, or infra
   platform work?
        │
        └─ See §4 below. Usually expense unless new functionality
          is being delivered.
```

Clarifying questions to ask yourself:
- **"If I described this Epic to Finance, would they agree a new capability is being created?"** If you hesitate, it's probably expense.
- **"Would this Epic still make sense if the existing system already had this capability?"** If no, it's new functionality → capitalize.

## 3. Examples (SaaS context)

### Clearly capex

- **New SSO integration** (Okta, Azure AD, custom SAML) — net-new auth capability.
- **Billing engine v2** — ground-up rewrite that adds usage-based pricing the current system can't do.
- **New mobile feature: visitor scheduling** — feature that didn't exist.
- **API v2 launch** — new public API surface with new resources/endpoints (not just a version bump of existing endpoints).
- **New event bus platform** — infra that enables other teams to ship async features they couldn't ship before.
- **New property management portal** — net-new UI and workflows for a new persona.

### Clearly NOT capex

- **Rotating a dependency** (e.g., upgrading Rails, Node, a library). Maintenance.
- **On-call rotation work, bug triage, incident response.** Operational.
- **Performance tuning an existing feature** with no new user-facing capability. Maintenance.
- **Security patches / CVE remediation.** Maintenance.
- **Routine refactor** of a module with no new capability shipping as a result. Maintenance.
- **Deprecation work** (removing a feature). Not an asset being created.
- **Documentation sprints, internal tooling polish, dev experience improvements** — expense unless clearly a net-new internal platform.

### Judgment calls (document your reasoning in the Epic)

- **Large refactor that enables a new feature.** Split it: the enabling scaffolding needed to unblock the new feature can be capex when paired with the new feature Epic. Pure refactor with no feature behind it = expense. When in doubt, ask the Eng Finance partner.
- **Vendor migration** (e.g., moving from Auth0 to Cognito). Usually expense — same capability, different provider. If the migration also delivers new functionality (e.g., you pick up MFA types you didn't have), capitalize the new-functionality portion only, as its own Epic.
- **Major version upgrade of an internal framework.** Usually expense. Capitalize only if the upgrade unlocks meaningfully new capability being built on top of it in the same planning horizon.
- **Experimental / A/B-tested features.** If the experiment ships as GA, capex from the point the team committed to build. If killed before GA, expense all accumulated cost (see policy §7).

## 4. How to fill the 4 Jira fields

On the Epic, set:

| Field | When you set it | How |
|---|---|---|
| `CapEx Eligible` | At Epic creation | `Yes` / `No` / `TBD`. Default `TBD` is fine while in Preliminary. |
| `CapEx Stage` | When stage transitions (see §5) | `Preliminary`, `Application Development`, `Post-Implementation` |
| `CapEx Project Code` | At Epic creation if known, otherwise when stage → Application Development | Pull from `config/projects.yaml`. If your project isn't in the registry, open a PR to add it — follow the existing naming: `CAPEX-<FY>-<TEAM>-<SHORTNAME>` |
| `Placed in Service Date` | On production release | ISO date. Automation will nag you if you close the Epic without this set. |

If you're unsure, set `CapEx Eligible = TBD` and message the Eng Finance partner. `TBD` is safe; `Yes` or `No` without thought is not.

## 5. What to do when stage changes

Stages are real — update the field when work moves:

- **Preliminary → Application Development:** the team has committed to build (e.g., RFC approved, design doc signed off, sprint work starts). Flip `CapEx Stage` and set `CapEx Eligible = Yes` (or `No` if you've concluded it's not eligible after all).
- **Application Development → Post-Implementation:** the Epic has been placed in service. Set `Placed in Service Date`, flip `CapEx Stage`. Typically this happens as you close the Epic.
- **Killed pre-launch:** close the Epic with a resolution that makes it clear (e.g., `Won't Do`). Leave `CapEx Stage = Application Development` and `Placed in Service Date` empty. Add a comment explaining the kill. The Eng Finance partner will pick this up during the monthly review and expense the accumulated cost (policy §7).

Don't retroactively re-stage to "hide" ineligible work as eligible. Auditors look at history. Honest classification protects everyone.

## 6. Monthly 15-minute EM review checklist

Run this by **working day -3** of each month (see `finance-process.md` for full cadence).

- [ ] Open the saved JQL filter: `CapEx: Active Application Development Epics` filtered to my team.
- [ ] For each open Epic: is `CapEx Stage` still accurate this month? Still `Application Development`, or did it move to Post-Implementation?
- [ ] For each Epic that closed this month: is `Placed in Service Date` set correctly?
- [ ] For any Epic killed mid-flight this month: is it clearly marked as killed? (Comment + appropriate resolution.)
- [ ] For each open Epic with `CapEx Eligible = TBD`: has it been `TBD` for more than 30 days? If yes, make a decision now.
- [ ] Scan the list for epics that look miscategorized (e.g., a bug-fix title on a `CapEx Eligible = Yes` epic). Fix.

If anything is unclear, message the Eng Finance partner before working day -3. They'd much rather answer questions ahead of close than chase corrections after.

## 7. FAQ

**"A big feature's Epic spans two fiscal periods. What do I do?"**
Nothing special. The report captures labor by period based on Jira activity in that period. The `CapEx Stage = Application Development` setting just tells the report that period's costs are eligible. Costs get capitalized in the periods they're incurred; amortization starts at placed-in-service date.

**"Do PM and design hours count?"**
Yes, their fully-loaded cost is eligible when they're doing Application Development stage work on a capitalized Epic (policy §4). Make sure they're assigned to relevant Jira issues under the Epic or logged via the configured cost method.

**"What about contractors on my team?"**
Excluded from v1 (policy §2). Their cost stays in OpEx. V2 will revisit.

**"I fixed a bug in a feature that shipped last month. That Epic is still open. Capitalize?"**
No. Once the feature is placed in service, it's Post-Implementation. Open a new Epic for the fix with `CapEx Eligible = No` rather than piling onto the old Epic.

**"I'm not sure. Who do I ask?"**
Eng Finance partner (first stop), then VP Eng, then Controller. Most questions resolve in under 5 minutes in Slack.

