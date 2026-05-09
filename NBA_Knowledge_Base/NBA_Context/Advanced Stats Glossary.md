---
type: nba-context
tags: [nba, stats, glossary]
---

# Advanced Stats Glossary

Quick reference for every stat used in the optimizer.

## Ratings (Per 100 Possessions)

**OFF_RATING** — Points scored per 100 possessions when a player is on the court.
Higher = better offense. League average ~114.

**DEF_RATING** — Points allowed per 100 possessions when a player is on the court.
Lower = better defense. League average ~114.

**NET_RATING** — OFF_RATING minus DEF_RATING. The most concise single-number summary.
Positive = team outscores opponents when this player plays.

**ON_OFF_DIFF** — How much better/worse the team's net rating is with this player
on vs off the court. Isolates the player's marginal impact.

## Efficiency Stats

**TS% (True Shooting %)** — Points per shooting attempt, accounting for free throws
and 3-pointers. Better than FG% because it values efficiency over volume.
`TS% = PTS / (2 × (FGA + 0.44 × FTA))`

**FG3_PCT** — 3-point field goal percentage. Important for IS_SHOOTER classification.

## Usage & Creation

**USG_PCT (Usage Rate)** — Estimated % of team possessions used by player while on court.
High USG% = primary ball handler / shot creator. Low = off-ball role.

**AST_PCT** — % of teammate field goals a player assisted while on court.
High = playmaker / passer.

## Defense

**BLK (Blocks per game)** — Shot blocking. Indicator of rim protection.

**STL (Steals per game)** — Passing lane disruption. Indicator of active defense / anticipation.

## Composite / Value

**COMPOSITE_SCORE_NORM** — This project's 0-100 player quality score. PCA-weighted
combination of all above stats with recency weighting.

**VORPD** — Value Over Replacement Per Dollar. See [[Methodology/VORPD Explained]].

**INFLUENCE_SCORE** — Custom metric capturing a player's impact beyond their own stats.
Incorporates how teammates perform differently around them.

**NET_SYNERGY_PROFILE** — Player's average synergy with teammates based on 2-man lineup data.
See [[Methodology/Synergy Modeling]].

## Related Notes
- [[Methodology/Feature Engineering]]
- [[NBA_Context/Salary Cap Rules]]
- [[NBA_Context/Lineup Analysis Basics]]
