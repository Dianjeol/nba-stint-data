import pandas as pd
import numpy as np
from scipy.sparse import lil_matrix
from sklearn.linear_model import Ridge
import sys

def calculate_rapm(lineup_stints_file, players_file, minutes_file, output_file, regularization_alpha=500, min_minutes=500):
    """
    Calculates player RAPM (Regularized Adjusted Plus-Minus) using Ridge Regression,
    filtered for players who meet a minimum minutes played criteria.

    Args:
        lineup_stints_file (str): Path to the lineup_stints.csv file.
        players_file (str): Path to the players.csv file for name mapping.
        minutes_file (str): Path to the player_minutes.csv file.
        output_file (str): Path for the output CSV file.
        regularization_alpha (int): The regularization strength for the Ridge model.
        min_minutes (int): The minimum total minutes a player must have played.
    """
    try:
        # 1. Load data
        print("Loading data...")
        lineup_stints_df = pd.read_csv(lineup_stints_file).dropna(subset=['HOME_LINEUP', 'AWAY_LINEUP'])
        players_df = pd.read_csv(players_file)
        minutes_df = pd.read_csv(minutes_file)
        print("Data loaded successfully.")

        # 2. Filter players by minutes played
        print(f"Filtering for players with at least {min_minutes} minutes...")
        qualified_players_set = set(minutes_df[minutes_df['TOTAL_MINUTES'] >= min_minutes]['PLAYER_ID'])
        print(f"Found {len(qualified_players_set)} players meeting the minutes criteria.")

        # 3. Prepare data for modeling
        print("Preparing data for RAPM calculation...")
        
        # Get a list of all unique players present in the stints
        all_players_in_stints = set()
        for _, row in lineup_stints_df.iterrows():
            all_players_in_stints.update(map(int, row['HOME_LINEUP'].split(', ')))
            all_players_in_stints.update(map(int, row['AWAY_LINEUP'].split(', ')))
        
        # Intersect all players with those who meet the minutes criteria
        unique_players = sorted(list(all_players_in_stints.intersection(qualified_players_set)))
        player_to_col = {player_id: i for i, player_id in enumerate(unique_players)}
        
        num_stints = len(lineup_stints_df)
        num_players = len(unique_players)

        X = lil_matrix((num_stints, num_players), dtype=np.int8)

        for i, row in lineup_stints_df.iterrows():
            # Home players get +1
            for player_id_str in row['HOME_LINEUP'].split(', '):
                player_id = int(player_id_str)
                if player_id in player_to_col: # Only include qualified players
                    col_idx = player_to_col[player_id]
                    X[i, col_idx] = 1
            # Away players get -1
            for player_id_str in row['AWAY_LINEUP'].split(', '):
                player_id = int(player_id_str)
                if player_id in player_to_col: # Only include qualified players
                    col_idx = player_to_col[player_id]
                    X[i, col_idx] = -1

        y = lineup_stints_df['PLUS_MINUS']
        sample_weights = lineup_stints_df['DURATION_SECONDS']

        # 4. Fit the Ridge Regression model
        print(f"Fitting Ridge Regression model (alpha={regularization_alpha})...")
        X_csr = X.tocsr()
        
        ridge_model = Ridge(alpha=regularization_alpha)
        ridge_model.fit(X_csr, y, sample_weight=sample_weights)
        rapm_values = ridge_model.coef_

        # 5. Create the results DataFrame
        print("Formatting results...")
        results_df = pd.DataFrame({
            'PLAYER_ID': unique_players,
            'RAPM': rapm_values
        })

        # 6. Merge with player names, sort, and save
        final_results_df = pd.merge(results_df, players_df, on='PLAYER_ID')
        final_results_df.sort_values(by='RAPM', ascending=False, inplace=True)
        
        final_results_df = final_results_df[['PLAYER_ID', 'PLAYER_NAME', 'RAPM']]
        final_results_df['RAPM'] = final_results_df['RAPM'].round(4)
        final_results_df.reset_index(drop=True, inplace=True)
        
        print(f"Saving RAPM results to {output_file}...")
        final_results_df.to_csv(output_file, index=False)

        print(f"Successfully calculated RAPM and saved to {output_file}.")
        print("\nTop 20 Players by RAPM (>= 500 minutes):")
        print(final_results_df.head(20).to_string())

    except FileNotFoundError as e:
        print(f"Error: The file {e.filename} was not found.", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

if __name__ == '__main__':
    calculate_rapm(
        lineup_stints_file='lineup_stints.csv',
        players_file='players.csv',
        minutes_file='player_minutes.csv',
        output_file='rapm_results_min500.csv'
    ) 