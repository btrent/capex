# Jira Setup Guide

**Audience:** Jira Cloud admin
**Goal:** Configure the custom fields, screens, permissions, and automation required to track software capitalization on Epics.
**Time estimate:** 30-45 minutes.

> Versioned guide. Propose changes via PR.

---

## 1. Custom fields to create

All four fields live on the **Epic** issue type.

| Field name | Type | Options / format | Default | Required? |
|---|---|---|---|---|
| `CapEx Eligible` | Select List (single choice) | `Yes`, `No`, `TBD` | `TBD` | No (but enforced via automation — see §5) |
| `CapEx Stage` | Select List (single choice) | `Preliminary`, `Application Development`, `Post-Implementation` | none | No |
| `CapEx Project Code` | Short text (recommend: Select List with controlled vocab once registry stabilizes) | e.g. `CAPEX-2026-PLATFORM-SSO` | none | No |
| `Placed in Service Date` | Date picker | ISO date | none | No |

**Why short text for Project Code in v1:** avoids a chicken-and-egg problem with the YAML registry at `config/projects.yaml`. Once the registry is stable (~2 close cycles), migrate to a Select List sourced from that registry to eliminate typos.

### Creation steps (Jira Cloud UI)

1. **Settings → Issues → Custom fields → Create custom field.**
2. For each field above, choose the type, give it the exact name shown (the name is what JQL and the reporting script look up), and save.
3. Set options / default value as specified.

## 2. Field context (scope)

**Recommendation: apply all four fields to _all projects_, not just engineering projects.**

Rationale:
- Companies that acquire teams landing in separate Jira projects benefit from global application — no config changes needed after each acquisition.
- Non-eng projects will simply leave fields at `TBD` / blank; no harm.
- If noise is a concern later, we can scope down. Easier to remove than add.

To apply globally: in the field's context configuration, choose **"Global context (all issues)"**.

## 3. Screen configuration

Add all four fields to the following Epic screens. In Jira Cloud: **Issues → Screens → [screen name] → Add field**.

- **Epic — Create screen:** all four fields visible. `Placed in Service Date` optional at creation; typically set later.
- **Epic — View / Edit screen:** all four fields visible and editable.
- **Epic — Default screen** (if used by your scheme): all four fields.

If the project uses a Screen Scheme that differs per project, apply the change to the schemes used by your engineering projects at minimum. Global application is fine.

## 4. Permissions

Default Jira permissions are typically sufficient. Recommended posture:

- **Edit these fields:** Epic reporter, Epic assignee, project admins, Jira admins.
- **Read:** everyone with project access (default).

If the instance uses field-level security, add the four fields to an "Engineering Management" permission group. Don't overthink it for v1 — most Jira users are already constrained by project permissions.

## 5. Automation rule: nag for missing Placed-in-Service date

Using **Jira Automation** (Project settings → Automation, or Global automation).

**Rule name:** `CapEx: prompt for Placed in Service date on Epic Done`

**Trigger:** Issue transitioned
 - From status: any
 - To status: `Done` (or whatever your "Done" category status is)
 - Issue type: Epic

**Conditions (all must match):**
 - `CapEx Eligible` = `Yes`
 - `Placed in Service Date` is empty

**Action:** Create sub-task (or assign a task to the reporter)
 - Summary: `Set Placed in Service Date on {{issue.key}}`
 - Assignee: `{{issue.reporter}}`
 - Description: `This Epic is marked CapEx Eligible = Yes but has no Placed in Service Date. Please set it to the production release date that delivered the intended functionality. See docs/capitalization-policy.md §6.`

Recommended second action: **Slack message** to `#eng-capex-ops` (or equivalent) with the Epic key and reporter tag so the Eng Finance partner has a visible backlog.

## 6. Reporting JQL

The reporting script (`scripts/generate_report.py`, owned by the other agent) uses JQL to pull Epics. The canonical query for "what was capitalized in period X":

```
issuetype = Epic
AND "CapEx Eligible" = Yes
AND "CapEx Stage" = "Application Development"
AND resolved >= "2026-04-01" AND resolved <= "2026-04-30"
```

For real-time sanity-checking in the Jira UI:

```
issuetype = Epic AND "CapEx Eligible" = Yes AND "CapEx Stage" = "Application Development"
```

Save this as a shared filter named `CapEx: Active Application Development Epics` — link it from the README.

## 7. Finding custom field IDs

The reporting script references fields by their numeric ID (e.g. `customfield_10234`), not display name. Field names can be changed; IDs are stable.

### Via REST API (recommended)

```bash
# Replace <YOUR-SITE> with e.g. yourcompany.atlassian.net
# Replace <EMAIL> and <API-TOKEN> with your Atlassian credentials
# Create API token at id.atlassian.com -> Security -> API tokens

curl -s -u "<EMAIL>:<API-TOKEN>" \
  -H "Accept: application/json" \
  "https://<YOUR-SITE>/rest/api/3/field" \
  | jq '.[] | select(.name | test("CapEx|Placed in Service")) | {id, name}'
```

Expected output:

```json
{"id": "customfield_10201", "name": "CapEx Eligible"}
{"id": "customfield_10202", "name": "CapEx Stage"}
{"id": "customfield_10203", "name": "CapEx Project Code"}
{"id": "customfield_10204", "name": "Placed in Service Date"}
```

Record these IDs in the report script's config — the exact IDs will differ in your instance.

### Via UI (fallback)

Admin → Issues → Custom fields → click the `...` menu next to a field → `Edit details`. The URL contains `customFieldId=10201` — that's the numeric ID.

## 8. Smoke test

After setup, verify:

1. Create a test Epic in an engineering project.
2. Confirm all four fields appear on Create, View, and Edit screens.
3. Set `CapEx Eligible = Yes`, leave `Placed in Service Date` empty, transition to Done.
4. Within ~1 minute, confirm the automation rule fires and a follow-up task is assigned to the reporter.
5. Run the JQL in §6 — the test Epic should appear.
6. Delete the test Epic.

## 9. Handoff

Once configured, ping the Eng Finance partner with:
- The custom field IDs (§7 output).
- The Jira instance base URL.
- A confirmation that the automation rule is enabled.

They will finish wiring the report script.

