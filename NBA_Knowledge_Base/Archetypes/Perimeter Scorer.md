---
archetype: "Perimeter Scorer"
player_count: 87
avg_composite_score: 47.06
avg_salary: 12757248
avg_off_rating_adj: 2.69
avg_def_rating_adj: 0.12
avg_vorpd: 4.27
tags: [archetype]
---
# Perimeter Scorer

> 3-point specialists and spot-up shooters. High IS_SHOOTER flag, strong TS%.

## Archetype Summary

| Metric | Value |
|---|---|
| Total Players | 87 |
| Avg Composite Score | 47.1 |
| Avg Salary | $12,757,248 |
| Avg Off Rating Adj | 2.69 |
| Avg Def Rating Adj | 0.12 |
| Avg VORPD | 4.27 |

## Top 10 Players by Composite Score

| Player | Score | Salary | Team |
|---|---|---|---|
| [[Players/De'Anthony Melton|De'Anthony Melton]] | 69.2 | $2,710,900 | PHI |
| [[Players/OG Anunoby|OG Anunoby]] | 68.9 | $34,816,707 | NYK |
| [[Players/Bogdan Bogdanović|Bogdan Bogdanović]] | 64.2 | $14,095,988 | ATL |
| [[Players/Kris Dunn|Kris Dunn]] | 62.5 | $4,774,686 | UTA |
| [[Players/Kentavious Caldwell-Pope|Kentavious Caldwell-Pope]] | 61.8 | $19,024,744 | DEN |
| [[Players/Isaiah Hartenstein|Isaiah Hartenstein]] | 59.6 | $25,077,131 | NYK |
| [[Players/Alex Caruso|Alex Caruso]] | 59.4 | $15,927,938 | CHI |
| [[Players/Immanuel Quickley|Immanuel Quickley]] | 58.4 | $28,596,729 | TOR |
| [[Players/Lauri Markkanen|Lauri Markkanen]] | 58.3 | $40,822,138 | UTA |
| [[Players/Draymond Green|Draymond Green]] | 57.6 | $22,783,108 | GSW |

## All Players (Dataview)

```dataview
TABLE composite_score, salary, team, season
FROM "NBA_Knowledge_Base/Players"
WHERE archetype = "Perimeter Scorer"
SORT composite_score DESC
```

## Synergy Notes

_How this archetype pairs with others — see [[📊 Knowledge Base Dashboard]] for cross-archetype synergy data._
