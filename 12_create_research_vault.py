"""
Option 3: Research & Decision Log Vault
Creates Obsidian template notes and sample pre-filled entries for tracking
model decisions, scenario hypotheses, player scouts, and weekly reviews.
Run from the project root: python 12_create_research_vault.py
"""

from pathlib import Path
from datetime import date

BASE = Path(__file__).parent
VAULT = BASE
OUT = VAULT / "Research_Log"
TODAY = date.today().isoformat()

# ── Templates ──────────────────────────────────────────────────────────────

TEMPLATE_DECISION = """\
---
type: decision
date: {{date}}
status: "proposed"
area: "{{area}}"
tags: [decision, {{area}}]
---

# Decision: {{title}}

**Date:** {{date}}
**Area:** {{area}} _(modeling / optimization / data / reporting)_
**Status:** Proposed → Accepted / Rejected / Deferred

---

## Context

_What situation or problem prompted this decision?_

## Options Considered

1. **Option A** — description, trade-offs
2. **Option B** — description, trade-offs
3. **Option C** — description, trade-offs

## Decision

_What was chosen and why._

## Consequences

- **Positive:** ...
- **Negative / Risk:** ...

## Outcome Measurement

_How will we know if this decision was correct? What metric or result would validate it?_

## Related Notes

- [[Research Index]]
"""

TEMPLATE_SCENARIO = """\
---
type: scenario-analysis
date: {{date}}
scenario: "{{letter}}"
tags: [scenario, analysis]
---

# Scenario {{letter}} Analysis

**Date:** {{date}}
**Scenario File:** `optimized_roster_syn_{{letter}}.csv`

> Link to Obsidian note: [[Scenarios/Scenario {{letter}}]]

---

## Hypothesis

_What did you expect from this scenario setup? What strategic goal does it optimize for?_

## Observations

### Roster Composition
_Describe the archetype mix. Any surprises?_

### Salary Efficiency
_Is the cap used efficiently? Any obvious overpays/underpays?_

### Synergy
_Does the roster have natural synergy pairs? Gaps?_

## Strengths

- ...

## Weaknesses / Concerns

- ...

## Compared to Other Scenarios

| Scenario | Advantage of This One |
|---|---|
| vs A | ... |
| vs B | ... |

## Recommendation

_Keep / Modify / Drop this scenario? What constraint changes would improve it?_
"""

TEMPLATE_SCOUT = """\
---
type: player-scout
date: {{date}}
player: "{{player_name}}"
team: "{{team}}"
tags: [scout, player]
---

# Scout Note: {{player_name}}

**Date:** {{date}}
**Team:** {{team}}
**Obsidian Profile:** [[Players/{{player_name}}]]

---

## Why Scouting This Player

_What caught your attention? Trade rumor, breakout stats, contract situation?_

## Statistical Impression

_Go beyond the model. What do the stats suggest the model might be missing?_

## Eye Test / Context

_Playing style, role on current team, fit issues, injury history, age curve._

## Contract Situation

- **Current Salary:** $
- **Contract Status:** _(expiring / extension eligible / rookie deal)_
- **Value Assessment:** Overpaid / Fair / Underpaid

## Fit with Our Model Scenarios

_Does this player slot well into any of the 10 scenarios? Which archetype best captures them?_

## Decision

- [ ] Add to watch list
- [ ] Flag for scenario re-run with this player included
- [ ] No action needed
"""

TEMPLATE_WEEKLY = """\
---
type: weekly-review
date: {{date}}
week: "{{week}}"
tags: [weekly, review]
---

# Weekly Review — {{week}}

**Date:** {{date}}

---

## What I Worked On

- [ ] ...
- [ ] ...
- [ ] ...

## Key Findings This Week

_What did the data tell you that surprised you?_

## Model / Pipeline Changes

_Any parameters tuned, scripts modified, or decisions made?_
_Link to decision notes:_

## Open Questions

1. ...
2. ...

## Next Week

- [ ] ...
- [ ] ...

## Metrics Snapshot

| Metric | Value | Change |
|---|---|---|
| Best scenario avg score | | |
| Lowest salary scenario | | |
| Players analyzed | | |
"""

# ── Pre-filled sample notes ────────────────────────────────────────────────

SAMPLE_DECISION_LAMBDA = f"""\
---
type: decision
date: {TODAY}
status: "accepted"
area: "modeling"
tags: [decision, modeling, synergy]
---

# Decision: Synergy Weight (λ = 0.05)

**Date:** {TODAY}
**Area:** Modeling
**Status:** Accepted

---

## Context

After computing NET_SYNERGY_PROFILE scores in step 06, needed to decide how heavily
synergy should influence the optimizer's objective function vs raw COMPOSITE_SCORE_NORM.

## Options Considered

1. **λ = 0.0** — Pure composite score, ignore synergy entirely
2. **λ = 0.05** — Synergy adds up to ~5% uplift (chosen)
3. **λ = 0.20** — Heavy synergy weighting, risk of dropping high-composite players

## Decision

**λ = 0.05** — Synergy acts as a tiebreaker between similarly-scored players.
At this level, a player with a 91.0 composite + top synergy profile (~+0.9) can
edge out a 91.4 composite player with negative synergy (-0.8), but a clearly
superior player is never bumped by a mediocre one.

## Consequences

- **Positive:** Rosters feel more "coherent" archetypally. Fewer jarring pair conflicts.
- **Negative / Risk:** Synergy data is sparse (50-min threshold). Could amplify noise.

## Outcome Measurement

Compare scenario avg scores with λ=0.0 vs λ=0.05. If avg score drops >1.5 points
while archetype diversity improves, consider reducing λ.

## Related Notes

- [[05_compute_synergy]]
- [[07_optimizer_synergy]]
- [[Research Index]]
"""

