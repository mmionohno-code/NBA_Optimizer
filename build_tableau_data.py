"""
Export Tableau-ready data files.
Creates clean, flat CSVs optimized for drag-and-drop in Tableau.
Also generates a step-by-step Tableau setup guide.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import pandas as pd
import os

print("=" * 60)
print("PREPARING TABLEAU-READY DATA EXPORTS")
print("=" * 60)

output_dir = 'tableau_data'
os.makedirs(output_dir, exist_ok=True)

# ============================================================
# EXPORT 1 — PLAYER DATABASE (main data source)
# ============================================================

print("\n--- Export 1: Player Database ---")
df_all = pd.read_csv('nba_clustered.csv')

# Tableau needs clean, flat data with readable column names
cols_export = {
    'PLAYER_NAME': 'Player Name',
    'TEAM_ABBREVIATION': 'Team',
    'SEASON': 'Season',
    'ARCHETYPE': 'Archetype',
    'COMPOSITE_SCORE_NORM': 'Composite Score',
    'SALARY': 'Salary',
    'VORPD': 'Value Per Dollar (VORPD)',
    'OFF_RATING_ADJUSTED': 'Offensive Rating (Adjusted)',
    'DEF_RATING_ADJUSTED': 'Defensive Rating (Adjusted)',
    'ON_OFF_DIFF': 'ON/OFF Differential',
    'INFLUENCE_SCORE': 'Influence Score',
    'TS_PCT': 'True Shooting %',
    'BLK': 'Blocks Per Game',
    'STL': 'Steals Per Game',
    'AST_PCT_ADJUSTED': 'Assist % (Adjusted)',
    'FG3_PCT': 'Three-Point %',
    'IS_SHOOTER': 'Is Real Shooter',
}

available_cols = {k: v for k, v in cols_export.items() if k in df_all.columns}
df_tableau = df_all[list(available_cols.keys())].rename(columns=available_cols)

# Add salary in millions for easier Tableau use
df_tableau['Salary ($M)'] = (df_tableau['Salary'] / 1_000_000).round(2)

# Add rank per season
df_tableau['Rank'] = df_tableau.groupby('Season')['Composite Score'].rank(ascending=False, method='min').astype(int)

df_tableau.to_csv(f'{output_dir}/player_database.csv', index=False)
print(f"  Saved: {output_dir}/player_database.csv ({len(df_tableau)} rows)")

# ============================================================
# EXPORT 2 — OPTIMIZED ROSTERS (all 10 scenarios in one file)
# ============================================================

print("\n--- Export 2: Optimized Rosters ---")

scenario_names = {
    'A': 'Hard Cap ($136M)', 'B': 'Luxury Tax ($165M)', 'C': 'Budget ($90M)',
    'D': 'Rebuild ($136M)', 'E': 'Win-Now ($165M)', 'F': 'Defensive Identity',
    'G': 'Offensive Identity', 'H': 'Three-Point Era', 'I': 'Small Ball',
    'J': 'Value/Efficiency'
}

all_rosters = []
for key in 'ABCDEFGHIJ':
    filepath = f'optimized_roster_syn_{key}.csv'
    if os.path.exists(filepath):
        roster = pd.read_csv(filepath)
        roster['Scenario'] = key
        roster['Scenario Name'] = scenario_names.get(key, key)
        all_rosters.append(roster)

if all_rosters:
    df_rosters = pd.concat(all_rosters, ignore_index=True)

    # Clean column names for Tableau
    rename_roster = {
        'PLAYER_NAME': 'Player Name',
        'TEAM_ABBREVIATION': 'Team',
        'ARCHETYPE': 'Archetype',
        'COMPOSITE_SCORE_NORM': 'Base Score',
        'COMPOSITE_SYNERGY': 'Synergy Score',
        'NET_SYNERGY_PROFILE': 'Net Synergy Profile',
        'SALARY': 'Salary',
        'VORPD': 'VORPD',
        'AGE': 'Age',
        'BLK': 'Blocks',
        'STL': 'Steals',
    }
    available_rename = {k: v for k, v in rename_roster.items() if k in df_rosters.columns}
    df_rosters = df_rosters.rename(columns=available_rename)
    df_rosters['Salary ($M)'] = pd.to_numeric(df_rosters.get('Salary', 0), errors='coerce').fillna(0) / 1_000_000

    df_rosters.to_csv(f'{output_dir}/optimized_rosters.csv', index=False)
    print(f"  Saved: {output_dir}/optimized_rosters.csv ({len(df_rosters)} rows)")

# ============================================================
# EXPORT 3 — SYNERGY PAIRS
# ============================================================

print("\n--- Export 3: Synergy Pairs ---")

df_synergy = pd.read_csv('nba_synergy_2324.csv')
syn_rename = {
    'GROUP_NAME': 'Player Pair',
    'MIN': 'Shared Minutes',
    'DEF_SYNERGY': 'Defensive Synergy',
    'OFF_SYNERGY': 'Offensive Synergy',
    'NET_SYNERGY': 'Net Synergy',
    'W_NET_SYNERGY_SCALED': 'Scaled Net Synergy',
    'ARCHETYPE_A': 'Player A Archetype',
    'ARCHETYPE_B': 'Player B Archetype',
}
available_syn = {k: v for k, v in syn_rename.items() if k in df_synergy.columns}
df_syn_export = df_synergy.rename(columns=available_syn)
df_syn_export.to_csv(f'{output_dir}/synergy_pairs.csv', index=False)
print(f"  Saved: {output_dir}/synergy_pairs.csv ({len(df_syn_export)} rows)")

# ============================================================
# EXPORT 4 — SYNERGY PROFILES
# ============================================================

print("\n--- Export 4: Player Synergy Profiles ---")

df_profile = pd.read_csv('nba_def_synergy_profile.csv')
df_profile = df_profile.rename(columns={
    'PLAYER_NAME': 'Player Name',
    'PLAYER_ID': 'Player ID',
    'NET_SYNERGY_PROFILE': 'Net Synergy Profile',
})
df_profile.to_csv(f'{output_dir}/synergy_profiles.csv', index=False)
print(f"  Saved: {output_dir}/synergy_profiles.csv ({len(df_profile)} rows)")

# ============================================================
# TABLEAU SETUP GUIDE
# ============================================================

print("\n--- Generating Tableau Setup Guide ---")

guide = """# TABLEAU SETUP GUIDE — NBA Optimizer Dashboard
============================================================

