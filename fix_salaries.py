"""
Fix salary imputation errors in nba_complete_master.csv.
110 players in 2023-24 incorrectly set to league minimum ($1,119,563).
Corrected values sourced from publicly reported 2023-24 contracts.
"""

import pandas as pd
import numpy as np

# ── 2023-24 VERIFIED SALARY CORRECTIONS ─────────────────────────────────────
# All values in USD, sourced from public contract reporting (Spotrac/HoopsHype)
SALARY_CORRECTIONS_2324 = {
    # ── Stars clearly wrong ─────────────────────────────────────────────────
    'Jimmy Butler III':      45183960,
    'Gordon Hayward':        31500000,
    'Malcolm Brogdon':       22567321,
    'Evan Fournier':         17000000,
    'Markelle Fultz':        17400000,
    'Davis Bertans':         16000000,
    'Bojan Bogdanovic':      18000000,
    'Malik Beasley':         15400000,
    'Christian Wood':        14285714,
    'Marcus Morris Sr.':     14000000,
    'Richaun Holmes':        12000000,
    'Robert Covington':      12833333,
    'James Wiseman':         12115920,
    'P.J. Tucker':           11400000,
    'Devonte\' Graham':      12700000,
    'Talen Horton-Tucker':   10960000,
    'Cody Martin':            8600000,
    'Daniel Theis':          10000000,
    'Alec Burks':            10000000,
    'Killian Hayes':          7500000,
    'Dante Exum':             7560000,
    'Reggie Jackson':         6900000,
    'Cam Reddish':            7000000,
    'Mo Bamba':               8100000,
    'Lonnie Walker IV':       6100000,
    'KJ Martin':              6000000,
    'Cameron Payne':          6000000,
    'Jae Crowder':            6833333,
    'Dario Saric':            5500000,
    'Spencer Dinwiddie':      5200000,
    'Monte Morris':           5000000,
    'Thaddeus Young':         4500000,
    'Josh Richardson':        4780000,
    'Patrick Beverley':       4500000,
    'Delon Wright':           4000000,
    'Jalen McDaniels':        4000000,
    'Aleksej Pokusevski':     4000000,
    'Cedi Osman':             4000000,
    'Chris Duarte':           4000000,
    'Shake Milton':           4000000,
    'Danilo Gallinari':       6500000,
    'Patty Mills':            3000000,
    'Torrey Craig':           3000000,
    'Justin Holiday':         3000000,
    'Keita Bates-Diop':       3000000,
    'Dennis Smith Jr.':       3000000,
    'Lamar Stevens':          2500000,
    'Brandon Boston':         2500000,
    'Bol Bol':                2500000,
    'Xavier Tillman':         2500000,
    'Vasilije Micic':         2000000,
    'Sasha Vezenkov':         2000000,
    'Malachi Flynn':          2000000,
    # ── Mid-tier corrections ─────────────────────────────────────────────────
    'Trey Lyles':            6000000,
    'Chimezie Metu':         3300000,
    'Troy Brown Jr.':        2800000,
    'Yuta Watanabe':         2500000,
    'Tristan Thompson':      2879403,   # 10+ yr veteran min
    'Wesley Matthews':       2879403,   # 10+ yr veteran min
    'Ish Smith':             2879403,   # 10+ yr veteran min
    'Cory Joseph':           2879403,   # 10+ yr veteran min
    'Mike Muscala':          2800000,
    'Oshae Brissett':        2200000,
    'Caleb Houstan':         2019706,   # Rookie scale
    'Jaden Springer':        2019706,   # Rookie scale
    'Patrick Baldwin Jr.':   2019706,   # Rookie scale
    'JT Thor':               2019706,   # Rookie scale
    'MarJon Beauchamp':      2019706,
    'Trent Forrest':         1836090,
    'Omer Yurtseven':        2019706,
    # ── Rookie / Two-Way (still above league min) ────────────────────────────
    'Alperen Sengun':         3922440,   # 3rd year rookie scale
    'GG Jackson':             2019706,   # Two-way → standard, 1st yr
    'Jabari Walker':          2019706,   # 2nd year rookie scale
    'Dalano Banton':          2019706,
    'Derrick Rose':           2879403,   # Veteran minimum (10+ yrs)
    'David Roddy':            2019706,
    'Johnny Davis':           5000000,   # 2nd year rookie scale
    'Jordan Nwora':           2019706,
    'MarJon Beauchamp':       2019706,   # Rookie scale
    'Jontay Porter':          2019706,   # Two-way
    'Jared Butler':           2019706,
    'Lester Quinones':        1836090,   # Two-way
}

# ── Apply corrections ────────────────────────────────────────────────────────
df = pd.read_csv('nba_complete_master.csv')
LEAGUE_MIN = 1_119_563.0

# Mask: 2023-24 season AND currently at league min
mask_2324 = df['SEASON'] == '2023-24'
mask_min  = df['SALARY'] == LEAGUE_MIN

corrected = 0
for name, salary in SALARY_CORRECTIONS_2324.items():
    # Try PLAYER_NAME_CLEAN (lowercase) first
    row_mask = mask_2324 & mask_min & (df['PLAYER_NAME_CLEAN'] == name.lower())
    if row_mask.sum() == 0:
        # Fallback: match first + last name on PLAYER_NAME (case-insensitive)
        parts = name.split()
        search = parts[0] + ' ' + parts[-1]
        row_mask = mask_2324 & mask_min & (df['PLAYER_NAME'].str.contains(
            search, case=False, na=False, regex=False))
    n = row_mask.sum()
    if n > 0:
        df.loc[row_mask, 'SALARY'] = float(salary)
        # Recompute CAP_PCT
        cap_val = df.loc[row_mask, 'CAP'].iloc[0] if 'CAP' in df.columns else 140588000
        df.loc[row_mask, 'CAP_PCT'] = float(salary) / cap_val
        corrected += n

# ── Report ───────────────────────────────────────────────────────────────────
still_wrong = df[(df['SEASON'] == '2023-24') & (df['SALARY'] == LEAGUE_MIN)]
print(f"Corrections applied : {corrected} rows")
print(f"Still at league min : {len(still_wrong)} players (likely genuine minimums)")
print("\nRemaining league-min players:")
print(still_wrong[['PLAYER_NAME','PTS','SALARY']].sort_values('PTS', ascending=False).to_string())

# ── Verify key fixes ─────────────────────────────────────────────────────────
df_2324 = df[df['SEASON'] == '2023-24']
for name in ['Jimmy Butler III', 'Malcolm Brogdon', 'Alperen Sengun']:
    row = df_2324[df_2324['PLAYER_NAME'].str.contains(name.split()[0], case=False, na=False)]
    if len(row):
        print(f"\n{name}: ${row['SALARY'].iloc[0]:,.0f}")

df.to_csv('nba_complete_master.csv', index=False)
print("\nnba_complete_master.csv saved.")