SAMPLE_SCENARIO_A = f"""\
---
type: scenario-analysis
date: {TODAY}
scenario: "A"
tags: [scenario, analysis]
---

# Scenario A Analysis — Max Budget Balanced

**Date:** {TODAY}
**Scenario File:** `optimized_roster_syn_A.csv`

> [[Scenarios/Scenario A]]

---

## Hypothesis

Scenario A uses the full $165M luxury tax budget with no strong archetype constraints.
Expected to produce the highest-composite roster overall — essentially the "dream team"
if money were no object. Should reveal the market's top 15 players by composite score.

## Observations

### Roster Composition
- Heavy on Elite Playmakers (3-4) and Perimeter Scorers — as expected at max budget.
- SGA + LaMelo appear together, creating a dual-creator situation that could cause ball-sharing tension IRL.
- Defensive Wings are present but not dominant — model optimizes offensively at max spend.

### Salary Efficiency
- Total spend approaches $160M+. Very little cap space left — no room for in-season moves.
- Several players on max extensions relative to their composite score.

### Synergy
- Strong offensive synergy among playmakers. Defensive pairing is weakest area.

## Strengths

- Highest average composite score of all scenarios
- Star power is undeniable on paper

## Weaknesses / Concerns

- Real NBA teams can't simply sign anyone — no/trades/buyouts modeled
- Roster is offense-centric; could struggle vs elite defenses

## Recommendation

Keep as the "ceiling" benchmark. Use Scenario B/C for realistic planning. Flag the
defensive gap as a constraint to tighten in future optimization runs.
"""

SAMPLE_SCOUT_SGA = f"""\
---
type: player-scout
date: {TODAY}
player: "Shai Gilgeous-Alexander"
team: "OKC"
tags: [scout, player, elite-playmaker]
---

# Scout Note: Shai Gilgeous-Alexander

**Date:** {TODAY}
**Team:** OKC Thunder
**Obsidian Profile:** [[Players/Shai Gilgeous-Alexander]]

---

## Why Scouting This Player

Top composite score in the model (91.39). Appears in every high-budget scenario.
Worth understanding what drives his dominance in the model to validate its outputs.

## Statistical Impression

- Elite OFF_RATING_ADJ (+5.92) — one of the best in the dataset
- Strong ON_OFF_DIFF (+8.32) — team is dramatically better with him on court
- Reasonable DEF_RATING_ADJ (+0.91) — not a defensive anchor, but solid
- Low 3P% relative to Perimeter Scorers but high TS% (63%) — midrange efficiency outlier

## Eye Test / Context

The model correctly identifies him as an elite player. His midrange game is not captured
well by IS_SHOOTER (0) but he's highly efficient regardless. The model may
actually *underrate* him slightly by not rewarding shot creation vs volume shooting.

## Contract Situation

- **Current Salary:** $33,729,226
- **Contract Status:** Supermax extension kicks in 2024-25
- **Value Assessment:** Fair — possibly underpaid at this level given MVP trajectory

## Fit with Our Model Scenarios

Appears in Scenario A, G, J (max budget). Not affordable in Scenario C ($90M) or H (budget).
Correctly modeled — he's a "max player or bust" acquisition.

## Decision

- [x] Flag for scenario re-run with this player included
- Model behavior validated. SGA is a true ceiling player.
"""

INDEX_NOTE = f"""\
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
"""


def main():
    print("=== Option 3: Creating Research & Decision Log Vault ===")

    dirs = [
        OUT / "Templates",
        OUT / "Decisions",
        OUT / "Scenarios",
        OUT / "Scouts",
        OUT / "Weekly",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    # Write templates
    templates = {
        "Templates/Decision Log Template.md": TEMPLATE_DECISION,
        "Templates/Scenario Analysis Template.md": TEMPLATE_SCENARIO,
        "Templates/Player Scout Template.md": TEMPLATE_SCOUT,
        "Templates/Weekly Review Template.md": TEMPLATE_WEEKLY,
    }
    for rel, content in templates.items():
        path = OUT / rel
        path.write_text(content, encoding="utf-8")
        print(f"  Template: {path.name}")

    # Write sample pre-filled notes
    samples = {
        "Decisions/Lambda Weight Decision.md": SAMPLE_DECISION_LAMBDA,
        "Scenarios/Scenario A Analysis.md": SAMPLE_SCENARIO_A,
        "Scouts/Shai Gilgeous-Alexander Scout.md": SAMPLE_SCOUT_SGA,
        "📓 Research Index.md": INDEX_NOTE,
    }
    for rel, content in samples.items():
        path = OUT / rel
        path.write_text(content, encoding="utf-8")
        print(f"  Sample:   {path.name}")

    print(f"\nAll done! Open Obsidian and browse Research_Log/")
    print("Templates are in Research_Log/Templates/ — duplicate and fill in for new entries.")


if __name__ == "__main__":
    main()