## Step 1: Install Tableau
- Download Tableau Public (free): https://public.tableau.com/
- Or Tableau Desktop (paid, 14-day free trial)

## Step 2: Connect to Data
1. Open Tableau
2. Click "Text file" under Connect (left sidebar)
3. Navigate to the 'tableau_data' folder
4. Open 'player_database.csv' as your primary data source

## Step 3: Add Additional Data Sources (optional)
- Drag 'optimized_rosters.csv' as a second data source
- Drag 'synergy_pairs.csv' as a third
- Drag 'synergy_profiles.csv' as a fourth

## Step 4: Build These Worksheets

### WORKSHEET 1: Player Value Map (Score vs Salary)
- Drag "Salary ($M)" to Columns
- Drag "Composite Score" to Rows
- Drag "Archetype" to Color (Marks card)
- Drag "Player Name" to Detail
- Filter: Season = 2023-24
- This creates the scatter plot showing value (top-left = best value)

### WORKSHEET 2: Top 20 Rankings
- Drag "Player Name" to Rows
- Drag "Composite Score" to Columns
- Sort descending by Composite Score
- Drag "Archetype" to Color
- Filter: Season = 2023-24, Rank <= 20

### WORKSHEET 3: Archetype Breakdown
- Drag "Archetype" to Rows
- Drag "Number of Records" (or COUNT) to Columns
- Drag "Archetype" to Color
- Shows player count per archetype

### WORKSHEET 4: Salary Distribution
- Drag "Salary ($M)" to Columns (as dimension, then change to continuous)
- Right-click axis → "Show Distribution" → select histogram
- Drag "Archetype" to Color
- Shows salary distribution across archetypes

### WORKSHEET 5: Optimized Roster View
- Switch to 'optimized_rosters.csv' data source
- Drag "Scenario Name" to Filters → show filter
- Drag "Player Name" to Rows
- Drag "Synergy Score" to Columns
- Drag "Salary ($M)" to Size
- Drag "Archetype" to Color
- Now you can click different scenarios in the filter to see each roster

### WORKSHEET 6: Scenario Comparison
- Drag "Scenario Name" to Columns
- Drag SUM("Base Score") to Rows
- Add SUM("Salary") as a dual axis
- Shows score vs salary across all 10 scenarios

### WORKSHEET 7: Player Trajectory (across seasons)
- Back to 'player_database.csv'
- Drag "Season" to Columns
- Drag "Composite Score" to Rows
- Drag "Player Name" to Detail
- Filter to specific players (e.g., Jokic, Wembanyama)
- Shows how player scores changed across 3 seasons

### WORKSHEET 8: Synergy Pairs
- Switch to 'synergy_pairs.csv'
- Drag "Player Pair" to Rows
- Drag "Net Synergy" to Columns
- Sort descending
- Drag "Net Synergy" to Color (green-red diverging)
- Filter to top 25

## Step 5: Build the Dashboard
1. Click "New Dashboard" tab at bottom
2. Set size to "Automatic" or 1200x800
3. Drag worksheets from the left panel onto the dashboard canvas
4. Add filters as "Actions" so clicking one chart filters the others
5. Add a title: "NBA Roster Optimization Engine"

## Step 6: Publish (Optional)
1. File → Save to Tableau Public
2. Create a free Tableau Public account
3. Your dashboard gets a shareable URL
4. Add this URL to your resume/LinkedIn

## Data Files Reference
- player_database.csv    — 1,185 player-seasons (main data)
- optimized_rosters.csv  — 150 roster slots (10 scenarios x 15 players)
- synergy_pairs.csv      — 1,661 pairwise chemistry values
- synergy_profiles.csv   — 395 player-level synergy profiles
"""

with open(f'{output_dir}/TABLEAU_SETUP_GUIDE.md', 'w', encoding='utf-8') as f:
    f.write(guide)

print(f"  Saved: {output_dir}/TABLEAU_SETUP_GUIDE.md")

print(f"\n{'=' * 60}")
print(f"TABLEAU DATA EXPORTS COMPLETE")
print(f"{'=' * 60}")
print(f"\nFiles in '{output_dir}/' folder:")
print(f"  player_database.csv       — {len(df_tableau)} player-seasons")
print(f"  optimized_rosters.csv     — {len(df_rosters)} roster slots")
print(f"  synergy_pairs.csv         — {len(df_syn_export)} pairs")
print(f"  synergy_profiles.csv      — {len(df_profile)} profiles")
print(f"  TABLEAU_SETUP_GUIDE.md    — Step-by-step Tableau instructions")
print(f"\nNext: Open Tableau, connect to player_database.csv, and follow the guide.")
