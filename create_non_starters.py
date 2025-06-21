import pandas as pd
import sys

def create_non_starters(patterns_file, output_file):
    """
    Identifies players who were substituted into a quarter (did not start).

    Args:
        patterns_file (str): Path to the player_substitution_patterns.csv file.
        output_file (str): Path for the output CSV file.
    """
    try:
        # 1. Load the substitution patterns
        print("Loading substitution patterns...")
        df = pd.read_csv(patterns_file)
        print("Patterns loaded successfully.")

        # 2. Filter for players whose pattern starts with "IN"
        print("Filtering for non-quarter-starters...")
        # The .str.startswith() method is a direct way to check the beginning of the string
        non_starters = df[df['SUBSTITUTION_PATTERN'].str.startswith('IN')].copy()
        print(f"Found {len(non_starters)} instances of non-quarter-starters.")

        # 3. Save to CSV
        print(f"Saving non-quarter-starters to {output_file}...")
        non_starters.to_csv(output_file, index=False)

        print(f"Successfully created {output_file}")
        print("\nFirst 10 non-starter entries:")
        print(non_starters.head(10).to_string())

    except FileNotFoundError as e:
        print(f"Error: The file {e.filename} was not found.", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

if __name__ == '__main__':
    PATTERNS_CSV = 'player_substitution_patterns.csv'
    OUTPUT_CSV = 'non_quarter_starters.csv'
    create_non_starters(PATTERNS_CSV, OUTPUT_CSV) 