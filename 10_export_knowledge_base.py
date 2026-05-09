"""
Option 1: Player/Scenario Knowledge Base
Exports NBA optimizer data into Obsidian Markdown notes with YAML frontmatter.
Creates linked notes for Players, Archetypes, and Scenarios.
Run from the project root: python 10_export_knowledge_base.py
"""

import pandas as pd
import os
from pathlib import Path

BASE = Path(__file__).parent
VAULT = BASE  # Obsidian vault is the project root
OUT = VAULT / "NBA_Knowledge_Base"

SCENARIO_LABELS = {
    "A": "Max Budget ($165M) - Balanced",
    "B": "Hard Cap ($136M) - Value Focus",
    "C": "Budget ($90M) - Efficiency",
    "D": "Max Budget - Defense First",
    "E": "Hard Cap - Playmaker Heavy",
    "F": "Hard Cap - 3-and-D Focus",
    "G": "Max Budget - Star + Depth",
    "H": "Budget - Young Core",
    "I": "Hard Cap - Balanced Synergy",
    "J": "Max Budget - Championship Roster",
}

ARCHETYPE_DESC = {
    "Elite Playmaker":   "High-usage primary ball-handlers who create offense. Top AST%, high COMPOSITE_SCORE.",
    "Perimeter Scorer":  "3-point specialists and spot-up shooters. High IS_SHOOTER flag, strong TS%.",
    "Defensive Wing":    "Two-way players with elite DEF_RATING. BLK + STL leaders.",
    "Stretch Big":       "Bigs with shooting range. FG3_PCT > 35%, rim presence.",
    "Paint Anchor":      "Traditional bigs. High BLK, negative PCA_X (rim-centric profile).",
    "Two-Way Guard":     "Guards who contribute on both ends. Balanced OFF/DEF rating adjustments.",
    "Role Player":       "Solid contributors who fill specific team needs without a dominant single skill.",
}


def safe_str(val, fmt=None):
    if pd.isna(val):
        return "N/A"
    if fmt == "salary":
        return f"${val:,.0f}"
    if fmt == "pct":
        return f"{val:.1%}"
    if fmt == "float2":
        return f"{val:.2f}"
    return str(val)


def make_dirs():
    for sub in ["Players", "Players/Seasons", "Archetypes", "Scenarios"]:
        (OUT / sub).mkdir(parents=True, exist_ok=True)


