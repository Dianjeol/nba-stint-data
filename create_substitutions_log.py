import pandas as pd
import sys

def create_substitutions_log(stats_file, output_file):
    """
    Logs all player substitutions for each quarter of each game using only IDs.

    Args:
        stats_file (str): Path to the play-by-play CSV file.
        output_file (str): Path for the output CSV log file.
    """
    try:
        # 1. Load data
        print("Loading data...")
        # Load only necessary columns from the stats file
        cols = ['GAME_ID', 'PERIOD', 'PCTIMESTRING', 'EVENTMSGTYPE', 'PLAYER1_ID', 'PLAYER2_ID']
        df = pd.read_csv(stats_file, usecols=cols, low_memory=True)
        print("Data loaded successfully.")

        # 2. Filter for substitution events
        print("Filtering for substitution events...")
        subs = df[df['EVENTMSGTYPE'] == 8].copy()
        
        # Drop rows where players involved are 0 (not real players)
        subs = subs[(subs['PLAYER1_ID'] != 0) & (subs['PLAYER2_ID'] != 0)]
        print(f"Found {len(subs)} substitution events.")

        # 3. Prepare the final log DataFrame
        print("Preparing final log...")
        sub_log = subs[[
            'GAME_ID', 
            'PERIOD', 
            'PCTIMESTRING', 
            'PLAYER1_ID',
            'PLAYER2_ID'
        ]]
        
        sub_log.rename(columns={
            'PCTIMESTRING': 'TIME',
            'PLAYER1_ID': 'PLAYER_OUT_ID',
            'PLAYER2_ID': 'PLAYER_IN_ID'
        }, inplace=True)
        
        # Sort the log for readability
        sub_log.sort_values(by=['GAME_ID', 'PERIOD', 'TIME'], ascending=[True, True, False], inplace=True)

        # 4. Save to CSV
        print(f"Saving substitution log to {output_file}...")
        sub_log.to_csv(output_file, index=False)

        print(f"Successfully created substitution log and saved to {output_file}")
        print("\nFirst 10 substitution events:")
        print(sub_log.head(10).to_string())

    except FileNotFoundError as e:
        print(f"Error: The file {e.filename} was not found.", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

if __name__ == '__main__':
    STATS_CSV = 'nbastats_2024.csv'
    OUTPUT_CSV = 'substitutions_log.csv'
    create_substitutions_log(STATS_CSV, OUTPUT_CSV) 