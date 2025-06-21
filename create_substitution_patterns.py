import pandas as pd
import sys

def create_substitution_patterns(log_file, output_file):
    """
    Creates a log of substitution patterns for each player within each quarter.

    Args:
        log_file (str): Path to the substitutions_log.csv file.
        output_file (str): Path for the output CSV file.
    """
    try:
        # 1. Load the substitution log
        print("Loading substitution log...")
        df = pd.read_csv(log_file)
        print("Log loaded successfully.")

        # 2. Unpivot the data to create a single stream of events
        print("Processing substitution events...")
        # Create a DataFrame for players going out
        out_events = df[['GAME_ID', 'PERIOD', 'TIME', 'PLAYER_OUT_ID']].copy()
        out_events.rename(columns={'PLAYER_OUT_ID': 'PLAYER_ID'}, inplace=True)
        out_events['ACTION'] = 'OUT'

        # Create a DataFrame for players coming in
        in_events = df[['GAME_ID', 'PERIOD', 'TIME', 'PLAYER_IN_ID']].copy()
        in_events.rename(columns={'PLAYER_IN_ID': 'PLAYER_ID'}, inplace=True)
        in_events['ACTION'] = 'IN'

        # Combine them into a single DataFrame
        all_events = pd.concat([out_events, in_events])

        # 3. Sort events to ensure correct chronological order
        # The log is already sorted by GAME_ID, PERIOD, and TIME (descending),
        # which represents the correct chronological order.
        # We just need to maintain this order after concatenation.
        all_events.sort_values(by=['GAME_ID', 'PERIOD', 'TIME'], ascending=[True, True, False], inplace=True)

        # 4. Group by player and quarter, then create the pattern string
        print("Aggregating substitution patterns...")
        patterns = all_events.groupby(['GAME_ID', 'PERIOD', 'PLAYER_ID'])['ACTION'].apply(lambda x: ', '.join(x)).reset_index()
        patterns.rename(columns={'ACTION': 'SUBSTITUTION_PATTERN'}, inplace=True)
        
        # 5. Save to CSV
        print(f"Saving substitution patterns to {output_file}...")
        patterns.to_csv(output_file, index=False)

        print(f"Successfully created substitution patterns and saved to {output_file}")
        print("\nFirst 10 substitution patterns:")
        print(patterns.head(10).to_string())

    except FileNotFoundError as e:
        print(f"Error: The file {e.filename} was not found.", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

if __name__ == '__main__':
    LOG_CSV = 'substitutions_log.csv'
    OUTPUT_CSV = 'player_substitution_patterns.csv'
    create_substitution_patterns(LOG_CSV, OUTPUT_CSV) 