def export_players(df: pd.DataFrame):
    """One note per player. Most recent season drives YAML frontmatter.
    All seasons are embedded as a history table inside the note body."""
    df_sorted = df.sort_values("SEASON", ascending=False)
    latest = df_sorted.drop_duplicates(subset="PLAYER_ID", keep="first").copy()
    latest = latest.sort_values("COMPOSITE_SCORE_NORM", ascending=False)

    # Build a lookup: PLAYER_ID -> all rows sorted newest first
    all_seasons = df_sorted.groupby("PLAYER_ID")

    print(f"  Exporting {len(latest)} player notes (all seasons embedded)...")
    for _, row in latest.iterrows():
        name = row["PLAYER_NAME"]
        safe_name = name.replace("/", "-").replace(":", "")
        archetype = row["ARCHETYPE"]
        arch_link = f"[[Archetypes/{archetype}]]"

        salary_raw = row["SALARY"]
        try:
            salary_yaml = int(float(str(salary_raw).replace("$", "").replace(",", "")))
        except Exception:
            salary_yaml = 0

        composite = row["COMPOSITE_SCORE_NORM"]
        try:
            composite_val = float(str(composite).replace("%", ""))
        except Exception:
            composite_val = 0.0

        frontmatter = f"""---
player: "{name}"
team: "{safe_str(row['TEAM_ABBREVIATION'])}"
season: "{safe_str(row['SEASON'])}"
archetype: "{archetype}"
composite_score: {composite_val:.2f}
salary: {salary_yaml}
vorpd: {safe_str(row['VORPD'], 'float2')}
off_rating_adj: {safe_str(row['OFF_RATING_ADJUSTED'], 'float2')}
def_rating_adj: {safe_str(row['DEF_RATING_ADJUSTED'], 'float2')}
on_off_diff: {safe_str(row['ON_OFF_DIFF'], 'float2')}
is_shooter: {int(row['IS_SHOOTER']) if not pd.isna(row['IS_SHOOTER']) else 0}
tags: [player, {archetype.lower().replace(' ', '-').replace("'", "")}]
---
"""
        ts_pct = safe_str(row["TS_PCT"])
        fg3_pct = safe_str(row["FG3_PCT"])
        try:
            ts_display = f"{float(str(ts_pct).replace('%','')):.1%}" if "%" not in str(ts_pct) else ts_pct
        except Exception:
            ts_display = ts_pct
        try:
            fg3_display = f"{float(str(fg3_pct).replace('%','')):.1%}" if "%" not in str(fg3_pct) else fg3_pct
        except Exception:
            fg3_display = fg3_pct

        # Build season history table from all rows for this player
        pid = row["PLAYER_ID"]
        try:
            player_seasons = all_seasons.get_group(pid).sort_values("SEASON", ascending=False)
        except KeyError:
            player_seasons = df_sorted[df_sorted["PLAYER_ID"] == pid]

        seasons_count = len(player_seasons)

        def fmt_composite(v):
            try:
                return f"{float(str(v).replace('%', '')):.1f}"
            except Exception:
                return str(v)

        def fmt_salary(v):
            try:
                return f"${float(str(v).replace('$','').replace(',','')):.0f}"
            except Exception:
                return str(v)

        def fmt_float(v):
            try:
                return f"{float(v):.2f}"
            except Exception:
                return str(v)

        history_rows = "\n".join(
            f"| {r['SEASON']} | {r['TEAM_ABBREVIATION']} | {fmt_composite(r['COMPOSITE_SCORE_NORM'])} "
            f"| {fmt_salary(r['SALARY'])} | {fmt_float(r['VORPD'])} "
            f"| {fmt_float(r['OFF_RATING_ADJUSTED'])} | {fmt_float(r['DEF_RATING_ADJUSTED'])} "
            f"| {fmt_float(r['ON_OFF_DIFF'])} |"
            for _, r in player_seasons.iterrows()
        )

        # Trend indicator for composite score (newest vs oldest)
        if seasons_count > 1:
            scores = [
                float(str(r["COMPOSITE_SCORE_NORM"]).replace("%", ""))
                for _, r in player_seasons.iterrows()
            ]
            delta = scores[0] - scores[-1]
            if delta > 3:
                trend = f"Trending UP (+{delta:.1f} pts over {seasons_count} seasons)"
            elif delta < -3:
                trend = f"Trending DOWN ({delta:.1f} pts over {seasons_count} seasons)"
            else:
                trend = f"Stable ({delta:+.1f} pts over {seasons_count} seasons)"
        else:
            trend = "Single season in dataset"

        body = f"""# {name}

> **Archetype:** {arch_link} | **Team:** {safe_str(row['TEAM_ABBREVIATION'])} | **Latest Season:** {safe_str(row['SEASON'])}

## Most Recent Season Stats ({safe_str(row['SEASON'])})

| Metric | Value |
|---|---|
| Composite Score | **{composite_val:.1f}** / 100 |
| Salary | {safe_str(salary_raw, 'salary')} |
| VORPD | {safe_str(row['VORPD'], 'float2')} |
| Off Rating Adj | {safe_str(row['OFF_RATING_ADJUSTED'], 'float2')} |
| Def Rating Adj | {safe_str(row['DEF_RATING_ADJUSTED'], 'float2')} |
| On/Off Diff | {safe_str(row['ON_OFF_DIFF'], 'float2')} |
| TS% | {ts_display} |
| 3P% | {fg3_display} |
| Influence Score | {safe_str(row['INFLUENCE_SCORE'], 'float2')} |

## Season History ({seasons_count} season{"s" if seasons_count > 1 else ""})

> **Trend:** {trend}

| Season | Team | Score | Salary | VORPD | Off Rtg | Def Rtg | On/Off |
|---|---|---|---|---|---|---|---|
{history_rows}

## Profile

- **Cluster:** {safe_str(row['CLUSTER'])}
- **PCA Position:** ({safe_str(row['PCA_X'], 'float2')}, {safe_str(row['PCA_Y'], 'float2')})
- **Is Shooter:** {'Yes' if int(row['IS_SHOOTER'] if not pd.isna(row['IS_SHOOTER']) else 0) else 'No'}

## Appears In Scenarios

```dataview
TABLE scenario, COMPOSITE_SYNERGY as "Synergy Score", SALARY as "Salary"
FROM "NBA_Knowledge_Base/Scenarios"
WHERE contains(players, "{name}")
```

## Notes

_Add your scouting notes here._
"""
        path = OUT / "Players" / f"{safe_name}.md"
        path.write_text(frontmatter + body, encoding="utf-8")

    print(f"  Done: {len(latest)} player notes -> NBA_Knowledge_Base/Players/")


