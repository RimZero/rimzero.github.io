import nba_py
from nba_py import team, game, constants, player
import json
import os
import pandas as pd

TEAMS_FILE = 'teams.csv'
PRIMARY_KEYS = [u'TEAM_ID', u'TEAM_NAME',
                u'PASS_TEAMMATE_PLAYER_ID', u'PLAYER_NAME']
if __name__ == '__main__':
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
            suffixes=['_ON_MADE', '_ON_RECEIVED']).dropna().drop(['TEAM_ID', 'PASS_TEAMMATE_PLAYER_ID'])
        if all is not None:
            all = pd.concat([all, ordered_overall])
        else:
            all = ordered_overall
        print overall
    all.to_csv('passdash/data/passdash.csv', index=False)
