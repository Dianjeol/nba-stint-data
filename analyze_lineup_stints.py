import pandas as pd
import sys

def analyze_lineup_stints(lineup_stints_file):
    """
    Analyzes the number of players per stint and prints a summary.

    Args:
        lineup_stints_file (str): Path to the lineup_stints.csv file.
    """
    try:
        # 1. Load the lineup stints data
        print("Loading lineup stints data...")
        df = pd.read_csv(lineup_stints_file)
        print("Data loaded successfully.")

        # 2. Initialize counters
        ten_players_count = 0
        more_than_ten_count = 0
        less_than_ten_count = 0

        # 3. Iterate over each stint and analyze the number of players
        print("Analyzing player counts per stint...")
        for index, row in df.iterrows():
            home_lineup_str = row['HOME_LINEUP']
            away_lineup_str = row['AWAY_LINEUP']
            
            # Safely count players in each list, handling empty/NaN cases
            num_home = len(home_lineup_str.split(', ')) if pd.notna(home_lineup_str) and home_lineup_str else 0
            num_away = len(away_lineup_str.split(', ')) if pd.notna(away_lineup_str) and away_lineup_str else 0
            
            total_players = num_home + num_away

            # 4. Update counters based on the total number of players
            if total_players == 10:
                ten_players_count += 1
            elif total_players > 10:
                more_than_ten_count += 1
            else:
                less_than_ten_count += 1
        
        # 5. Print the final statistics
        total_stints = len(df)
        print("\n--- Lineup Stint Analysis ---")
        print(f"Total stints analyzed: {total_stints}")
        print(f"Stints with exactly 10 players: {ten_players_count}")
        print(f"Stints with more than 10 players: {more_than_ten_count}")
        print(f"Stints with fewer than 10 players: {less_than_ten_count}")
        print("-----------------------------\n")

    except FileNotFoundError:
        print(f"Error: The file {lineup_stints_file} was not found.", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

if __name__ == '__main__':
    LINEUP_STINTS_CSV = 'lineup_stints.csv'
    analyze_lineup_stints(LINEUP_STINTS_CSV) 