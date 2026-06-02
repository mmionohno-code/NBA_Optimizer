---
archetype: "Perimeter Scorer"
player_count: 81
avg_composite_score: 39.97
avg_salary: 13783393
avg_off_rating_adj: 2.10
avg_def_rating_adj: 0.17
avg_vorpd: 3.50
tags: [archetype]
---
# Perimeter Scorer

> 3-point specialists and spot-up shooters. High IS_SHOOTER flag, strong TS%.

## Archetype Summary

| Metric | Value |
|---|---|
| Total Players | 81 |
| Avg Composite Score | 40.0 |
| Avg Salary | $13,783,393 |
| Avg Off Rating Adj | 2.10 |
| Avg Def Rating Adj | 0.17 |
| Avg VORPD | 3.50 |

## Top 10 Players by Composite Score

| Player | Score | Salary | Team |
|---|---|---|---|
| [[Players/Jusuf Nurkić|Jusuf Nurkić]] | 66.8 | $17,048,050 | PHX |
| [[Players/De'Anthony Melton|De'Anthony Melton]] | 61.9 | $2,710,900 | PHI |
| [[Players/OG Anunoby|OG Anunoby]] | 61.8 | $34,816,707 | NYK |
| [[Players/Bogdan Bogdanović|Bogdan Bogdanović]] | 58.2 | $14,095,988 | ATL |
| [[Players/Lonzo Ball|Lonzo Ball]] | 57.0 | $7,271,892 | CHI |
| [[Players/Kentavious Caldwell-Pope|Kentavious Caldwell-Pope]] | 55.4 | $19,024,744 | DEN |
| [[Players/Kris Dunn|Kris Dunn]] | 54.5 | $4,774,686 | UTA |
| [[Players/Isaiah Hartenstein|Isaiah Hartenstein]] | 52.9 | $25,077,131 | NYK |
| [[Players/D'Angelo Russell|D'Angelo Russell]] | 51.8 | $5,002,228 | LAL |
| [[Players/Immanuel Quickley|Immanuel Quickley]] | 50.5 | $28,596,729 | TOR |

## All Players (Dataview)

```dataview
TABLE composite_score, salary, team, season
FROM "NBA_Knowledge_Base/Players"
WHERE archetype = "Perimeter Scorer"
SORT composite_score DESC
```

## Synergy Notes

_How this archetype pairs with others — see [[📊 Knowledge Base Dashboard]] for cross-archetype synergy data._
