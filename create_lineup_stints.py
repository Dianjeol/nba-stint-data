import pandas as pd
import sys

def convert_time_to_seconds(pctimestring):
    """Converts MM:SS string to remaining seconds in a period."""
    if isinstance(pctimestring, str):
        minutes, seconds = map(int, pctimestring.split(':'))
        return minutes * 60 + seconds
    return 0

def create_lineup_stints(stints_file, starters_file, subs_file, active_players_file, output_file):
    """
    Enriches stint data with the full player lineups for each stint.

    Args:
        stints_file (str): Path to the stints.csv file.
        starters_file (str): Path to the quarter_starters.csv file.
        subs_file (str): Path to the substitutions_log.csv file.
        active_players_file (str): Path to the quarter_active_players.csv file.
        output_file (str): Path for the output CSV file.
    """
    try:
        # 1. Load all necessary data
        print("Loading input files...")
        stints_df = pd.read_csv(stints_file)
        starters_df = pd.read_csv(starters_file)
        subs_df = pd.read_csv(subs_file)
        active_players_df = pd.read_csv(active_players_file)
        print("Files loaded successfully.")

        # 2. Prepare lookups for efficient processing
        print("Preparing data lookups...")
        
        # Starters lookup: {(game_id, period): {'home': {p1, p2}, 'away': {pA, pB}}}
        def parse_player_list(s):
            return set(map(int, s.split(', '))) if pd.notna(s) and s else set()
        
        starters_df['HOME_SET'] = starters_df['HOME_STARTERS'].apply(parse_player_list)
        starters_df['AWAY_SET'] = starters_df['AWAY_STARTERS'].apply(parse_player_list)
        starters_lookup = starters_df.set_index(['GAME_ID', 'PERIOD'])[['HOME_SET', 'AWAY_SET']].to_dict('index')

        # Player-team lookup: {(game_id, player_id): 'home'/'away'}
        player_team_lookup = {}
        for _, row in active_players_df.iterrows():
            game_id = row['GAME_ID']
            for player_id in parse_player_list(row['HOME_PLAYERS']):
                player_team_lookup[(game_id, player_id)] = 'home'
            for player_id in parse_player_list(row['AWAY_PLAYERS']):
                player_team_lookup[(game_id, player_id)] = 'away'

        # Substitutions lookup: {(game_id, period, time_seconds): [sub_list]}
        subs_df['SECONDS_REMAINING'] = subs_df['TIME'].apply(convert_time_to_seconds)
        subs_lookup = subs_df.groupby(['GAME_ID', 'PERIOD', 'SECONDS_REMAINING'])[['PLAYER_OUT_ID', 'PLAYER_IN_ID']].apply(lambda x: x.to_dict('records')).to_dict()

        # 3. Process stints game by game
        print("Processing stints to determine lineups...")
        all_lineup_stints = []
        
        # Group stints by game and period to process them chronologically
        for (game_id, period), period_stints in stints_df.groupby(['GAME_ID', 'PERIOD']):
            
            # Get initial lineup for the quarter
            starter_info = starters_lookup.get((game_id, period), {})
            home_lineup = starter_info.get('HOME_SET', set()).copy()
            away_lineup = starter_info.get('AWAY_SET', set()).copy()

            # Sort stints chronologically (descending start time)
            period_stints = period_stints.sort_values(by='STINT_START_SECONDS', ascending=False)
            
            for _, stint in period_stints.iterrows():
                # Add current lineup to the stint record
                stint_data = stint.to_dict()
                stint_data['HOME_LINEUP'] = ', '.join(sorted([str(p) for p in home_lineup]))
                stint_data['AWAY_LINEUP'] = ', '.join(sorted([str(p) for p in away_lineup]))
                all_lineup_stints.append(stint_data)
                
                # Find substitutions at the end of this stint to prepare for the next
                sub_time = stint['STINT_END_SECONDS']
                subs_for_next_stint = subs_lookup.get((game_id, period, sub_time), [])
                
                for sub in subs_for_next_stint:
                    p_out, p_in = sub['PLAYER_OUT_ID'], sub['PLAYER_IN_ID']
                    
                    # Update lineups based on player's team
                    if player_team_lookup.get((game_id, p_out)) == 'home':
                        home_lineup.discard(p_out)
                        home_lineup.add(p_in)
                    elif player_team_lookup.get((game_id, p_out)) == 'away':
                        away_lineup.discard(p_out)
                        away_lineup.add(p_in)
        
        # 4. Create and save the final DataFrame
        print("Saving final lineup stints...")
        final_df = pd.DataFrame(all_lineup_stints)
        
        # Reorder columns for clarity
        cols = ['GAME_ID', 'PERIOD', 'HOME_LINEUP', 'AWAY_LINEUP'] + [c for c in stints_df.columns if c not in ['GAME_ID', 'PERIOD']]
        final_df = final_df[cols]

        final_df.to_csv(output_file, index=False)
        print(f"Successfully created {output_file}")
        print("\nFirst 5 lineup stint entries:")
        print(final_df.head(5).to_string())

    except FileNotFoundError as e:
        print(f"Error: The file {e.filename} was not found.", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

if __name__ == '__main__':
    create_lineup_stints(
        stints_file='stints.csv',
        starters_file='quarter_starters.csv',
        subs_file='substitutions_log.csv',
        active_players_file='quarter_active_players.csv',
        output_file='lineup_stints.csv'
    ) 