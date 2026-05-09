---
type: index
tags: [index, research]
---

# 📓 NBA Optimizer — Research Log

> Personal research notes, model decisions, and scouting observations.
> Use the templates in `Research_Log/Templates/` to create new entries.

---

## Quick Links

- [[🏗️ Pipeline Overview]] — Full pipeline documentation
- [[📊 Knowledge Base Dashboard]] — Player/scenario data explorer

---

## How to Use This Vault

| Note Type | Template | Purpose |
|---|---|---|
| Model Decision | [[Templates/Decision Log Template]] | Record why a parameter/approach was chosen |
| Scenario Analysis | [[Templates/Scenario Analysis Template]] | Deep-dive on a specific roster scenario |
| Player Scout | [[Templates/Player Scout Template]] | Notes on an individual player |
| Weekly Review | [[Templates/Weekly Review Template]] | Track weekly progress |

---

## Recent Decisions

```dataview
TABLE date, area, status
FROM "Research_Log/Decisions"
SORT date DESC
LIMIT 10
```

---

## Open Scenarios

```dataview
TABLE date, scenario
FROM "Research_Log/Scenarios"
SORT date DESC
```

---

## All Scout Notes

```dataview
TABLE date, player, team
FROM "Research_Log/Scouts"
SORT date DESC
```

---

## Entries

### Decisions
- [[Decisions/Lambda Weight Decision]]

### Scenario Analyses
- [[Scenarios/Scenario A Analysis]]

### Player Scouts
- [[Scouts/Shai Gilgeous-Alexander Scout]]
