import pandas as pd
from collections import defaultdict
import sys

def calculate_player_minutes(lineup_stints_file, players_file, output_file):
    """
    Calculates the total minutes played by each player based on stint data
    and saves the result to a CSV file.

    Args:
        lineup_stints_file (str): Path to the lineup_stints.csv file.
        players_file (str): Path to the players.csv file for name mapping.
        output_file (str): Path for the output CSV file.
    """
    try:
        # 1. Load the required data
        print("Loading data...")
        lineup_stints_df = pd.read_csv(lineup_stints_file)
        players_df = pd.read_csv(players_file)
        print("Data loaded successfully.")

        # 2. Calculate total seconds played for each player
        print("Calculating total playing time for each player...")
        player_seconds = defaultdict(float)

        for _, row in lineup_stints_df.iterrows():
            duration = row['DURATION_SECONDS']
            
            # Combine home and away players into a single list
            home_players = row['HOME_LINEUP']
            away_players = row['AWAY_LINEUP']
            
            all_players_str = []
            if pd.notna(home_players) and home_players:
                all_players_str.extend(home_players.split(', '))
            if pd.notna(away_players) and away_players:
                all_players_str.extend(away_players.split(', '))
            
            # Add duration to each player's total
            for player_id_str in all_players_str:
                player_id = int(player_id_str)
                player_seconds[player_id] += duration

        # 3. Convert dictionary to a DataFrame
        minutes_df = pd.DataFrame(player_seconds.items(), columns=['PLAYER_ID', 'TOTAL_SECONDS'])
        minutes_df['TOTAL_MINUTES'] = minutes_df['TOTAL_SECONDS'] / 60

        # 4. Merge with player names
        print("Mapping player IDs to names...")
        final_df = pd.merge(minutes_df, players_df, on='PLAYER_ID')

        # 5. Sort by most minutes played
        final_df.sort_values(by='TOTAL_MINUTES', ascending=False, inplace=True)
        
        # 6. Format and print the final output
        print("\n--- Total Minutes Played per Player ---")
        output_df = final_df[['PLAYER_ID', 'PLAYER_NAME', 'TOTAL_MINUTES']].copy()
        output_df['TOTAL_MINUTES'] = output_df['TOTAL_MINUTES'].round(2)
        
        # Reset index for clean printing and CSV saving
        output_df.reset_index(drop=True, inplace=True)
        
        print(output_df.to_string())
        print("-------------------------------------\n")

        # 7. Save to CSV
        print(f"Saving player minutes to {output_file}...")
        output_df.to_csv(output_file, index=False)
        print(f"Successfully saved to {output_file}.")

    except FileNotFoundError as e:
        print(f"Error: The file {e.filename} was not found.", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

if __name__ == '__main__':
    LINEUP_STINTS_CSV = 'lineup_stints.csv'
    PLAYERS_CSV = 'players.csv'
    OUTPUT_CSV = 'player_minutes.csv'
    calculate_player_minutes(LINEUP_STINTS_CSV, PLAYERS_CSV, OUTPUT_CSV) 