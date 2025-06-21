import pandas as pd
import numpy as np
import sys

def create_quarter_rosters(stats_file, players_file, output_file):
    """
    Analyzes play-by-play data to find all players with an action in each quarter of each game.
    It lists home and away players in separate columns.

    Args:
        stats_file (str): Path to the play-by-play CSV file (e.g., nbastats_2024.csv).
        players_file (str): Path to the players CSV file.
        output_file (str): Path for the output CSV file.
    """
    try:
        # 1. Load data
        print("Loading data...")
        # Load the set of valid player IDs for filtering
        player_ids = set(pd.read_csv(players_file)['PLAYER_ID'])

        # Load only necessary columns from the main stats file
        cols = [
            'GAME_ID', 'PERIOD', 'HOMEDESCRIPTION', 'VISITORDESCRIPTION',
            'PLAYER1_ID', 'PLAYER1_TEAM_ID',
            'PLAYER2_ID', 'PLAYER2_TEAM_ID',
            'PLAYER3_ID', 'PLAYER3_TEAM_ID'
        ]
        df = pd.read_csv(stats_file, usecols=cols, low_memory=True)
        print("Data loaded successfully.")

        # 2. Identify home team for each game
        print("Identifying home teams...")
        # Find the first event with a home description for each game to identify the home team ID
        home_teams = df.dropna(subset=['HOMEDESCRIPTION'])
        home_team_map = home_teams.groupby('GAME_ID')['PLAYER1_TEAM_ID'].first().to_dict()
        print("Home teams identified.")

        # 3. Process player data
        print("Processing player data...")
        # Melt player columns to create a long format DataFrame
        player_cols = ['PLAYER1_ID', 'PLAYER2_ID', 'PLAYER3_ID']
        team_cols = ['PLAYER1_TEAM_ID', 'PLAYER2_TEAM_ID', 'PLAYER3_TEAM_ID']
        
        # Unpivot player and team IDs
        id_vars = ['GAME_ID', 'PERIOD']
        melted_players = pd.melt(df, id_vars=id_vars, value_vars=player_cols, value_name='PLAYER_ID')
        melted_teams = pd.melt(df, id_vars=id_vars, value_vars=team_cols, value_name='TEAM_ID')
        
        # Combine player and team data
        all_players = pd.concat([
            melted_players[['GAME_ID', 'PERIOD', 'PLAYER_ID']],
            melted_teams[['TEAM_ID']]
        ], axis=1)

        # Drop rows with invalid or missing player IDs
        all_players.dropna(subset=['PLAYER_ID'], inplace=True)
        all_players = all_players[all_players['PLAYER_ID'] != 0]

        # Filter to keep only valid player IDs from players.csv
        all_players = all_players[all_players['PLAYER_ID'].isin(player_ids)]
        
        # Cast to integer for consistency
        all_players['PLAYER_ID'] = all_players['PLAYER_ID'].astype(int)
        
        # 4. Determine player role (Home/Away)
        print("Determining player roles...")
        all_players['HOME_TEAM_ID'] = all_players['GAME_ID'].map(home_team_map)
        all_players['ROLE'] = np.where(all_players['TEAM_ID'] == all_players['HOME_TEAM_ID'], 'Home', 'Away')
        
        # 5. Group by quarter and aggregate players into separate columns
        print("Aggregating results...")
        # Drop duplicates to get unique players per quarter
        unique_players = all_players.drop_duplicates(subset=['GAME_ID', 'PERIOD', 'PLAYER_ID'])

        def aggregate_players(df):
            home_players = sorted(df[df['ROLE'] == 'Home']['PLAYER_ID'].astype(str))
            away_players = sorted(df[df['ROLE'] == 'Away']['PLAYER_ID'].astype(str))
            return pd.Series({
                'HOME_PLAYERS': ', '.join(home_players),
                'AWAY_PLAYERS': ', '.join(away_players)
            })

        final_rosters = unique_players.groupby(['GAME_ID', 'PERIOD']).apply(aggregate_players).reset_index()
        
        # 6. Save to CSV
        print(f"Saving results to {output_file}...")
        final_rosters.to_csv(output_file, index=False)

        print(f"Successfully created quarter rosters for {len(final_rosters)} quarters.")
        print("\nFirst 5 roster entries:")
        print(final_rosters.head(5).to_string())

    except FileNotFoundError as e:
        print(f"Error: The file {e.filename} was not found.", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

if __name__ == '__main__':
    STATS_CSV = 'nbastats_2024.csv'
    PLAYERS_CSV = 'players.csv'
    OUTPUT_CSV = 'quarter_active_players.csv'
    create_quarter_rosters(STATS_CSV, PLAYERS_CSV, OUTPUT_CSV) 