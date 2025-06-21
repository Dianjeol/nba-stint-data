import pandas as pd
import sys

def create_quarter_starters(active_players_file, non_starters_file, output_file):
    """
    Identifies the starting players for each quarter by finding players who were active
    but not substituted in during that quarter.

    Args:
        active_players_file (str): Path to the quarter_active_players.csv file.
        non_starters_file (str): Path to the non_quarter_starters.csv file.
        output_file (str): Path for the output CSV file.
    """
    try:
        # 1. Load the input files
        print("Loading input files...")
        active_players_df = pd.read_csv(active_players_file)
        non_starters_df = pd.read_csv(non_starters_file)
        print("Files loaded successfully.")

        # 2. Prepare the non-starters data for easy lookup
        print("Processing non-starters...")
        # Create a set of non-starters for each game-period for efficient lookup
        non_starters_set = non_starters_df.groupby(['GAME_ID', 'PERIOD'])['PLAYER_ID'].apply(set)
        
        # 3. Determine starters for each quarter
        print("Identifying quarter starters...")
        starter_rows = []
        for index, row in active_players_df.iterrows():
            game_id = row['GAME_ID']
            period = row['PERIOD']
            
            # Get the set of non-starters for the current game and period
            try:
                non_starters_for_quarter = non_starters_set.loc[game_id, period]
            except KeyError:
                non_starters_for_quarter = set()

            # Convert comma-separated player strings to sets of integers
            home_active = set(map(int, str(row['HOME_PLAYERS']).split(', '))) if pd.notna(row['HOME_PLAYERS']) else set()
            away_active = set(map(int, str(row['AWAY_PLAYERS']).split(', '))) if pd.notna(row['AWAY_PLAYERS']) else set()

            # Find the difference: active players minus non-starters are the starters
            home_starters = sorted(list(home_active - non_starters_for_quarter))
            away_starters = sorted(list(away_active - non_starters_for_quarter))
            
            starter_rows.append({
                'GAME_ID': game_id,
                'PERIOD': period,
                'HOME_STARTERS': ', '.join(map(str, home_starters)),
                'AWAY_STARTERS': ', '.join(map(str, away_starters))
            })
            
        starters_df = pd.DataFrame(starter_rows)

        # 4. Save to CSV
        print(f"Saving quarter starters to {output_file}...")
        starters_df.to_csv(output_file, index=False)

        print(f"Successfully created {output_file}")
        print("\nFirst 5 starter entries:")
        print(starters_df.head(5).to_string())

    except FileNotFoundError as e:
        print(f"Error: The file {e.filename} was not found.", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

if __name__ == '__main__':
    ACTIVE_PLAYERS_CSV = 'quarter_active_players.csv'
    NON_STARTERS_CSV = 'non_quarter_starters.csv'
    OUTPUT_CSV = 'quarter_starters.csv'
    create_quarter_starters(ACTIVE_PLAYERS_CSV, NON_STARTERS_CSV, OUTPUT_CSV) 