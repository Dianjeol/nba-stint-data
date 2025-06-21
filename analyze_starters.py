import pandas as pd
import sys

def analyze_quarter_starters(starters_file):
    """
    Analyzes the number of starting players per quarter and prints a summary.

    Args:
        starters_file (str): Path to the quarter_starters.csv file.
    """
    try:
        # 1. Load the starters data
        print("Loading quarter starters data...")
        df = pd.read_csv(starters_file)
        print("Data loaded successfully.")

        # 2. Initialize counters
        ten_starters_count = 0
        more_than_ten_count = 0
        less_than_ten_count = 0

        # 3. Iterate over each quarter and analyze the number of starters
        print("Analyzing starter counts per quarter...")
        for index, row in df.iterrows():
            home_starters_str = row['HOME_STARTERS']
            away_starters_str = row['AWAY_STARTERS']
            
            # Safely count players in each list, handling empty/NaN cases
            num_home = len(home_starters_str.split(', ')) if pd.notna(home_starters_str) and home_starters_str else 0
            num_away = len(away_starters_str.split(', ')) if pd.notna(away_starters_str) and away_starters_str else 0
            
            total_starters = num_home + num_away

            # 4. Update counters based on the total number of starters
            if total_starters == 10:
                ten_starters_count += 1
            elif total_starters > 10:
                more_than_ten_count += 1
            else:
                less_than_ten_count += 1
        
        # 5. Print the final statistics
        total_quarters = len(df)
        print("\n--- Quarter Starter Analysis ---")
        print(f"Total quarters analyzed: {total_quarters}")
        print(f"Quarters with exactly 10 starters: {ten_starters_count}")
        print(f"Quarters with more than 10 starters: {more_than_ten_count}")
        print(f"Quarters with fewer than 10 starters: {less_than_ten_count}")
        print("--------------------------------\n")

    except FileNotFoundError:
        print(f"Error: The file {starters_file} was not found.", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

if __name__ == '__main__':
    STARTERS_CSV = 'quarter_starters.csv'
    analyze_quarter_starters(STARTERS_CSV) 