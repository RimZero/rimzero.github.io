import nba_py
from nba_py import team, game, constants, player
import json
import os
import pandas as pd
import time
import traceback

TEAMS_FILE = 'teams.csv'
METHODS = [('PlayerInGameSplits', ['by_half', 'by_period', 'by_score_margin', 'by_actual_margin'], 'data/player_ingame_splits.csv'),
           ('PlayerOpponentSplits', [
            'by_conference', 'by_division', 'by_opponent'], 'data/player_opponent_splits.csv'),
           ('PlayerGeneralSplits', ['location', 'win_losses', 'month', 'pre_post_all_star', 'starting_position', 'days_rest'], 'data/player_general_splits.csv')]
KEYS = [u'PLAYER_ID', u'NAME', u'TEAM', u'GROUP_SET', u'GROUP_VALUE', u'GP', u'W', u'L', u'W_PCT', u'MIN',
        u'FGM', u'FGA', u'FG_PCT', u'FG3M', u'FG3A', u'FG3_PCT', u'FTM', u'FTA',
        u'FT_PCT', u'OREB', u'DREB', u'REB', u'AST', u'TOV', u'STL', u'BLK',
        u'BLKA', u'PF', u'PFD', u'PTS', u'PLUS_MINUS',
        u'DD2', u'TD3', u'GP_RANK', u'W_RANK', u'L_RANK', u'W_PCT_RANK',
        u'MIN_RANK', u'FGM_RANK', u'FGA_RANK', u'FG_PCT_RANK', u'FG3M_RANK',
        u'FG3A_RANK', u'FG3_PCT_RANK', u'FTM_RANK', u'FTA_RANK', u'FT_PCT_RANK',
        u'OREB_RANK', u'DREB_RANK', u'REB_RANK', u'AST_RANK', u'TOV_RANK',
        u'STL_RANK', u'BLK_RANK', u'BLKA_RANK', u'PF_RANK', u'PFD_RANK',
        u'PTS_RANK', u'PLUS_MINUS_RANK', u'NBA_FANTASY_PTS_RANK', u'DD2_RANK',
        u'TD3_RANK']
PRIMARY_KEYS = [u'TEAM_ID', u'TEAM_NAME',
                u'PASS_TEAMMATE_PLAYER_ID', u'PLAYER_NAME']

if __name__ == '__main__':
    players = player.PlayerList(only_current=0).info()
    players = players[players.TEAM_ABBREVIATION != ""]
    for method, group_names, file_path in METHODS:
        result = pd.DataFrame(columns=KEYS)
        for index, row in players.iterrows():
            while True:
                try:
                    data = getattr(player, method)(
                        player_id=row['PERSON_ID'], per_mode=constants.PerMode.Totals,)
                except Exception as e:
                    traceback.print_exc()
                    time.sleep(5)
                    continue
                break
            player_result = pd.DataFrame(columns=KEYS)
            for group_name in group_names:
                group_data = getattr(data, group_name)()
                group_data['PLAYER_ID'] = row['PERSON_ID']
                group_data['NAME'] = row['DISPLAY_LAST_COMMA_FIRST']
                group_data['TEAM'] = row['TEAM_ABBREVIATION']
                group_data = group_data[KEYS]
                player_result = player_result.append(group_data, )
            result = result.append(player_result)
        result.to_csv(file_path, index=False)


def test():
    if os.path.exists(TEAMS_FILE):
        teams = pd.DataFrame.from_csv(TEAMS_FILE)
    else:
        teams = team.TeamList().info().dropna()
        teams.to_csv(TEAMS_FILE)
    all = None
    for index, row in teams.iterrows():
        data = team.TeamPassTracking(team_id=row['TEAM_ID'])
        passes_made = data.passes_made().drop([u'PASS_TYPE'], 1)
        passes_made.rename(
            columns={'PASS_FROM': 'PLAYER_NAME'}, inplace=True)

        passes_recieved = data.passes_recieved().drop([u'PASS_TYPE'], 1)
        passes_recieved.rename(
            columns={'PASS_TO': 'PLAYER_NAME'}, inplace=True)

        overall = passes_made.merge(
            passes_recieved, left_on=PRIMARY_KEYS,
            right_on=PRIMARY_KEYS, how='outer',
            suffixes=['_ON_MADE', '_ON_RECEIVED']).dropna().drop(['TEAM_ID', 'PASS_TEAMMATE_PLAYER_ID'], 1)
        if all is not None:
            all = pd.concat([all, overall])
        else:
            all = overall
        print overall
    all.to_csv('data/passdash.csv', index=False)
