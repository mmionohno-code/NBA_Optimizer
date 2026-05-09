"""
Adds two new note layers to the Obsidian vault:
  - Teams/{TEAM}.md  (30 NBA franchise notes, each linking to all its players)
  - Salary_Tiers/{TIER}.md  (5 contract bracket notes, each linking to players in range)

Both layers cross-link to existing Players/{name}.md notes, adding
hundreds of new edges to the graph for richer visual density.

Run from project root: python 14_add_layers.py
"""

from pathlib import Path
import pandas as pd

BASE = Path(__file__).parent
VAULT = BASE / "NBA_Knowledge_Base"
TEAMS_DIR = VAULT / "Teams"
TIERS_DIR = VAULT / "Salary_Tiers"

TEAM_NAMES = {
    "ATL": "Atlanta Hawks", "BOS": "Boston Celtics", "BKN": "Brooklyn Nets",
    "CHA": "Charlotte Hornets", "CHI": "Chicago Bulls", "CLE": "Cleveland Cavaliers",
    "DAL": "Dallas Mavericks", "DEN": "Denver Nuggets", "DET": "Detroit Pistons",
    "GSW": "Golden State Warriors", "HOU": "Houston Rockets", "IND": "Indiana Pacers",
    "LAC": "LA Clippers", "LAL": "Los Angeles Lakers", "MEM": "Memphis Grizzlies",
    "MIA": "Miami Heat", "MIL": "Milwaukee Bucks", "MIN": "Minnesota Timberwolves",
    "NOP": "New Orleans Pelicans", "NYK": "New York Knicks", "OKC": "Oklahoma City Thunder",
    "ORL": "Orlando Magic", "PHI": "Philadelphia 76ers", "PHX": "Phoenix Suns",
    "POR": "Portland Trail Blazers", "SAC": "Sacramento Kings", "SAS": "San Antonio Spurs",
    "TOR": "Toronto Raptors", "UTA": "Utah Jazz", "WAS": "Washington Wizards",
}

SALARY_TIERS = [
    ("Supermax",   40_000_000, float("inf"), "$40M+ — supermax / franchise tier"),
    ("Max",        30_000_000,  40_000_000,  "$30M-$40M — max contract tier"),
    ("High",       20_000_000,  30_000_000,  "$20M-$30M — high-end starter tier"),
    ("Mid",        10_000_000,  20_000_000,  "$10M-$20M — mid-level / quality starter"),
    ("Role",                0,  10_000_000,  "<$10M — role player / minimum"),
]


def safe(name: str) -> str:
    return name.replace("/", "-").replace("\\", "-").replace(":", "")


def load_players() -> pd.DataFrame:
    df = pd.read_csv(BASE / "nba_complete_master.csv")
    df = df.dropna(subset=["PLAYER_NAME", "TEAM_ABBREVIATION"])
    return df


def write_team_notes(df: pd.DataFrame) -> int:
    TEAMS_DIR.mkdir(parents=True, exist_ok=True)
    written = 0
    for abbr, name in TEAM_NAMES.items():
        team_df = df[df["TEAM_ABBREVIATION"] == abbr]
        players = sorted(team_df["PLAYER_NAME"].unique())
        if not len(players):
            continue

        avg_salary = team_df["SALARY"].dropna().mean() if "SALARY" in team_df else 0
        total_salary = team_df["SALARY"].dropna().sum() if "SALARY" in team_df else 0

        lines = [
            "---",
            "type: team",
            f'abbr: "{abbr}"',
            f'name: "{name}"',
            "tags: [team, franchise]",
            "---",
            "",
            f"# {name} ({abbr})",
            "",
            f"**Players in dataset:** {len(players)}",
            f"**Total payroll (sum across rows):** ${total_salary:,.0f}",
            f"**Avg salary:** ${avg_salary:,.0f}" if avg_salary else "",
            "",
            "## Roster",
            "",
        ]
        for p in players:
            lines.append(f"- [[Players/{safe(p)}]]")

        (TEAMS_DIR / f"{abbr} - {name}.md").write_text(
            "\n".join(lines), encoding="utf-8"
        )
        written += 1
    return written


def write_salary_tier_notes(df: pd.DataFrame) -> int:
    TIERS_DIR.mkdir(parents=True, exist_ok=True)
    if "SALARY" not in df.columns:
        print("  No SALARY column; skipping tier notes.")
        return 0

    df = df.dropna(subset=["SALARY"])
    df = df.sort_values("SALARY", ascending=False).drop_duplicates(
        subset="PLAYER_NAME", keep="first"
    )

    written = 0
    for tier_name, lo, hi, blurb in SALARY_TIERS:
        tier_df = df[(df["SALARY"] >= lo) & (df["SALARY"] < hi)]
        players = sorted(tier_df["PLAYER_NAME"].unique())
        if not len(players):
            continue

        lines = [
            "---",
            "type: salary-tier",
            f'tier: "{tier_name}"',
            "tags: [salary, contract]",
            "---",
            "",
            f"# {tier_name} Tier",
            "",
            f"_{blurb}_",
            "",
            f"**Players in tier:** {len(players)}",
            "",
            "## Members",
            "",
        ]
        for p in players:
            sal = tier_df.loc[tier_df["PLAYER_NAME"] == p, "SALARY"].iloc[0]
            lines.append(f"- [[Players/{safe(p)}]] — ${sal:,.0f}")

        (TIERS_DIR / f"{tier_name}.md").write_text(
            "\n".join(lines), encoding="utf-8"
        )
        written += 1
    return written


def main():
    print("=== Adding Teams + Salary Tier layers ===")
    df = load_players()
    print(f"  Loaded {len(df)} player-rows from master CSV")

    n_teams = write_team_notes(df)
    print(f"  Wrote {n_teams} Team notes -> NBA_Knowledge_Base/Teams/")

    n_tiers = write_salary_tier_notes(df)
    print(f"  Wrote {n_tiers} Salary Tier notes -> NBA_Knowledge_Base/Salary_Tiers/")

    print("\nDone. Reload Obsidian and check the graph.")


if __name__ == "__main__":
    main()