def export_archetypes(df: pd.DataFrame):
    """One note per archetype with aggregated stats and player list."""
    print("  Exporting archetype notes...")
    df_sorted = df.sort_values("SEASON", ascending=False)
    latest = df_sorted.drop_duplicates(subset="PLAYER_ID", keep="first")

    for archetype, group in latest.groupby("ARCHETYPE"):
        safe_arch = archetype.replace("/", "-")
        count = len(group)
        avg_score = group["COMPOSITE_SCORE_NORM"].mean()
        avg_salary = group["SALARY"].mean()
        avg_off = group["OFF_RATING_ADJUSTED"].mean()
        avg_def = group["DEF_RATING_ADJUSTED"].mean()
        avg_vorpd = group["VORPD"].mean()

        top_players = group.nlargest(10, "COMPOSITE_SCORE_NORM")[["PLAYER_NAME", "COMPOSITE_SCORE_NORM", "SALARY", "TEAM_ABBREVIATION"]]

        desc = ARCHETYPE_DESC.get(archetype, "")

        frontmatter = f"""---
archetype: "{archetype}"
player_count: {count}
avg_composite_score: {avg_score:.2f}
avg_salary: {avg_salary:.0f}
avg_off_rating_adj: {avg_off:.2f}
avg_def_rating_adj: {avg_def:.2f}
avg_vorpd: {avg_vorpd:.2f}
tags: [archetype]
---
"""
        top_rows = "\n".join(
            f"| [[Players/{r['PLAYER_NAME'].replace('/', '-').replace(':', '')}|{r['PLAYER_NAME']}]] "
            f"| {r['COMPOSITE_SCORE_NORM']:.1f} "
            f"| ${r['SALARY']:,.0f} "
            f"| {r['TEAM_ABBREVIATION']} |"
            for _, r in top_players.iterrows()
        )

        body = f"""# {archetype}

> {desc}

## Archetype Summary

| Metric | Value |
|---|---|
| Total Players | {count} |
| Avg Composite Score | {avg_score:.1f} |
| Avg Salary | ${avg_salary:,.0f} |
| Avg Off Rating Adj | {avg_off:.2f} |
| Avg Def Rating Adj | {avg_def:.2f} |
| Avg VORPD | {avg_vorpd:.2f} |

## Top 10 Players by Composite Score

| Player | Score | Salary | Team |
|---|---|---|---|
{top_rows}

## All Players (Dataview)

```dataview
TABLE composite_score, salary, team, season
FROM "NBA_Knowledge_Base/Players"
WHERE archetype = "{archetype}"
SORT composite_score DESC
```

## Synergy Notes

_How this archetype pairs with others — see [[📊 Knowledge Base Dashboard]] for cross-archetype synergy data._
"""
        path = OUT / "Archetypes" / f"{safe_arch}.md"
        path.write_text(frontmatter + body, encoding="utf-8")

    print(f"  Done: {latest['ARCHETYPE'].nunique()} archetype notes -> NBA_Knowledge_Base/Archetypes/")


