# NBA Stint and Lineup Analysis

This project provides a full data pipeline for analyzing NBA play-by-play data. It starts with raw event logs and transforms them through a series of steps to produce advanced metrics, including per-stint player lineups and a Regularized Adjusted Plus-Minus (RAPM) model to evaluate player impact.

The data for this analysis comes from the [nba_data NBA play-by-play dataset](https://github.com/shufinskiy/nba_data).

## Project Structure

### Source Data
- `nbastats_2024.csv`: The raw play-by-play event data for the season.
- `players.csv`: A list of all players with their corresponding IDs.
- `teams.csv`: A list of all teams with their IDs.
- `player_team_assignments.csv`: Maps players to their teams.

### Python Modules
The data pipeline is executed through a series of Python scripts. Each script performs a specific transformation and generates a corresponding CSV file.

1.  `create_stints.py`: Processes raw data to identify and calculate stints (periods of continuous on-court player presence).
2.  `create_quarter_rosters.py`: Determines all players who had an action in each quarter.
3.  `create_substitutions_log.py`: Creates a detailed log of all substitution events.
4.  `create_substitution_patterns.py`: Analyzes the substitution log to create a sequence of actions (e.g., "IN, OUT") for each player per quarter.
5.  `create_non_starters.py`: Identifies players who were substituted into a quarter after it had started.
6.  `create_starters.py`: Determines the starting lineup for each quarter by cross-referencing active players and non-starters.
7.  `create_lineup_stints.py`: The core of the pipeline. It enriches the stint data with the exact home and away lineups on the court for the duration of each stint.
8.  `calculate_player_minutes.py`: Calculates the total minutes played for every player.
9.  `create_rapm.py`: Implements a Regularized Adjusted Plus-Minus (RAPM) model to estimate player impact, filtered for players with over 500 minutes played.

### Analysis Scripts
- `analyze_starters.py`: Provides a summary of how many players start in each quarter.
- `analyze_lineup_stints.py`: Analyzes the final lineup stints to check data integrity (e.g., how many stints have exactly 10 players).

## How to Run

1.  **Set up the environment:**
    It is recommended to use a virtual environment.
    ```bash
    python3 -m venv .venv
    ```

2.  **Install dependencies:**
    Activate the virtual environment and install the required packages.
    ```bash
    source .venv/bin/activate
    pip install pandas scikit-learn
    ```

3.  **Run the pipeline:**
    Execute the Python scripts in the order listed above to generate all data artifacts. For example:
    ```bash
    python create_stints.py
    python create_quarter_rosters.py
    ...
    ``` 