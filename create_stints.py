import pandas as pd
import numpy as np
import sys

def convert_time_to_seconds(pctimestring):
    """Converts MM:SS string to remaining seconds in a period."""
    if isinstance(pctimestring, str):
        minutes, seconds = map(int, pctimestring.split(':'))
        return minutes * 60 + seconds
    return 0

def create_stints(input_file, output_file):
    """
    Creates stints from play-by-play data, focusing on time and score changes.
    A stint is a period of time where the on-court players are constant.
    """
    try:
        # 1. Load only necessary columns
        cols = [
            'GAME_ID', 'PERIOD', 'PCTIMESTRING', 'EVENTMSGTYPE', 
            'SCOREMARGIN', 'EVENTNUM'
        ]
        df = pd.read_csv(input_file, usecols=cols, low_memory=True)

        # 2. Prepare the data
        # Convert time to seconds
        df['SECONDS_REMAINING'] = df['PCTIMESTRING'].apply(convert_time_to_seconds)
        
        # Ensure SCOREMARGIN is numeric and handle non-numeric values
        df['SCOREMARGIN'] = pd.to_numeric(df['SCOREMARGIN'], errors='coerce')
        # Forward-fill NaN values in SCOREMARGIN
        df.sort_values(by=['GAME_ID', 'PERIOD', 'EVENTNUM'], inplace=True)
        df['SCOREMARGIN'] = df.groupby(['GAME_ID', 'PERIOD'])['SCOREMARGIN'].ffill().bfill()
        df['SCOREMARGIN'].fillna(0, inplace=True) # Fill any remaining NaNs at start/end of games

        # 3. Identify stint boundaries
        # A new stint starts on a substitution event or when a period changes.
        df['SUBSTITUTION'] = (df['EVENTMSGTYPE'] == 8)
        # Shift the substitution marker to mark the END of a stint
        df['STINT_ENDS'] = df['SUBSTITUTION'].shift(1).fillna(False)

        # A stint also changes between periods
        df['PERIOD_CHANGE'] = (df['PERIOD'] != df['PERIOD'].shift(1))
        df['STINT_BOUNDARY'] = df['STINT_ENDS'] | df['PERIOD_CHANGE']
        
        # Assign a unique ID to each stint
        df['STINT_ID'] = df['STINT_BOUNDARY'].cumsum()

        # 4. Aggregate data by stint
        stints = df.groupby('STINT_ID').agg(
            GAME_ID=('GAME_ID', 'first'),
            PERIOD=('PERIOD', 'first'),
            STINT_START_SECONDS=('SECONDS_REMAINING', 'first'),
            STINT_END_SECONDS=('SECONDS_REMAINING', 'last'),
            START_SCORE_MARGIN=('SCOREMARGIN', 'first'),
            END_SCORE_MARGIN=('SCOREMARGIN', 'last')
        ).reset_index()

        # 5. Calculate duration and plus/minus
        stints['DURATION_SECONDS'] = stints['STINT_START_SECONDS'] - stints['STINT_END_SECONDS']
        stints['PLUS_MINUS'] = stints['END_SCORE_MARGIN'] - stints['START_SCORE_MARGIN']
        
        # Filter out zero-duration stints which can occur at period boundaries
        stints = stints[stints['DURATION_SECONDS'] > 0].copy()
        
        # Add Plus/Minus per minute
        stints['PLUS_MINUS_PER_MINUTE'] = (stints['PLUS_MINUS'] / stints['DURATION_SECONDS']) * 60
        
        # Clean up the final dataframe
        final_stints = stints[['GAME_ID', 'PERIOD', 'DURATION_SECONDS', 'PLUS_MINUS', 'PLUS_MINUS_PER_MINUTE', 'STINT_START_SECONDS', 'STINT_END_SECONDS']]

        final_stints.to_csv(output_file, index=False)

        print(f"Successfully created {len(final_stints)} stints and saved to {output_file}")
        print("\nFirst 10 stints:")
        print(final_stints.head(10).to_string())

    except FileNotFoundError:
        print(f"Error: The file {input_file} was not found.", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

if __name__ == '__main__':
    INPUT_CSV = 'nbastats_2024.csv'
    OUTPUT_CSV = 'stints.csv'
    create_stints(INPUT_CSV, OUTPUT_CSV) 