def export_scenarios():
    """One note per scenario (A-J) with full roster and budget summary."""
    print("  Exporting scenario notes...")
    for letter, label in SCENARIO_LABELS.items():
        csv_path = BASE / f"optimized_roster_syn_{letter}.csv"
        if not csv_path.exists():
            print(f"    Skipping scenario {letter}: file not found")
            continue

        df = pd.read_csv(csv_path)

        def parse_money(val):
            try:
                return float(str(val).replace("$", "").replace(",", ""))
            except Exception:
                return 0.0

        df["_salary_num"] = df["SALARY"].apply(parse_money)
        total_salary = df["_salary_num"].sum()
        avg_score = df["COMPOSITE_SCORE_NORM"].apply(
            lambda v: float(str(v).replace("%", ""))
        ).mean()

        archetype_counts = df["ARCHETYPE"].value_counts().to_dict()
        arch_str = "\n".join(f"  - {a}: {n}" for a, n in archetype_counts.items())

        roster_rows = "\n".join(
            f"| [[Players/{row['PLAYER_NAME'].replace('/', '-').replace(':', '')}|{row['PLAYER_NAME']}]] "
            f"| {row['ARCHETYPE']} "
            f"| {float(str(row['COMPOSITE_SCORE_NORM']).replace('%','')):.1f} "
            f"| ${parse_money(row['SALARY']):,.0f} "
            f"| {row['TEAM_ABBREVIATION']} |"
            for _, row in df.sort_values(
                "COMPOSITE_SCORE_NORM",
                key=lambda s: s.apply(lambda v: float(str(v).replace("%", ""))),
                ascending=False
            ).iterrows()
        )

        player_list_yaml = "[" + ", ".join(f'"{r["PLAYER_NAME"]}"' for _, r in df.iterrows()) + "]"

        frontmatter = f"""---
scenario: "{letter}"
label: "{label}"
total_salary: {total_salary:.0f}
avg_composite_score: {avg_score:.2f}
roster_size: {len(df)}
tags: [scenario]
players: {player_list_yaml}
---
"""
        body = f"""# Scenario {letter}: {label}

## Budget Overview

| Metric | Value |
|---|---|
| Total Salary | ${total_salary:,.0f} |
| Roster Size | {len(df)} players |
| Avg Composite Score | {avg_score:.1f} |

## Archetype Breakdown

{arch_str}

## Full Roster

| Player | Archetype | Score | Salary | Team |
|---|---|---|---|---|
{roster_rows}

## Analysis

_Add your notes on this scenario here._

## Compare With

```dataview
TABLE label, total_salary, avg_composite_score, roster_size
FROM "NBA_Knowledge_Base/Scenarios"
SORT avg_composite_score DESC
```
"""
        path = OUT / "Scenarios" / f"Scenario {letter}.md"
        path.write_text(frontmatter + body, encoding="utf-8")

    print(f"  Done: {len(SCENARIO_LABELS)} scenario notes -> NBA_Knowledge_Base/Scenarios/")


def export_dashboard(df: pd.DataFrame):
    """Master index note with Dataview queries — the hub of the knowledge base."""
    latest = df.sort_values("SEASON", ascending=False).drop_duplicates("PLAYER_ID", keep="first")
    arch_counts = latest["ARCHETYPE"].value_counts()
    arch_table = "\n".join(f"| {a} | {n} |" for a, n in arch_counts.items())

    content = f"""---
type: dashboard
tags: [index, dashboard]
---

# 📊 NBA Knowledge Base Dashboard

> Auto-generated from project data. Navigate via the graph view or the Dataview tables below.
> **Dataview plugin required** for live queries — install it in Settings → Community Plugins.

---

## Quick Stats

| | |
|---|---|
| Total Players | {len(latest)} |
| Seasons Covered | 2021-22, 2022-23, 2023-24 |
| Optimization Scenarios | 10 (A–J) |
| Player Archetypes | {latest['ARCHETYPE'].nunique()} |

---

## Top 15 Players by Composite Score

```dataview
TABLE player, team, archetype, composite_score, salary
FROM "NBA_Knowledge_Base/Players"
SORT composite_score DESC
LIMIT 15
```

---

## Best Value Players (High Score, Low Salary)

```dataview
TABLE player, team, archetype, composite_score, salary
FROM "NBA_Knowledge_Base/Players"
WHERE salary < 15000000 AND composite_score > 60
SORT composite_score DESC
LIMIT 15
```

---

## Players by Archetype

| Archetype | Count |
|---|---|
{arch_table}

```dataview
TABLE player, composite_score, salary
FROM "NBA_Knowledge_Base/Players"
GROUP BY archetype
```

---

## All Scenarios

```dataview
TABLE label, total_salary, avg_composite_score, roster_size
FROM "NBA_Knowledge_Base/Scenarios"
SORT avg_composite_score DESC
```

---

## Archetypes Index

```dataview
TABLE avg_composite_score, avg_salary, player_count
FROM "NBA_Knowledge_Base/Archetypes"
SORT avg_composite_score DESC
```

---

## Navigation

- [[Archetypes/Elite Playmaker]] · [[Archetypes/Perimeter Scorer]] · [[Archetypes/Defensive Wing]]
- [[Archetypes/Stretch Big]] · [[Archetypes/Paint Anchor]] · [[Archetypes/Two-Way Guard]]
- [[Scenarios/Scenario A]] → [[Scenarios/Scenario J]]
"""
    path = OUT / "📊 Knowledge Base Dashboard.md"
    path.write_text(content, encoding="utf-8")
    print("  Done: Dashboard -> NBA_Knowledge_Base/ Knowledge Base Dashboard.md")


