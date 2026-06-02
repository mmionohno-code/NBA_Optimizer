# TABLEAU SETUP GUIDE — NBA Optimizer Dashboard
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