def export_season_notes(df: pd.DataFrame):
    """One note per player-season row (~1,200 notes). Each links back to the main player note."""
    print(f"  Exporting {len(df)} individual season notes...")
    for _, row in df.iterrows():
        name = row["PLAYER_NAME"]
        safe_name = name.replace("/", "-").replace(":", "")
        season = row["SEASON"]
        archetype = row["ARCHETYPE"]

        try:
            composite_val = float(str(row["COMPOSITE_SCORE_NORM"]).replace("%", ""))
        except Exception:
            composite_val = 0.0

        try:
            salary_num = int(float(str(row["SALARY"]).replace("$", "").replace(",", "")))
        except Exception:
            salary_num = 0

        def fmt(v, kind=None):
            if pd.isna(v):
                return "N/A"
            if kind == "pct":
                try:
                    return f"{float(str(v).replace('%','')):.1%}"
                except Exception:
                    return str(v)
            if kind == "f2":
                try:
                    return f"{float(v):.2f}"
                except Exception:
                    return str(v)
            return str(v)

        frontmatter = f"""---
player_season: "{name} ({season})"
player: "{name}"
season: "{season}"
team: "{fmt(row['TEAM_ABBREVIATION'])}"
archetype: "{archetype}"
composite_score: {composite_val:.2f}
salary: {salary_num}
vorpd: {fmt(row['VORPD'], 'f2')}
off_rating_adj: {fmt(row['OFF_RATING_ADJUSTED'], 'f2')}
def_rating_adj: {fmt(row['DEF_RATING_ADJUSTED'], 'f2')}
on_off_diff: {fmt(row['ON_OFF_DIFF'], 'f2')}
season_weight: {fmt(row['SEASON_WEIGHT'], 'f2')}
tags: [season-note, {archetype.lower().replace(' ', '-').replace("'", "")}]
---
"""
        body = f"""# {name} — {season}

> Part of [[Players/{safe_name}]] | Archetype: [[Archetypes/{archetype}]]

| Metric | Value |
|---|---|
| Season | {season} |
| Team | {fmt(row['TEAM_ABBREVIATION'])} |
| Composite Score | **{composite_val:.1f}** / 100 |
| Salary | ${salary_num:,} |
| VORPD | {fmt(row['VORPD'], 'f2')} |
| Off Rating Adj | {fmt(row['OFF_RATING_ADJUSTED'], 'f2')} |
| Def Rating Adj | {fmt(row['DEF_RATING_ADJUSTED'], 'f2')} |
| On/Off Diff | {fmt(row['ON_OFF_DIFF'], 'f2')} |
| TS% | {fmt(row['TS_PCT'], 'pct')} |
| 3P% | {fmt(row['FG3_PCT'], 'pct')} |
| Influence Score | {fmt(row['INFLUENCE_SCORE'], 'f2')} |
| Season Weight | {fmt(row['SEASON_WEIGHT'], 'f2')} |

_Navigate back to the full player profile: [[Players/{safe_name}]]_
"""
        filename = f"{safe_name} ({season}).md"
        path = OUT / "Players" / "Seasons" / filename
        path.write_text(frontmatter + body, encoding="utf-8")

    print(f"  Done: {len(df)} season notes -> NBA_Knowledge_Base/Players/Seasons/")


def main():
    print("=== Option 1: Exporting Player/Scenario Knowledge Base ===")
    make_dirs()
    df = pd.read_csv(BASE / "nba_clustered.csv")
    export_players(df)
    export_season_notes(df)
    export_archetypes(df)
    export_scenarios()
    export_dashboard(df)
    print(f"\nAll done! Open Obsidian and browse NBA_Knowledge_Base/")
    print("Tip: Install the Dataview plugin to activate all live-query tables.")


if __name__ == "__main__":
    main()
